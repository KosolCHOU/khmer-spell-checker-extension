"""
Khmer Text Segmentation Module
Extracted from spell_checker_advanced.py for easier debugging and maintenance.
Handles text normalization and word segmentation using Viterbi algorithm.
"""

import re
import math
import difflib
from typing import List, Dict, Set
from functools import lru_cache

# Import dependencies from spell checker
try:
    from .spell_checker_constants import COMMON_TYPOS, WHITELIST_WORDS, STOPWORDS
except ImportError:
    from spell_checker_constants import COMMON_TYPOS, WHITELIST_WORDS, STOPWORDS


# ============================================================================
# Character Type Checking
# ============================================================================

def is_kh_consonant(text: str) -> bool:
    """Check if text is a single Khmer consonant"""
    if len(text) != 1:
        return False
    cp = ord(text)
    # 0x1780 (KA) to 0x17A2 (QA)
    return 0x1780 <= cp <= 0x17A2


def is_kh_letter_seq(text: str) -> bool:
    """Check if text contains only Khmer letters (no punctuation/digits)"""
    for char in text:
        cp = ord(char)
        # Basic Khmer block check (roughly): 1780-17FF
        # Exclude digits 17E0-17E9
        # Exclude symbols 17D4-17D9 (punctuations)
        if not (0x1780 <= cp <= 0x17FF):
            return False
        if 0x17E0 <= cp <= 0x17E9:  # Digits
            return False
        if 0x17D4 <= cp <= 0x17D9:  # Punctuation
            return False
    return True


# ============================================================================
# Text Normalization
# ============================================================================

def normalize_text(text: str) -> str:
    """Normalize Khmer text to handle encoding and punctuation."""
    text = text.replace("\u17c1\u17b8", "\u17be")
    puncts = r'[!?:;"«»(){}\\[\\]%,។៖ៗ\\-]'
    text = re.sub(f'({puncts})', r' \1 ', text)
    text = re.sub(r'\s+', ' ', text)
    # Don't strip - preserve leading/trailing whitespace for accurate offset calculation
    return text


# ============================================================================
# Viterbi Segmentation
# ============================================================================

def get_char_type_cost(text: str) -> float:
    """Cost for skipping a character (treating as unknown)"""
    if not text:
        return 0.0
    
    # Check if it's a Khmer letter
    ch = text[0]
    is_khmer = ("\u1780" <= ch <= "\u17FF" or "\u19E0" <= ch <= "\u19FF")
    
    if not is_khmer:
        return 0.0  # Free to skip/segment non-Khmer (punctuation, space)
        
    return 3.0  # Reduced from 15.0 to prevent "over-splitting" of valid words next to typos


def viterbi_segment(text: str, word_set: Set[str], word_freq: Dict[str, float]) -> List[str]:
    """
    Segment text using Viterbi algorithm (probabilistic).
    Minimizes: Sum(-log(P(word)))
    """
    n = len(text)
    if n == 0:
        return []
    
    # dp[i] = (min_cost, length_of_last_word)
    dp = [(float('inf'), 0)] * (n + 1)
    dp[0] = (0.0, 0)
    
    MAX_WORD_LEN = 25  # Optimization
    
    for i in range(n):
        if dp[i][0] == float('inf'):
            continue
            
        current_cost = dp[i][0]
        
        # 1. Option: Treat current char as Unknown/Junk
        char_cost = get_char_type_cost(text[i])
        if (current_cost + char_cost) < dp[i+1][0]:
            dp[i+1] = (current_cost + char_cost, 1)
            
        # 2. Option: Match Dictionary Word
        # Optimization: Skip if current char is not Khmer (cannot start a dictionary word)
        if not (0x1780 <= ord(text[i]) <= 0x17FF):
            continue
            
        # Optimization: Early exit if first char not in any word start
        # (Assuming we had a prefix tree, currently we check word_set blindly)
        
        end_cap = min(i + MAX_WORD_LEN, n)
        for j in range(i + 1, end_cap + 1):
            cand = text[i:j]
            
            # Optimization: Skip single consonants as words to prefer compounds/merging
            if len(cand) == 1 and is_kh_consonant(cand) and cand != "ក៏":
                continue

            if cand in word_set:
                # Calculate cost
                # Cost = 6 - log10(IPM). Min IPM=0.01 -> Cost ~ 8. Max IPM=1M -> Cost=0.
                ipm = word_freq.get(cand, 0.01)
                if ipm <= 0:
                    ipm = 0.01
                word_cost = 6.0 - math.log10(ipm)
                
                # Penalize single consonants/vowels to prefer longer compounds
                if len(cand) == 1:
                    word_cost += 5.0
                
                if (current_cost + word_cost) < dp[j][0]:
                    dp[j] = (current_cost + word_cost, len(cand))
                    
    # Backtrack
    tokens = []
    i = n
    while i > 0:
        length = dp[i][1]
        # Safety fallback
        if length == 0:
            # Should not happen if DP filled correctly, but if stuck, take 1 char
            length = 1
             
        tokens.append(text[i-length:i])
        i -= length
        
    tokens.reverse()
    return tokens


# ============================================================================
# Token Merging Helpers
# ============================================================================

def is_kh_letter_seq_strict(s: str) -> bool:
    """
    Strict check for Khmer letters (Consonants, Vowels, Diacritics)
    Excludes punctuation (17D4+) and digits (17E0+)
    """
    for ch in s:
        cp = ord(ch)
        # Range 0x1780 (KA) to 0x17D3 (BANTOC) covers standard letters & marks
        if not (0x1780 <= cp <= 0x17D3):
            return False
    return True


def is_dependent_start(s: str) -> bool:
    """Check if first char is a dependent vowel or sign (cannot start a word)"""
    if not s:
        return False
    # Check if first char is a dependent vowel or sign (cannot start a word)
    # 17B4 (Vowel Inherent AQ) to 17D3 (Bantoc/Coeng/etc)
    cp = ord(s[0])
    return 0x17B4 <= cp <= 0x17D3


# ============================================================================
# Main Segmentation Function
# ============================================================================

def segment_text(text: str, word_set: Set[str], word_freq: Dict[str, float], 
                 words_by_start: Dict[str, List[str]], is_known_func) -> List[str]:
    """
    Segment Khmer text into tokens.
    
    Strategy:
      1) Normalize and split on whitespace/punctuation if present.
      2) Apply Viterbi algorithm for probabilistic segmentation.
      3) Post-pass: merge adjacent unknown tokens if their concatenation closely
         matches a known dictionary word (to catch cases like 'លោ'+'លក' -> 'លោក').
    
    Args:
        text: Input text to segment
        word_set: Set of valid words
        word_freq: Dictionary of word frequencies (IPM)
        words_by_start: Dictionary mapping first character to list of words
        is_known_func: Function to check if a token is known
        
    Returns:
        List of segmented tokens
    """
    if not text:
        return []

    # Normalize text first (fixes impossible sequences and adds spaces to punctuation)
    text = normalize_text(text)

    # Use Viterbi Segmentation for best probabilistic split
    tokens = viterbi_segment(text, word_set, word_freq)

    # print(f"DEBUG: segment_text raw tokens: {tokens}")
    
    # Post-pass: merge adjacent unknown tokens
    # Goal: Group sequences of unknown Khmer characters/stubs into a single "Unknown Word" token.
    # This prevents an unknown word like "ច្រេន" from being split into ['ច', '្', 'រេន'] and reported as 3 errors.
    
    final_tokens: List[str] = []
    
    for t in tokens:
        if not final_tokens:
            final_tokens.append(t)
            continue
            
        prev = final_tokens[-1]
        
        # Merge decisions:
        # 1. Both must be Khmer letter sequences (no punctuation).
        if is_kh_letter_seq_strict(prev) and is_kh_letter_seq_strict(t):
            should_merge = False
            
            # Case A: Both Unknown (and not known specific typos)
            if (not is_known_func(prev)) and (not is_known_func(t)):
                # If either is a specifically known typo, don't merge them into a single blob
                # unless they form a larger known typo (checked in second pass)
                if prev not in COMMON_TYPOS and t not in COMMON_TYPOS:
                    should_merge = True
                    # print(f"DEBUG: Merging Unknowns: {prev} + {t}")
            
            # Case B: Current token starts with a dependent mark (must attach to prev)
            elif is_dependent_start(t):
                should_merge = True
                # print(f"DEBUG: Dependent Merge: {prev} + {t}")
                
            # Case C: Previous token ends with Coeng (17D2) (must accept next consonant)
            elif prev.endswith('\u17d2'):
                should_merge = True
                # print(f"DEBUG: Coeng Merge: {prev} + {t}")
                
            if should_merge:
                final_tokens[-1] = prev + t
                continue

        final_tokens.append(t)

    # Merge adjacent tokens if their concatenation matches a dictionary word (fuzzy or exact)
    # This handles "split typos" like ['ស', 'ប្តា', 'ហ៏'] -> 'សប្តាហ៏' (typo of 'សប្តាហ៍')
    
    merged_tokens = []
    i = 0
    n_tokens = len(final_tokens)
    
    while i < n_tokens:
        merged = False
        # Try window sizes 4 down to 2
        for k in range(4, 1, -1):
            if i + k > n_tokens:
                continue
            
            chunk = final_tokens[i : i+k]
            
            concat = "".join(chunk)
            if not concat:
                continue
            
            # Force merge if explicitly listed in common typos
            if concat in COMMON_TYPOS:
                merged_tokens.append(concat)
                i += k
                merged = True
                break
            
            # Protect specific common typos from being merged into larger garbage
            # e.g. "To" + "Aeng" -> "Aeng" is a known typo, so keep it separate.
            if any(t in COMMON_TYPOS for t in chunk):
                continue
                
            # Heuristic: Only attempt merge if the chunk looks "fragmented"
            # Conditions:
            # 1. Contains at least one UNKNOWN token
            # We avoid merging if ALL tokens are already known words (e.g. "Go" + "To")
            has_unknown = any(not is_known_func(t) for t in chunk)
            
            if not has_unknown:
                continue

            # Avoid merging punctuation or spaces
            # If any token is purely non-Khmer letters (like space or punct), skip
            # Note: We rely on is_kh_letter_seq to ensure we only merge letter fragments
            if any(not is_kh_letter_seq_strict(t) and t.strip() != "" for t in chunk):
                continue
            
            # Optimization: Check if first char exists in dictionary
            candidates = words_by_start.get(concat[0], [])
            if not candidates:
                continue
                
            # Check for fuzzy match
            # We use a relatively high cutoff because we expect the intended word to be very similar
            # Lowered to 0.75 to capture typos with multiple diffs (e.g. Ta/Da var + wrong sign)
            # Increased back to 0.85 to prevent merging known words with typos (e.g. "To" + "Aeng")
            matches = difflib.get_close_matches(concat, candidates, n=1, cutoff=0.85)
            
            if matches:
                # Found a potential word that this chunk is a typo of
                match = matches[0]
                
                # Check if we are merging across a space?
                has_space = any(t.strip() == "" for t in chunk)
                if has_space:
                    # If merging across space, be stricter.
                    # Only merge if exact match or very high similarity
                    pass
                # Safety: Do not merge if the match is identical to one of the existing tokens
                # UNLESS the other tokens are unknown/junk (which implies we are correcting by removing junk)
                if match in chunk:
                    # If any other token is whitespace, DO NOT merge (avoids eating spaces after valid words)
                    if any(t.strip() == "" for t in chunk if t != match):
                        continue
                        
                    others_known = all(is_known_func(t) for t in chunk if t != match)
                    if others_known:
                        continue

                # Check length similarity to avoid "go" + "to" merging into "photo"
                # AND check for Stopwords eating.
                # If match contains a stopword as a substring that was originally a separate token, we should be careful.
                # e.g. "Typo" + "Stop" -> "TypoStop" (matches "LongWord").
                # If the original tokens included a Stopword, we should verify that the merged result is NOT just "Typo" + "Stop" glommed together incorrectly.
                # Actually, simply: If one of the chunks is a STOPWORD, allow merge ONLY if the result is an Exact Dictionary Match (not just fuzzy).
                
                has_stopword = any(t in STOPWORDS for t in chunk)
                is_fuzzy = match != concat
                
                if has_stopword and is_fuzzy:
                    # Reject fuzzy merge that consumes a stopword
                    continue

                # NEW: Block merging if one of the tokens is a long KNOWN valid word (>2 chars)
                # Unless the resulting concat is EXPLICITLY in COMMON_TYPOS
                has_long_known = False
                for t in chunk:
                    if len(t) > 2 and is_known_func(t):
                        has_long_known = True
                        break
                
                if has_long_known and concat not in COMMON_TYPOS:
                    # Allow if at least one token is unknown (likely a typo fragment)
                    if all(is_known_func(t) for t in chunk):
                        continue

                if abs(len(match) - len(concat)) <= 2:
                    merged_tokens.append(concat)  # Use concat (original text) for spell checker to correct later
                    i += k
                    merged = True
                    break
        
        if not merged:
            merged_tokens.append(final_tokens[i])
            i += 1

    # Post-pass: Merge adjacent number/digit tokens
    # Example: ['៥', '០'] -> ['៥០']
    nu_merged: List[str] = []
    i = 0
    while i < len(merged_tokens):
        t = merged_tokens[i]
        if re.match(r'^[0-9០-៩]+$', t):
            # Try to grab subsequent digits
            combined = t
            j = i + 1
            while j < len(merged_tokens) and re.match(r'^[0-9០-៩]+$', merged_tokens[j]):
                combined += merged_tokens[j]
                j += 1
            nu_merged.append(combined)
            i = j
        else:
            nu_merged.append(t)
            i += 1

    return [m for m in nu_merged if m]


# ============================================================================
# Debugging Utilities
# ============================================================================

def debug_segment(text: str, word_set: Set[str], word_freq: Dict[str, float], 
                  words_by_start: Dict[str, List[str]], is_known_func) -> Dict:
    """
    Debug version of segment_text that returns detailed information about the segmentation process.
    
    Returns:
        Dictionary containing:
        - normalized: Normalized text
        - viterbi_tokens: Raw tokens from Viterbi
        - merged_tokens: Tokens after merging unknown sequences
        - final_tokens: Final tokens after all merging passes
        - stats: Statistics about the segmentation
    """
    if not text:
        return {
            'normalized': '',
            'viterbi_tokens': [],
            'merged_tokens': [],
            'final_tokens': [],
            'stats': {}
        }
    
    # Normalize
    normalized = normalize_text(text)
    
    # Viterbi
    viterbi_tokens = viterbi_segment(normalized, word_set, word_freq)
    
    # First merge pass (unknown tokens)
    merged_unknown = []
    for t in viterbi_tokens:
        if not merged_unknown:
            merged_unknown.append(t)
            continue
            
        prev = merged_unknown[-1]
        
        if is_kh_letter_seq_strict(prev) and is_kh_letter_seq_strict(t):
            should_merge = False
            
            if (not is_known_func(prev)) and (not is_known_func(t)):
                if prev not in COMMON_TYPOS and t not in COMMON_TYPOS:
                    should_merge = True
            elif is_dependent_start(t):
                should_merge = True
            elif prev.endswith('\u17d2'):
                should_merge = True
                
            if should_merge:
                merged_unknown[-1] = prev + t
                continue

        merged_unknown.append(t)
    
    # Final segmentation
    final_tokens = segment_text(text, word_set, word_freq, words_by_start, is_known_func)
    
    # Statistics
    stats = {
        'original_length': len(text),
        'normalized_length': len(normalized),
        'viterbi_token_count': len(viterbi_tokens),
        'merged_unknown_count': len(merged_unknown),
        'final_token_count': len(final_tokens),
        'unknown_tokens': [t for t in final_tokens if not is_known_func(t)]
    }
    
    return {
        'normalized': normalized,
        'viterbi_tokens': viterbi_tokens,
        'merged_tokens': merged_unknown,
        'final_tokens': final_tokens,
        'stats': stats
    }


if __name__ == "__main__":
    # Simple test
    print("Khmer Segmenter Module")
    print("This module should be imported, not run directly.")
    print("Use debug_segment() for detailed segmentation analysis.")
