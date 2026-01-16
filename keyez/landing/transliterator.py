"""
SingKhmer to Khmer transliteration using Seq2Seq model (NumPy Implementation)
Optimized for inference latency via vectorized beam search.
"""
import numpy as np
from pathlib import Path
from typing import List, Tuple

# Special tokens (must match training)
PAD_IDX, SOS_IDX, EOS_IDX, UNK_IDX = 0, 1, 2, 3

def sigmoid(x):
    # Using clip to avoid overflow
    x = np.clip(x, -500, 500)
    return 1 / (1 + np.exp(-1.0 * x))

def tanh(x):
    return np.tanh(x)

def log_softmax(x, axis=-1):
    """Compute log-softmax in a numerically stable way (supports batch)."""
    x_max = np.max(x, axis=axis, keepdims=True)
    return x - x_max - np.log(np.sum(np.exp(x - x_max), axis=axis, keepdims=True))

class NumpyGRU:
    def __init__(self, weights_ih, weights_hh, bias_ih, bias_hh):
        self.w_ih = weights_ih
        self.w_hh = weights_hh
        self.b_ih = bias_ih
        self.b_hh = bias_hh
        self.hidden_size = weights_hh.shape[1]

    def step(self, x, h):
        """
        Step with support for both single (1D) and batched (2D) inputs.
        x: (input_dim,) or (batch, input_dim)
        h: (hidden_dim,) or (batch, hidden_dim)
        """
        if x.ndim == 1:
            # Original 1D logic
            gi = self.w_ih @ x + self.b_ih
            gh = self.w_hh @ h + self.b_hh
            
            i_r, i_z, i_n = np.split(gi, 3)
            h_r, h_z, h_n = np.split(gh, 3)
            
            r = sigmoid(i_r + h_r)
            z = sigmoid(i_z + h_z)
            n = tanh(i_n + r * h_n)
            h_next = (1 - z) * n + z * h
            return h_next
        else:
            # Batched logic (2D)
            # x: (B, I), self.w_ih: (3H, I). We need x @ W.T
            gi = x @ self.w_ih.T + self.b_ih
            gh = h @ self.w_hh.T + self.b_hh
            
            # Split along last axis (H dimension)
            i_r, i_z, i_n = np.split(gi, 3, axis=-1)
            h_r, h_z, h_n = np.split(gh, 3, axis=-1)
            
            r = sigmoid(i_r + h_r)
            z = sigmoid(i_z + h_z)
            n = tanh(i_n + r * h_n)
            h_next = (1 - z) * n + z * h
            return h_next

    def __call__(self, x_seq, h_initial=None):
        # x_seq: (seq_len, emb_dim)
        # Encoder is typically run once on single sequence, so 1D is fine here
        seq_len = x_seq.shape[0]
        if h_initial is None:
            # Only supports 1D h_initial for now (encoder use case)
            h = np.zeros(self.hidden_size)
        else:
            h = h_initial
        
        for t in range(seq_len):
            h = self.step(x_seq[t], h)
        return h

class SingKhmerTransliterator:
    """Handles SingKhmer to Khmer transliteration using NumPy only"""
    
    def __init__(self, weights_path: Path):
        data = np.load(weights_path, allow_pickle=True)
        self.metadata = data['metadata'].item()
        
        # Encoder weights
        self.enc_emb = data['encoder.embedding.weight']
        self.enc_gru = NumpyGRU(
            data['encoder.rnn.weight_ih_l0'],
            data['encoder.rnn.weight_hh_l0'],
            data['encoder.rnn.bias_ih_l0'],
            data['encoder.rnn.bias_hh_l0']
        )
        
        # Decoder weights
        self.dec_emb = data['decoder.embedding.weight']
        self.dec_gru = NumpyGRU(
            data['decoder.rnn.weight_ih_l0'],
            data['decoder.rnn.weight_hh_l0'],
            data['decoder.rnn.bias_ih_l0'],
            data['decoder.rnn.bias_hh_l0']
        )
        self.dec_fc = data['decoder.fc_out.weight'] # Shape: (Vocab, Hidden)
        self.dec_fc_bias = data['decoder.fc_out.bias']
        
        # Vocabs
        self.src_stoi = self.metadata['src_stoi']
        self.src_itos = self.metadata['src_itos']
        self.tgt_stoi = self.metadata['tgt_stoi']
        self.tgt_itos = self.metadata['tgt_itos']
        
        self.SOS_token = SOS_IDX
        self.EOS_token = EOS_IDX
        self.UNK_token = UNK_IDX
        self.PAD_token = PAD_IDX

    def _decode_indices(self, indices: List[int]) -> str:
        res = []
        for idx in indices:
            if idx in [self.SOS_token, self.EOS_token, self.PAD_token]:
                continue
            res.append(self.tgt_itos[idx])
        return "".join(res)

    def translate(self, singkhmer: str, top_k: int = 3) -> List[str]:
        """
        Translate SingKhmer to Khmer using vectorized beam search.
        """
        if not singkhmer:
            return [""] * top_k
            
        # 1. ENCODE
        # Tokenize input
        src_indices = [self.SOS_token]
        for char in singkhmer.lower():
            src_indices.append(self.src_stoi.get(char, self.UNK_token))
        src_indices.append(self.EOS_token)
        
        # Run Encoder (Single sequence)
        src_emb = self.enc_emb[src_indices]
        encoder_hidden = self.enc_gru(src_emb) # (H,)
        
        # 2. DECODE (Beam Search)
        # Prepare Beam state
        beam_width = top_k
        max_len = 50
        
        # Replicate hidden state: (Beam, H)
        hidden = np.tile(encoder_hidden, (beam_width, 1))
        
        # Start tokens: (Beam,)
        current_tokens = np.full(beam_width, self.SOS_token, dtype=int)
        
        # Cumulative scores: (Beam,)
        # Force beam 0 to be the only starter (score 0), others -inf
        scores = np.full(beam_width, -1e9)
        scores[0] = 0.0
        
        # Paths: List of lists matches best with variable lengths
        # Initialize with SOS
        paths = [[self.SOS_token] for _ in range(beam_width)]
        
        # Finished beams cache
        completed = []
        
        # To avoid infinite loops for finished beams in vectorized ops
        active_mask = np.ones(beam_width, dtype=bool) 
        
        for step in range(max_len):
            # If all inactive/finished, break
            if not np.any(active_mask):
                break
                
            # Embeddings: (Beam, Emb)
            embs = self.dec_emb[current_tokens]
            
            # GRU Step: (Beam, H)
            hidden = self.dec_gru.step(embs, hidden)
            
            # Logits: (Beam, Vocab)
            # fc is (V, H), need (B, H) @ (H, V) -> (B, V) + bias
            logits = hidden @ self.dec_fc.T + self.dec_fc_bias
            
            # Log Softmax
            log_probs = log_softmax(logits, axis=1) # (B, V)
            
            # Add previous scores
            # scores: (B,) -> broadcast to (B, V)
            total_scores = log_probs + scores[:, None]
            
            # Force finished beams to not expand (set scores to -inf)
            # (If a beam was already EOS, we shouldn't have been processing it, 
            # but vectorized ops process everything. We'll filter later)
            
            # Flatten to find top global candidates
            flat_scores = total_scores.flatten() 
            
            # Get Top-K indices across all (Beam * Vocab)
            # argpartition to find best K
            top_k_indices = np.argpartition(flat_scores, -beam_width)[-beam_width:]
            
            # Filter and sort
            best_candidates = []
            for idx in top_k_indices:
                score = flat_scores[idx]
                beam_idx = int(idx // self.dec_fc.shape[0])
                vocab_idx = int(idx % self.dec_fc.shape[0])
                best_candidates.append((score, beam_idx, vocab_idx))
            
            best_candidates.sort(key=lambda x: x[0], reverse=True)
            best_candidates = best_candidates[:beam_width]
            
            # Build next state
            next_tokens = []
            next_scores = []
            next_hidden = []
            next_paths = []
            next_active = []
            
            for score, beam_idx, vocab_idx in best_candidates:
                prev_path = paths[beam_idx]
                
                # If parent was already EOS, don't extend (shouldn't happen with proper masking logic, 
                # but simple check: if we picked an extension of a finished beam, ignore/penalize?
                # Actually, simpler: check if new token is EOS
                
                new_path = prev_path + [vocab_idx]
                
                if vocab_idx == self.EOS_token:
                    completed.append((new_path, score))
                    # This beam slot is effectively dead now, but we need to fill the slot for the matrix ops
                    # We'll fill with dummy values and set score to -inf in next iter
                    next_tokens.append(self.EOS_token) # Dummy
                    next_scores.append(-1e9) # Dead
                    next_hidden.append(hidden[beam_idx]) # Dummy
                    next_paths.append(new_path)
                    next_active.append(False)
                else:
                    next_tokens.append(vocab_idx)
                    next_scores.append(score)
                    next_hidden.append(hidden[beam_idx])
                    next_paths.append(new_path)
                    next_active.append(True)
            
            # Update state
            current_tokens = np.array(next_tokens)
            scores = np.array(next_scores)
            hidden = np.array(next_hidden)
            paths = next_paths
            active_mask = np.array(next_active)
            
            # Stop if we have enough completed
            if len(completed) >= top_k * 2: # heuristic margin
                break
                
        # Add any remaining active beams to completed
        for i, is_active in enumerate(active_mask):
            if is_active:
                completed.append((paths[i], scores[i]))
                
        # Sort by score
        completed.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        seen = set()
        for indices, _ in completed:
            text = self._decode_indices(indices)
            if text and text not in seen:
                results.append(text)
                seen.add(text)
                if len(results) >= top_k:
                    break
                    
        # Fallback
        while len(results) < top_k:
            results.append("")
            
        return results

# Global transliterator instance
_transliterator = None

def get_transliterator() -> SingKhmerTransliterator:
    """Get or create the global transliterator instance"""
    global _transliterator
    if _transliterator is None:
        model_dir = Path(__file__).resolve().parent / "model"
        weights_path = model_dir / "singkhmer_seq2seq_weights.npz"
        if not weights_path.exists():
             print(f"CRITICAL ERROR: Transliteration model weights not found at {weights_path}")
             raise FileNotFoundError(f"Model weights not found at {weights_path}")
        _transliterator = SingKhmerTransliterator(weights_path)
    return _transliterator
