"""
Advanced Khmer Spell Checker - Integrated from Streamlit App
Uses multiple data sources and NLP models for accurate detection and suggestions.
"""

import re
import sys
import math
import difflib
from pathlib import Path
from typing import List, Dict, Set, Tuple
import json

import pickle
from functools import lru_cache

# Import custom spell checker constants
try:
    from .spell_checker_constants import (
        POS_MAP, COMMON_NAMES, PRONOUNS, HONORIFICS, TECHNICAL_TERMS,
        BANNED_WORDS, SAFE_PREFIXES, STOPWORDS, WHITELIST_WORDS,
        WHITE_LIST_EXT, COMMON_TYPOS, MANUAL_TAGS, MANUAL_BIGRAMS,
        SUSPICIOUS_BIGRAMS, TRANSITIVE_VERBS_NOV, KHMER_NUM_WORDS,
        CLASSIFIERS, noun_classifier_map, LOC_TIME_WORDS,
        INTRANSITIVE_VERBS, AUXILIARIES, MOTION_VERBS, PATCH_WORDS,
        FREQ_BOOSTS, REGISTER_MAP, ROYAL_SUBJECTS, COMMON_SUBJECTS,
        CONTEXTUAL_PAIRS, SEMANTIC_REGISTER_MAP
    )
    from .khmer_segmenter import (
        normalize_text, segment_text, is_kh_consonant, is_kh_letter_seq,
        viterbi_segment, debug_segment
    )
except ImportError:
    # Fallback for direct execution
    from spell_checker_constants import (
        POS_MAP, COMMON_NAMES, PRONOUNS, HONORIFICS, TECHNICAL_TERMS,
        BANNED_WORDS, SAFE_PREFIXES, STOPWORDS, WHITELIST_WORDS,
        WHITE_LIST_EXT, COMMON_TYPOS, MANUAL_TAGS, MANUAL_BIGRAMS,
        SUSPICIOUS_BIGRAMS, TRANSITIVE_VERBS_NOV, KHMER_NUM_WORDS,
        CLASSIFIERS, noun_classifier_map, LOC_TIME_WORDS,
        INTRANSITIVE_VERBS, AUXILIARIES, MOTION_VERBS, PATCH_WORDS,
        FREQ_BOOSTS, REGISTER_MAP, ROYAL_SUBJECTS, COMMON_SUBJECTS,
        CONTEXTUAL_PAIRS, SEMANTIC_REGISTER_MAP
    )
    from khmer_segmenter import (
        normalize_text, segment_text, is_kh_consonant, is_kh_letter_seq,
        viterbi_segment, debug_segment
    )

# Paths setup
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
BUNDLE_PATH = DATA_DIR / "spell_checker_bundle.pkl"



# Data loaders
class SpellCheckerData:
    """Lazy-loaded data for spell checking"""
    
    _dictionary = None
    _frequency = None
    _names = None
    _bigrams = None
    _trigrams = None
    _bigram_context_fwd = None
    _bigram_context_bwd = None
    _semantic_map = None
    _word_set = None
    _word_list = None
    _word_to_pos = None
    _word_freq_ipm = None
    _max_ipm = None
    _words_by_start = None
    
    @classmethod
    def build_tables(cls) -> Tuple[Set[str], Dict[str, Set[str]], Dict[str, float], float]:
        if cls._word_set is None:
            if not BUNDLE_PATH.exists():
                raise FileNotFoundError(f"Spell checker bundle not found at {BUNDLE_PATH}")
            
            with open(BUNDLE_PATH, "rb") as f:
                bundle = pickle.load(f)
                
            cls._word_set = bundle['word_set']
            cls._word_to_pos = bundle['word_to_pos']
            cls._word_freq_ipm = bundle['word_freq_ipm']
            cls._max_ipm = bundle['max_ipm']
            cls._bigrams = bundle['bigrams']
            cls._bigram_context_fwd = bundle['bigram_context_fwd']
            cls._bigram_context_bwd = bundle['bigram_context_bwd']
            
            # Manual patches and common typos cleanup (already in bundle, but safe to repeat)
            cls._word_set.update(COMMON_NAMES)
            cls._word_set.update(PRONOUNS)
            cls._word_set.update(HONORIFICS)
            cls._word_set.update(TECHNICAL_TERMS)
            cls._word_set.update(WHITELIST_WORDS)

            
            # Remove known garbage words
            cls._word_set.discard("ដលោក")
            
            for bad_word in COMMON_TYPOS:
                # Only discard if it's NOT in the whitelist
                if bad_word in cls._word_set and bad_word not in WHITELIST_WORDS:
                    cls._word_set.discard(bad_word)
            
            # Ensure valid words are in the word set
            cls._word_set.update(PATCH_WORDS)

            # Boost frequency for compound words to prevent splitting
            for word, boost in FREQ_BOOSTS.items():
                cls._word_freq_ipm[word] = boost




            # Logic to treat Coeng Da (\u17d2\u178a) and Coeng Ta (\u17d2\u178f) as interchangeable
            # Generate variants for all words so both forms are considered valid
            variants = set()
            COENG_DA = "\u17d2\u178a"
            COENG_TA = "\u17d2\u178f"
            for w in cls._word_set:
                if COENG_DA in w:
                    variants.add(w.replace(COENG_DA, COENG_TA))
                if COENG_TA in w:
                    variants.add(w.replace(COENG_TA, COENG_DA))
            cls._word_set.update(variants)
            
            # Profanity filter: remove banned words
            cls._word_set.difference_update(BANNED_WORDS)
            
            # Pre-calculate words_by_start for faster segmentation
            cls._words_by_start = {}
            for w in cls._word_set:
                if w:
                    c = w[0]
                    if c not in cls._words_by_start:
                        cls._words_by_start[c] = []
                    cls._words_by_start[c].append(w)
        
        return cls._word_set, cls._word_to_pos, cls._word_freq_ipm, cls._max_ipm

    @classmethod
    def get_word_list(cls) -> List[str]:
        if cls._word_list is None:
            cls._word_list = list(cls.build_tables()[0])
        return cls._word_list

    @classmethod
    def load_bigrams(cls, limit: int = 50000) -> Dict[str, int]:
        cls.build_tables()
        return cls._bigrams

    @classmethod
    def get_context_candidates(cls, word: str, direction: str = 'fwd') -> List[Tuple[str, int]]:
        cls.build_tables()
        if direction == 'fwd':
            return cls._bigram_context_fwd.get(word, [])
        else:
            return cls._bigram_context_bwd.get(word, [])

    @classmethod
    def load_trigrams(cls, limit: int = 50000) -> Dict[str, int]:
        # Trigrams not in bundle yet to save space, returns empty
        return {}


    @classmethod
    def get_words_by_start(cls) -> Dict[str, List[str]]:
        cls.build_tables()
        return cls._words_by_start

    @classmethod
    def load_semantic_map(cls) -> Dict[str, str]:
        if cls._semantic_map is None:
            cls._semantic_map = {
                "បរិភោគ": "CONSUMPTION", "ញ៉ាំ": "CONSUMPTION", "ហូប": "CONSUMPTION",
                "ផឹក": "CONSUMPTION", "ពិសា": "CONSUMPTION",
                "បាយ": "EDIBLE", "ទឹក": "EDIBLE", "នំ": "EDIBLE", "ផ្លែឈើ": "EDIBLE",
                "សាច់": "EDIBLE", "ត្រី": "EDIBLE",
                "ដុំថ្ម": "INANIMATE", "តុ": "INANIMATE", "កៅអី": "INANIMATE",
                "ផ្ទះ": "INANIMATE", "ឡាន": "INANIMATE",
                "ដើរ": "MOVEMENT", "រត់": "MOVEMENT", "ហោះ": "MOVEMENT",
                "ជិះ": "MOVEMENT", "ហែល": "MOVEMENT",
                "សេចក្តី": "ABSTRACT", "ការ": "ABSTRACT", "ភាព": "ABSTRACT",
            }
        return cls._semantic_map


# ============================================================================
# Text Segmentation Functions
# ============================================================================
# NOTE: Segmentation functions have been moved to khmer_segmenter.py
# This includes: normalize_text(), is_kh_consonant(), is_kh_letter_seq(),
# get_char_type_cost(), viterbi_segment(), segment_text(), debug_segment()
# These functions are imported at the top of this file.
# ============================================================================

# Token classification and tagging
@lru_cache(maxsize=1024)
def classify_token(token: str) -> str:
    """Classify token type"""
    punct_set = {
        ".", ",", "?", "!", "។", "៕", "៖", "ៗ",
        "(", ")", "[", "]", "{", "}",
        "«", "»", '"', "'", "…", "—", "-",
        "%", "$", "+", "=", "*", "/", "៛",
    }
    
    if token in punct_set:
        return "PUNCT"
    
    if re.match(r'^[0-9០-៩\.]+$', token):
        return "NUM"
    
    if token.isspace():
        return "OTHER"
    
    for ch in token:
        if "\u1780" <= ch <= "\u17FF":
            return "WORD"
    
    return "OTHER"


def normalize_pos(pos_set: Set[str]) -> Set[str]:
    """Normalize POS tags"""
    normalized = set()
    for p in pos_set:
        if p in POS_MAP:
            normalized.add(POS_MAP[p])
    return normalized


def pos_tag_tokens(tokens: List[str], word_to_pos: Dict[str, Set[str]], 
                   word_set: Set[str]) -> List[dict]:
    """POS tag tokens"""
    tagged = []
    
    # Pre-defined tags for common words if missing
    # MANUAL_TAGS removed: imported from constants

    for t in tokens:
        token_type = classify_token(t)
        in_dict = False
        norm_pos = set()
        raw_pos = set()
        
        if token_type == "WORD":
            raw_pos = word_to_pos.get(t, set())
            norm_pos = normalize_pos(raw_pos)
            
            # Apply manual tags if empty or to supplement
            if t in MANUAL_TAGS:
                norm_pos.update(MANUAL_TAGS[t])
            elif t in WHITELIST_WORDS:
                # Infer Noun for typical whitelisted unknown words if no other tag
                if not norm_pos:
                    norm_pos.add("N")

            # Use is_known to apply filters
            in_dict = is_known(t)
            if t in WHITELIST_WORDS:
                in_dict = True

        elif token_type == "NUM":
            in_dict = True
            norm_pos = {"NUM"}
        elif token_type == "PUNCT":
            in_dict = True
        
        if t in PRONOUNS:
            norm_pos.add("PRON")
        
        tagged.append({
            "token": t,
            "type": token_type,
            "pos": norm_pos,
            "raw_pos": raw_pos,
            "in_dict": in_dict,
        })
    
    return tagged


# Error detection
@lru_cache(maxsize=4096)
def is_strict_word(token: str) -> bool:
    """Check if token is a valid dictionary word with filters"""
    # Safe strip trailings (ZWS, Space, etc.)
    token = token.strip().replace('\u200b', '')
    
    # Special case: Always allow repetition mark
    if token == "ៗ":
        return True
    
    if token not in SpellCheckerData._word_set:
        return False
        
    # Filter single consonants that are effectively junk (except 'ក៏')
    if len(token) == 1:
        if is_kh_consonant(token) and token != "ក៏":
             return False
        # Also filter dependent vowels/signs/numbers as single words
        cp = ord(token[0])
        if 0x17B4 <= cp <= 0x17D3: # Dependent vowels & signs
            return False

    
    # Filter suspicious short tokens
    if token in {"ន៏", "ហ៏", "គម", "រ"}:
         return False

    if token in BANNED_WORDS:
         return False
         
    return True

@lru_cache(maxsize=4096)
def is_known(token: str) -> bool:
    """Check if token is known word"""
    # 0. Check explicit typos (override compound check)
    if token in COMMON_TYPOS:
        return False

    # 1. Check strict dictionary
    if is_strict_word(token):
        return True
    
    # 2. Check compound
    return is_valid_compound(token, SpellCheckerData._word_set, SpellCheckerData.get_word_list())

def check_recursive_validity(text: str) -> bool:
    """Check if text is valid as single word or compound using strict filters"""
    if is_strict_word(text):
        return True
    
    for i in range(1, len(text)):
        if is_strict_word(text[:i]) and is_strict_word(text[i:]):
            return True
    return False


def is_valid_compound(word: str, word_set: Set[str], word_list: List[str]) -> bool:
    """Check if word is a valid compound"""
    # Check grammatical prefixes
    for prefix in SAFE_PREFIXES:
        if word.startswith(prefix) and len(word) > len(prefix):
            stem = word[len(prefix):]
            if check_recursive_validity(stem):
                return True
    
    # Check standard splits
    for i in range(1, len(word)):
        left = word[:i]
        right = word[i:]
        
        # Use is_strict_word to prevent "junk" + "junk" being valid
        if is_strict_word(left) and is_strict_word(right):
            if len(word) >= 9:
                return True
            
            matches = difflib.get_close_matches(word, word_list, n=1, cutoff=0.85)
            if matches:
                return False
            
            return True
    
    return False


def detect_register_mismatch(tagged_tokens: List[dict]) -> Dict[int, Dict]:
    """Detect mismatches between subject register and verb register (e.g., royal vs common)"""
    errors = {}
    
    for i in range(len(tagged_tokens) - 1):
        t1 = tagged_tokens[i]
        
        if t1["type"] != "WORD":
            continue
            
        # Check if this is a subject
        subject = t1["token"]
        is_royal_subject = any(royal in subject for royal in ROYAL_SUBJECTS)
        is_common_subject = subject in COMMON_SUBJECTS
        
        if not (is_royal_subject or is_common_subject):
            continue
        
        # Look for verb in next few tokens
        for j in range(i + 1, min(i + 5, len(tagged_tokens))):
            t2 = tagged_tokens[j]
            
            if t2["type"] != "WORD":
                continue
                
            verb = t2["token"]
            
            # --- Logic Enhancement: Semantic based check ---
            found_mismatch = False
            suggestion = None
            
            for meaning, variants in SEMANTIC_REGISTER_MAP.items():
                common_forms = variants.get("common", set())
                royal_forms = variants.get("royal", set())
                
                if is_royal_subject:
                    if verb in common_forms:
                        # Found Common verb with Royal Subject
                        
                        # EXCEPTION: Compound Motion Verbs (e.g. យាង + ទៅ)
                        # If verb is 'ទៅ' or 'មក', check if previous word was already a royal motion verb
                        if verb in {"ទៅ", "មក", "ដើរ"}:
                             # Look back from j
                             prev_k = j - 1
                             while prev_k > i:
                                 if tagged_tokens[prev_k]["type"] == "WORD":
                                     prev_word = tagged_tokens[prev_k]["token"]
                                     # If previous word is royal motion verb, this is valid compound
                                     if prev_word in {"យាង", "ស្តេចយាង", "ទ្រង់"}:
                                         found_mismatch = False
                                         break  # Break outer loop (skip this verb)
                                 prev_k -= 1
                             else:
                                 # Loop finished without break -> No royal antecedent found -> Mismatch
                                 found_mismatch = True
                                 # Pick best suggestion (first one)
                                 suggestion = list(royal_forms)[0] 
                        else:
                            found_mismatch = True
                            suggestion = list(royal_forms)[0]
                            
                elif is_common_subject:
                    if verb in royal_forms:
                        # Found Royal verb with Common Subject
                        found_mismatch = True
                        suggestion = list(common_forms)[0]
                
                if found_mismatch and suggestion:
                    # Don't override existing errors
                    if j not in errors:
                        errors[j] = {
                            'original': verb,
                            'suggestions': [suggestion],
                            'confidence': 0.90,
                            'error_type': 'register_mismatch'
                        }
                    break # Stop checking other meanings
            
            # If we found an error or valid compound exception, stop searching for verbs for this subject
            # (Simplification: assume one main verb per subject clause within window)
            if found_mismatch: 
                break
                
    return errors


def detect_contextual_confusion(tagged_tokens: List[dict], full_text: str) -> Dict[int, Dict]:
    """Detect commonly confused word pairs based on context"""
    errors = {}
    
    for pair_key, pair_info in CONTEXTUAL_PAIRS.items():
        for word, rules in pair_info.items():
            pattern = rules.get("pattern", "")
            if not pattern:
                continue
            
            # Find this word in tokens
            for i, t in enumerate(tagged_tokens):
                if t["type"] != "WORD" or t["token"] != word:
                    continue
                
                # Check if word appears in wrong context
                # Get surrounding context (3 words before and after)
                start_idx = max(0, i - 3)
                end_idx = min(len(tagged_tokens), i + 4)
                context_tokens = tagged_tokens[start_idx:end_idx]
                context_text = " ".join([ct["token"] for ct in context_tokens if ct["type"] == "WORD"])
                
                # Check if pattern matches
                import re
                if not re.search(pattern, context_text):
                    # Word is in wrong context, suggest the other word in pair
                    other_word = [w for w in pair_info.keys() if w != word][0]
                    
                    errors[i] = {
                        'original': word,
                        'suggestions': [other_word],
                        'confidence': 0.85,
                        'error_type': 'contextual'
                    }
    
    return errors


def detect_incomplete_words(tagged_tokens: List[dict], word_set: Set[str]) -> Dict[int, Dict]:
    """Detect words that are missing common endings"""
    errors = {}
    common_endings = ["រ", "ន", "ព", "ត", "ង", "ភាព", "ការ"]
    
    for i, t in enumerate(tagged_tokens):
        if t["type"] != "WORD":
            continue
            
        word = t["token"]
        
        # Skip if already known or too short
        if word in word_set or len(word) < 2:
            continue
        
        # Try adding common endings
        for ending in common_endings:
            candidate = word + ending
            if candidate in word_set:
                # Found a valid word by adding ending
                errors[i] = {
                    'original': word,
                    'suggestions': [candidate],
                    'confidence': 0.88,
                    'error_type': 'incomplete'
                }
                break
    
    return errors


# MANUAL_BIGRAMS removed: imported from constants

# SUSPICIOUS_BIGRAMS removed: imported from constants

def get_bigram_score(w1: str, w2: str, bigram_counts: Dict[str, int]) -> int:
    """Get bigram frequency score"""
    key = f"{w1} {w2}"
    if key in MANUAL_BIGRAMS:
        return 1000 # High fake score to validate this pair
    if key in SUSPICIOUS_BIGRAMS:
        return 0 # Force low score to trigger semantic check
    return bigram_counts.get(key, 0)


def detect_semantic_suspicion(tagged_tokens: List[dict], bigram_counts: Dict[str, int],
                               trigram_counts: Dict[str, int], word_list: List[str]) -> Dict[int, Dict]:
    """Detect contextual errors using context-driven search"""
    errors = {}
    
    # Thresholds
    SUSPICION_THRESHOLD = 50  # If current bigram score is lower than this
    SIMILARITY_THRESHOLD = 0.6 # For context candidates
    IMPROVEMENT_RATIO = 10.0
    
    # To map i, j to original token indices
    token_indices = list(range(len(tagged_tokens)))

    for i in range(len(tagged_tokens)):
        t1 = tagged_tokens[i]
        
        if t1["type"] != "WORD":
            continue
            
        # 0. Check Whitelist (Skip all checks if whitelisted)
        if t1["token"] in WHITELIST_WORDS:
            continue

        # 0. Check for Manual Typos First (Override all semantic checks)
        if t1["token"] in COMMON_TYPOS:
             # Respect whitelist!
             if t1["token"] in WHITELIST_WORDS:
                 pass # Skip typo flagging if whitelisted
             else:
                 errors[token_indices[i]] = {
                     'original': t1["token"],
                     'suggestions': [COMMON_TYPOS[t1["token"]]],
                     'confidence': 2.0,
                     'error_type': 'spelling'
                 }
                 continue
            
        # Find next word
        j = i + 1
        found_next = False
        while j < len(tagged_tokens):
             if tagged_tokens[j]["type"] == "WORD":
                 found_next = True
                 break
             if tagged_tokens[j]["type"] == "PUNCT":
                 break
             j += 1
        
        if not found_next:
            continue
            
        t2 = tagged_tokens[j]
        w1, w2 = t1["token"], t2["token"]
        current_score = get_bigram_score(w1, w2, bigram_counts)
        
        if current_score > SUSPICION_THRESHOLD:
            # Check manual suspicious list
            bg_key = f"{w1} {w2}"
            if bg_key in SUSPICIOUS_BIGRAMS:
                # Force suggestion
                sug = SUSPICIOUS_BIGRAMS[bg_key]
                # If sug is a bigram "Correct Correct", suggest it? 
                # Or if it's a mapping? "Bad Bad" -> "Good Good"
                # SUSPICIOUS_BIGRAMS maps "Bad" -> "Good"
                pass 
            else:
                continue

        # Strategy: Look for what SHOULD follow w1, and see if w2 is a typo of that.
        
        # Helper to get thresholds
        def get_thresholds(is_known_word, current_val, cand_val):
            # print(f"DEBUG: Checking thresholds. Known={is_known_word}, Curr={current_val}, Cand={cand_val}")
            
            # Base thresholds
            if is_known_word:
                 # VERY STRICT for known words
                 sim_thr = 0.90 
                 ratio_thr = 100.0 
            else:
                 sim_thr = 0.6
                 ratio_thr = 10.0
            
            # Relax similarity if Improvement is overwhelming
            # But DO NOT relax ratio for known words easily
            if cand_val > (current_val * 200) + 100:
                # If evidence is very strong, accept lower visual similarity
                # INCREASED threshold for known words to prevent valid words being swapped
                if is_known_word:
                    sim_thr = 0.80
                else:
                    sim_thr = 0.65 
            
            return sim_thr, ratio_thr

        # 1. Forward Context Analysis (w1 -> ?) checking w2
        is_known_w2 = t2.get("in_dict", False)
        
        # Safety: If w2 is in WHITELIST_WORDS, treat it as VERY known and skip semantic check
        # unless it's a known typo.
        if w2 in WHITELIST_WORDS:
             is_known_w2 = True
             # Skip semantic check for whitelisted words to prevent false positives
             # e.g. "បរទេស" (Foreign) -> "ប្រទេស" (Country)
             # unless we have a specific suspicious bigram rule.
             bg_key = f"{w1} {w2}"
             if bg_key not in SUSPICIOUS_BIGRAMS:
                 # Skip generic context check
                 continue
             else:
                 # Continue to check suspicious bigrams
                 pass
        
        if w2 not in WHITELIST_WORDS: # Only run generic check if not whitelisted
            expected_next = SpellCheckerData.get_context_candidates(w1, 'fwd')
            best_cand = None
            best_score = 0
            
            for cand_word, cand_score in expected_next:
                if cand_word == w2: continue 
                
                sim_thresh, ratio_thresh = get_thresholds(is_known_w2, current_score, cand_score)

                if cand_score < (current_score * ratio_thresh) + 5:
                    continue
                
                # For known words, enforce length similarity to prevent "LongValidWord" -> "ShortSubword"
                if is_known_w2:
                    if abs(len(w2) - len(cand_word)) > 2:
                        continue
                    # Prevent suggesting substring of known word (e.g. "កសាង" -> "សាង")
                    if w2 in cand_word or cand_word in w2:
                        continue

                sim = difflib.SequenceMatcher(None, w2, cand_word).ratio()
                if sim >= sim_thresh:
                    # Found a likely correction!
                    if cand_score > best_score:
                        best_score = cand_score
                        best_cand = cand_word
            
            if best_cand:
                errors[j] = {
                    'original': w2,
                    'suggestions': [best_cand],
                    'confidence': 0.85,
                    'error_type': 'contextual'
                }
                continue 

        # 1.5 Check Explicit Suspicious Bigrams (Forward/Bigram level)
        bg_key = f"{w1} {w2}"
        if bg_key in SUSPICIOUS_BIGRAMS:
             # "គូរ តែ" -> "គួរ តែ". Suggest "គួរ" for "គូរ" (w1).
             # "សា រះ" -> "សារៈ". Suggest merging?
             correct_phrase = SUSPICIOUS_BIGRAMS[bg_key]
             parts = correct_phrase.split()
             
             if len(parts) == 2:
                 cw1, cw2 = parts
                 if cw1 != w1:
                      errors[token_indices[i]] = {
                          'original': w1,
                          'suggestions': [cw1],
                          'confidence': 0.95,
                          'error_type': 'contextual'
                      }
                 if cw2 != w2:
                      errors[token_indices[j]] = {
                          'original': w2,
                          'suggestions': [cw2],
                          'confidence': 0.95,
                          'error_type': 'contextual'
                      }
             elif len(parts) == 1:
                 # Merging case handled by explicit semantic map, usually prefers Split Error logic.
                 # But if we are here, Split Error logic might have missed it.
                 # We can force a suggestion on w1, but w2 remains.
                 # Ideally, we rely on detect_error_slots to catch "concatenation" errors.
                 pass
             
             continue

        # 2. Backward Context Analysis (? -> w2) checking w1
        is_known_w1 = t1.get("in_dict", False)

        expected_prev = SpellCheckerData.get_context_candidates(w2, 'bwd')
        best_prev = None
        best_prev_score = 0
        
        for cand_word, cand_score in expected_prev:
            if cand_word == w1: continue
            
            sim_thresh, ratio_thresh = get_thresholds(is_known_w1, current_score, cand_score)
            
            if cand_score < (current_score * ratio_thresh) + 5:
                continue
            
            if is_known_w1:
                if abs(len(w1) - len(cand_word)) > 2:
                    continue
                if w1 in cand_word or cand_word in w1:
                    continue

            sim = difflib.SequenceMatcher(None, w1, cand_word).ratio()
            if sim >= sim_thresh:
                if cand_score > best_prev_score:
                    best_prev_score = cand_score
                    best_prev = cand_word
                    
        if best_prev:
            errors[i] = {
                'original': w1,
                'suggestions': [best_prev],
                'confidence': 0.85,
                'error_type': 'contextual'
            }

    return errors


# Whitelist logic removed: constants are now imported from spell_checker_constants.py



def detect_error_slots(tagged_tokens: List[dict], word_set: Set[str], 
                       word_list: List[str], bigram_counts: Dict[str, int],
                       trigram_counts: Dict[str, int], errors: Dict[int, Dict],
                       word_freq_ipm: Dict[str, float]) -> List[int]:
    """Detect spelling errors"""
    error_indices = set()
    
    for i, t in enumerate(tagged_tokens):
        # 0. Clean token for dictionary check
        token = t["token"].strip().replace('\u200b', '')
        if t["type"] == "WORD":

            if not token:
                 continue
            # 1. Check Manual Typos (High Priority)
            typo_fix = COMMON_TYPOS.get(token)
            if typo_fix:
                 # Check if the map is just to itself (safety)
                 if typo_fix != t["token"]:
                     errors[i] = {
                         'original': t["token"],
                         'suggestions': [typo_fix],
                         'confidence': 2.0,
                         'error_type': 'spelling'
                     }
                     continue

            # 2. Check Whitelist
            if token in WHITELIST_WORDS:
                continue


            if t["in_dict"]:
                # Check for Rare Word Confusion (e.g. "រេន" vs "រៀន")
                # Logic: If word is rare (freq < 10.0) and there is a VERY common neighbor (Ratio > 50), flag it.
                
                # Skip if word is a valid compound (not in strict set but is_known=True)
                # Compounds like "ការអប់រំ" have freq=0 but are valid.
                if t["token"] not in word_set:
                    # print(f"DEBUG: Skipping rare check for compound: {t['token']}")
                    continue

                freq = word_freq_ipm.get(token, 0)
                if freq < 1:
                     # print(f"DEBUG: Checking rare word: {token}, freq={freq}")
                     # Check close matches
                     # Check close matches
                     # Limit N to optimize speed
                     matches = difflib.get_close_matches(t["token"], word_list, n=5, cutoff=0.75)
                     # Filter for high freq neighbors (> 50.0 IPM)
                     # And ensure length is similar (typos usually preserve length)
                     # And ensure Frequency Ratio is significant (to avoid flagging valid rare words just because they look like common ones)
                     better = []
                     for m in matches:
                         if m == t["token"]: continue
                         if abs(len(m) - len(t["token"])) > 2: continue
                         
                         m_freq = word_freq_ipm.get(m, 0)
                         if m_freq > 50.0:
                             ratio = m_freq / max(freq, 0.01) # Avoid div by zero
                             if ratio > 50.0:
                                 better.append(m)
                     
                     if better:
                          # It is a likely typo masked as a rare dictionary word.
                          # Increase ratio for safer detection
                          if ratio > 100.0 or (freq < 1.0 and ratio > 50.0):
                               # Special check: if the "rare word" is actually a compound typo
                               # e.g. "បាយណាស" -> "បាយ" + "ណាស់"
                               # or "មកដ៏" -> "មក" + "ដល់"
                               
                               # If it contains "ដ៏" and isn't a known word --> Suggest ដល់ if reasonable
                               target_word = t["token"]
                               if "ដ៏" in target_word and "ដល់" not in target_word:
                                   errors[i] = {
                                        'original': target_word,
                                        'suggestions': [target_word.replace("ដ៏", "ដល់")],
                                        'confidence': 0.85,
                                        'error_type': 'spelling'
                                   } 
                                   continue
                               
                               if target_word.endswith("ណាស"):
                                    errors[i] = {
                                        'original': target_word,
                                        'suggestions': [target_word.replace("ណាស", "ណាស់")],
                                        'confidence': 0.90,
                                        'error_type': 'spelling'
                                   }
                                    continue

                               error_indices.add(i)
                               continue
            
            # Check for extra characters at word end (e.g., "គឺជារ" instead of "គឺជា")
            if len(token) > 2 and token.endswith("រ"):
                base = token[:-1]
                if base in word_set and base != token:
                    # Check if base word is much more common
                    base_freq = word_freq_ipm.get(base, 0)
                    token_freq = word_freq_ipm.get(token, 0)
                    if base_freq > token_freq * 10:  # Base is 10x more common
                        errors[i] = {
                            'original': t["token"],
                            'suggestions': [base],
                            'confidence': 0.85,
                            'error_type': 'spelling'
                        }
                        continue
            
            # Check for common consonant confusions (ច vs ជ, etc.)
            # Example: "ជីរភាព" should be "ចីរភាព"
            if "ជីរ" in token:
                corrected = token.replace("ជីរ", "ចីរ")
                if corrected in word_set:
                    errors[i] = {
                        'original': t["token"],
                        'suggestions': [corrected],
                        'confidence': 0.90,
                        'error_type': 'spelling'
                    }
                    continue

                continue
            
            is_likely_name = False
            if i > 0 and tagged_tokens[i - 1]["token"] in HONORIFICS:
                is_likely_name = True
            if i > 1 and tagged_tokens[i - 2]["token"] in HONORIFICS:
                is_likely_name = True
            
            if is_likely_name:
                continue
                
            if is_valid_compound(t["token"], word_set, word_list):
                continue
                
            error_indices.add(i)
            # Ensure an entry in errors dict for OOV words
            if i not in errors:
                # Basic suggestion attempt
                matches = difflib.get_close_matches(token, word_list, n=3, cutoff=0.7)
                errors[i] = {
                    'original': t["token"],
                    'suggestions': matches,
                    'confidence': 0.8,
                    'error_type': 'spelling'
                }
            
    # Detect split-word errors (e.g. "ប្រសិទ្ធ" + "ភា" -> "ប្រសិទ្ធភាព")
    # Logic: If two adjacent known words typically never appear together (bigram=0)
    # AND their concatenation is very close to a valid dictionary word, flag it.
    
    # 1. Gather all potential split errors
    split_errors = {} 
    
    i = 0
    while i < len(tagged_tokens):

        # Prevent overwriting existing high-confidence errors (e.g. Common Typos)
        # Modified: We allow split check to override OOV errors if context matches
        pass

        t1 = tagged_tokens[i]
        
        if t1['type'] != 'WORD':
            i += 1
            continue
            
        # Look ahead for next word, skipping whitespace
        j = i + 1
        sep = ""
        found_next_word = False
        
        while j < len(tagged_tokens):
            tn = tagged_tokens[j]
            if tn['type'] == 'WORD':
                found_next_word = True
                break
            
            # Stop if punctuation or non-whitespace key symbol found
            if tn['type'] == 'PUNCT' or tn['token'].strip():
                break
                
            sep += tn['token']
            j += 1
            
        if not found_next_word:
            i += 1
            continue
            
        t2 = tagged_tokens[j]
            
        concat = t1['token'] + t2['token']
        # Don't check tiny fragments to avoid noise
        if len(concat) < 4:
            i += 1
            continue

        # If one of the tokens is a KNOWN TYPO, do not attempt to merge it.
        # We want to correct the typo itself, not merge it.
        if t1['token'] in COMMON_TYPOS or t2['token'] in COMMON_TYPOS:
             i += 1
             continue

        # Optimization: Start with bigram check. If these words commonly go together, 
        # normally we skip. BUT if their concatenation is a dictionary word, it's likely a split typo.
        bg_count = get_bigram_score(t1['token'], t2['token'], bigram_counts)
        is_concat_valid = concat in word_set
        
        # Refined Logic: 
        # If words are commonly seen together (bg > 0), assume they are correct SEPARATE words.
        # UNLESS the concatenated form is a specific "Split Word" typo we know about.
        

        bg_key = f"{t1['token']} {t2['token']}"
        force_merge = False
        forced_suggestion = None
        
        if bg_key in SUSPICIOUS_BIGRAMS:
             sug = SUSPICIOUS_BIGRAMS[bg_key]
             if len(sug.split()) == 1:
                 force_merge = True
                 forced_suggestion = sug
                 
        if forced_suggestion:

             split_errors[i] = {
                 'original': f"{t1['token']}{sep}{t2['token']}",
                 'suggestions': [forced_suggestion],
                 'confidence': 1.0,
                 'error_type': 'spelling'
             }
             i = j + 1
             continue

        # Prevent merging known words separated by space unless forced
        if (t1['in_dict'] and t2['in_dict']) and len(sep) > 0 and not force_merge:
             i += 1
             continue

        if bg_count > 0 and not force_merge:
            # Check if we should force merge?
            if concat not in COMMON_TYPOS:
                 i += 1
                 continue
        
        # Check if concat is ALREADY a valid word (space missing/unnecessary split)
        if concat in word_set:
             # Additional check: If separated by substantial punctuation, don't merge?
             if len(sep.strip()) > 0 and not force_merge: 
                  i += 1
                  continue
             
             # Check for trivial merge (no visual change)
             # If sep is empty, original "A""B" -> suggestion "AB". Visual: "AB" -> "AB".
             if not sep:
                 i = j + 1
                 continue

             # Safety Check: If concat is identical to t1 or t2, it's not a split error
             if concat == t1['token'] or concat == t2['token']:
                 i += 1
                 continue


             split_errors[i] = {
                 'original': f"{t1['token']}{sep}{t2['token']}",
                 'suggestions': [concat],
                 'confidence': 1.0,
                 'error_type': 'spelling'
             }
             i = j + 1
             continue
             
        # Check if concat is CLOSE to a valid word
        # STOPWORD GUARD: If t1 or t2 is a Stopword, be stricter to avoid eating it.
        # e.g. "ជា" + "សេចក្តី" -> "សេចក្តី" (Bad!)
        is_stop_merge = (t1['token'] in STOPWORDS or t2['token'] in STOPWORDS)
        
        matches = difflib.get_close_matches(concat, word_list, n=1, cutoff=0.92)
        if not matches:
             # Relax for short words specifically to catch single-char typos
             # For shorter words, allow lower threshold (e.g. 1 char diff in 4 chars = 0.75)
             cutoff_val = 0.90
             if len(concat) <= 5:
                  cutoff_val = 0.70
             else:
                  cutoff_val = 0.85
                  
             matches = difflib.get_close_matches(concat, word_list, n=1, cutoff=cutoff_val)


        if matches:
             suggestion = matches[0]
             # Safety: If suggestion is exactly one of the known tokens, ignore it.
             if suggestion == t1['token'] or suggestion == t2['token']:
                 i += 1
                 continue

             # NEW: If BOTH tokens are known, do NOT fuzzy-merge them
             # unless the concat is an EXACT dictionary word.
             # This prevents 'ពណ៌' + 'នៃ' -> 'ពណ៌នា' or 'បញ្ជាក់' + 'ការ' -> 'បញ្ជាការ'
             if t1['in_dict'] and t2['in_dict']:
                  if concat != suggestion:
                       i += 1
                       continue

             if is_stop_merge:
                 # If we are merging a Stopword (e.g. "ជា"), we must ensure we aren't just deleting it.
                 # If suggestion is very close to t2, and t1 is the stopword, we are deleting t1.
                 if t1['token'] in STOPWORDS:
                      # Check similarity between suggestion and t2
                      if difflib.SequenceMatcher(None, suggestion, t2['token']).ratio() > 0.8:
                           i += 1
                           continue
                 if t2['token'] in STOPWORDS:
                      if difflib.SequenceMatcher(None, suggestion, t1['token']).ratio() > 0.8:
                           i += 1
                           continue


             split_errors[i] = {
                 'original': f"{t1['token']}{sep}{t2['token']}",
                 'suggestions': matches,
                 'confidence': 0.95,
                 'error_type': 'spelling'
             }
             pass
             
        i += 1

    # 2. Merge split_errors into main errors
    # Note: This might overlap with existing errors (though we usually check knowns here).
    # If index `i` is already an error, we merge suggestions.
    for idx, err_info in split_errors.items():

        errors[idx] = err_info
        
        # To prevent double-error on t2 if it was also flagged (unlikely if valid),
        # we can attempt to clean up. But since we might have skipped tokens, 
        # simplistic removal of idx+1 is risky if idx+1 is space.
        # Ideally we should remove the failure of the SECOND word.
        # But for now, let's just leave it or improve.
        # If we merged t1 and t2 (at index j), we might want to ensure j is not reported as separate error?
        # But 'errors' depends on detection order. 
        # Given we are replacing errors[idx], we are fine.
        
        # We can try to clear subsequent error if it exists?
        # But we don't know J here easily unless we stored it.
        pass


    # Semantic errors (Contextual) - DISABLED per user request (not robust enough)
    # semantic_errors = detect_semantic_suspicion(tagged_tokens, bigram_counts, 
    #                                            trigram_counts, word_list)
    
    # for idx, err_info in semantic_errors.items():
    #     if idx not in errors:
    #         errors[idx] = err_info
            
    # Grammar errors (Rules like A, B, C)
    grammar_errors = detect_grammar_errors(tagged_tokens, errors)
    for idx, err_info in grammar_errors.items():
        # Smart Merge: Keep existing error if higher confidence
        if idx in errors:
             if errors[idx].get('confidence', 0.0) >= err_info.get('confidence', 0.0):
                 continue
        errors[idx] = err_info
    
    # Merge all unique error indices
    all_indices = error_indices.union(set(errors.keys()))
    return sorted(list(all_indices))



def detect_grammar_errors(tagged_tokens: List[dict], errors: Dict[int, Dict]) -> Dict[int, Dict]:
    """
    Detect grammatical errors based on specific rule sets.
    Specifically checks for usage ofនិង (and), នឹង (will/stay), ហ្នឹង (that).
    Also checks SUSPICIOUS_BIGRAMS for context errors.
    """
    
    # 0. Check Suspicious Bigrams (Context phrases)
    for i in range(len(tagged_tokens) - 1):
        if i in errors: continue
        
        t1 = tagged_tokens[i]["token"]
        t2 = tagged_tokens[i+1]["token"]
        
        # Skip if punctuation involved (unless expected?)
        if tagged_tokens[i]["type"] != "WORD" or tagged_tokens[i+1]["type"] != "WORD":
            continue
            
        bg_key = f"{t1} {t2}"
        if bg_key in SUSPICIOUS_BIGRAMS:
             correction = SUSPICIOUS_BIGRAMS[bg_key]
             # If correction is 2 words, we suggest replacement for the error part
             parts = correction.split()
             if len(parts) == 2:
                 c1, c2 = parts
                 if c1 != t1:
                     errors[i] = {'original': t1, 'suggestions': [c1], 'confidence': 0.95, 'type': 'PHRASE', 'error_type': 'contextual'}
                 if c2 != t2:
                     errors[i+1] = {'original': t2, 'suggestions': [c2], 'confidence': 0.95, 'type': 'PHRASE', 'error_type': 'contextual'}
             elif len(parts) == 1:
                 # Merge suggestion?
                 pass


    
    # Helper to check if a token has a specific POS
    def has_pos(token_idx, pos_tag):
        if token_idx < 0 or token_idx >= len(tagged_tokens):
            return False
        # 'pos' is a set like {'N', 'V', 'ADJ'}
        return pos_tag in tagged_tokens[token_idx].get("pos", set())

    # Helper to check if token is noun or verb or adjective
    def is_verb(idx): 
        if idx < 0 or idx >= len(tagged_tokens): return False
        t = tagged_tokens[idx]
        if "V" in t.get("pos", set()): return True
        # Common behavior: if it's whitelisted but unknown, it's rarely a verb unless manually tagged
        return False

    def is_noun(idx): 
        if idx < 0 or idx >= len(tagged_tokens): return False
        t = tagged_tokens[idx]
        pos = t.get("pos", set())
        if "N" in pos or "PRON" in pos or "NUM" in pos: return True
        # If whitelisted or technical but no POS, assume Noun
        if t["token"] in WHITELIST_WORDS or t["token"] in TECHNICAL_TERMS:
            return True
        return False

    # Adjectives in Khmer often act as Verbs (Stative Verbs), so treat ADJ as potential Verb context
    def is_verb_like(idx): 
        if idx < 0 or idx >= len(tagged_tokens): return False
        t = tagged_tokens[idx]
        pos = t.get("pos", set())
        return "V" in pos or "ADJ" in pos
    
    # Iterate tokens
    for i in range(len(tagged_tokens)):
        token = tagged_tokens[i]["token"]
        
        # Rule A: និង (and) + Verb -> Error (Should be នឹង (will))
        # Refined: Only flag if preceded by PRON or Name (Subject). 
        # "Eat and Sleep" (Verb និង Verb) is valid.
        if token == "និង":
            # Exception: "ដូចគ្នានឹង" (Same as) - "នឹង" is correct, but if user wrote "និង", flag it?
            # Wait, the rule is checking for "និង" (and) where it should be "នឹង" (will).
            # If user wrote "ដូចគ្នានឹង", token is "នឹង". This block is for "និង".
            # If user wrote "ដូចគ្នានិង", it might be wrong if "ដូចគ្នានឹង" is the standard.
            # But let's check the reverse rule (checking "នឹង").
            
            next_idx = i + 1
            while next_idx < len(tagged_tokens) and tagged_tokens[next_idx]["type"] == "OTHER":
                next_idx += 1
            
            if next_idx < len(tagged_tokens):
                # Check previous context
                prev_idx = i - 1
                while prev_idx >= 0 and tagged_tokens[prev_idx]["type"] == "OTHER":
                    prev_idx -= 1
                    
                prev_is_subject = False
                if prev_idx >= 0:
                    prev_pos = tagged_tokens[prev_idx].get("pos", set())
                    if "PRON" in prev_pos or tagged_tokens[prev_idx]["token"] in HONORIFICS:
                         prev_is_subject = True
                    # Also if previous is proper noun (Name)? Hard to know.
                
                # Only apply if strictly Subject + And + Verb
                if prev_is_subject:
                    next_tok = tagged_tokens[next_idx]["token"]
                    if is_verb_like(next_idx) and next_tok not in {"អាច", "គួរ", "គប្បី", "ត្រូវ"}:
                         errors[i] = {
                             'original': token,
                             'suggestions': ["នឹង"],
                             'confidence': 0.90,
                             'type': 'GRAMMAR_A_WILL',
                             'error_type': 'contextual'
                         }
                         continue

        # Rule B: Noun + នឹង (will) + Noun -> Error (Should be និង (and))

        # Example: សៀវភៅ នឹង ប៊ិច -> សៀវភៅ និង ប៊ិច
        if token == "នឹង":
            prev_idx = i - 1
            while prev_idx >= 0 and tagged_tokens[prev_idx]["type"] == "OTHER":
                prev_idx -= 1
            
            next_idx = i + 1
            while next_idx < len(tagged_tokens) and tagged_tokens[next_idx]["type"] == "OTHER":
                next_idx += 1
                
            if prev_idx >= 0 and next_idx < len(tagged_tokens):
                # Check Noun + Will + Noun
                if is_noun(prev_idx) and is_noun(next_idx):
                    # But wait, "Dog will eat" (Noun Will Verb) is valid.
                    # Noun Will Noun? "Dog will cat"? No.
                    # "Book will Pen"? No.
                    # So checking if next is Noun is key.
                    # If it's ambiguous, safer to flag if it's strictly Noun or Noun-heavy freq.
                    
                    # Exception: "This is the thing that I will..." -> "នេះ គឺជា អ្វី ហ្នឹង..." (That)
                    # If "នឹង" acts as "That" (demonstrative), it usually follows a Noun.
                    # "Book that I read" -> "សៀវភៅ ហ្នឹង..."
                    # So Noun + នឹង + ... could be "This/That".
                    # But Rule B explicitly asks to change to "and". "Book and Pen".
                    # "Book that Pen"? No.
                    # Exception: Phrases like "ប្រឈមមុខនឹង" or "ជាមួយនឹង" where "នឹង" is correct
                    prev_word = tagged_tokens[prev_idx]["token"]
                    prev_prev_idx = prev_idx - 1
                    while prev_prev_idx >= 0 and tagged_tokens[prev_prev_idx]["type"] == "OTHER":
                        prev_prev_idx -= 1
                    
                    is_prepositional_phrase = False
                    if prev_word in {"ជាមួយ", "ជាប់", "ជួប", "ទាក់ទង", "ដូចគ្នា", "ស្មើ", "ស្រដៀង", "ស្រដៀងគ្នា", "ខុស", "ខុសគ្នា"}:
                        is_prepositional_phrase = True
                    elif prev_word == "មុខ" and prev_prev_idx >= 0 and tagged_tokens[prev_prev_idx]["token"] == "ប្រឈម":
                        is_prepositional_phrase = True
                    elif prev_word == "គ្នា" and prev_prev_idx >= 0 and tagged_tokens[prev_prev_idx]["token"] in {"ស្រដៀង", "ដូច", "ខុស"}:
                        is_prepositional_phrase = True
                    
                    if is_prepositional_phrase:
                        continue
                    
                    # Safety Check: If next word is clearly a Verb, do NOT suggest "And".
                    # "He will come" -> "គាត់ នឹង មក". "មក" might be Noun/Verb ambiguous, but in this slot it's likely Verb.
                    if is_verb(next_idx) or is_verb_like(next_idx):
                        continue
                    
                    # Exception: "សមនឹង" (Fit with/Suitable for)
                    if prev_word == "សម":
                        continue
                    
                    # Exception: "ផ្តល់នូវ" (Give [obj]) - wait, this is "នូវ" not "នឹង".
                    # But "ផ្តល់ នឹង"? No.
                    # "ផ្តល់ នូវ" is correct.
                    # If user wrote "ផ្តល់ នឹង", it's wrong.
                    # But here we are checking "នឹង" -> "និង".
                    # "Give and Take" -> "ផ្តល់ និង ទទួល".
                    # "Give will Take"? No.
                    
                    # Exception: "ខ្ញុំ នឹង ផ្តល់" (I will give).
                    # "ខ្ញុំ" (Pronoun/Noun) + "នឹង" + "ផ្តល់" (Verb).
                    # is_verb(next_idx) should catch "ផ្តល់".
                    # But "ផ្តល់" might be unknown or Noun/Verb.
                    # If next word is "ផ្តល់", skip.
                    if tagged_tokens[next_idx]["token"] == "ផ្តល់":
                        continue

                    errors[i] = {
                        'original': token,
                        'suggestions': ["និង"],
                        'confidence': 0.99,
                        'type': 'GRAMMAR_B_AND',
                        'error_type': 'contextual'
                    }
                    continue

        # Rule C: End of Sentence (EOS) + "និង"/"នឹង" -> Error (Should be "ហ្នឹង" or "នឹង" (still))
        # User says: "almost never និង".
        # So if "និង" at EOS -> Error.
        # Check EOS condition
        is_eos = False
        next_idx = i + 1
        while next_idx < len(tagged_tokens) and tagged_tokens[next_idx]["type"] == "OTHER":
             next_idx += 1
        
        if next_idx >= len(tagged_tokens):
            is_eos = True
        elif tagged_tokens[next_idx]["type"] == "PUNCT":
            # Check if it's sentence ending punct
            if tagged_tokens[next_idx]["token"] in {"។", "?", "!", "\n"}:
                is_eos = True
        
        if is_eos:
            if token == "និង": # "And" at end -> Wrong
                 errors[i] = {
                     'original': token,
                     'suggestions': ["ហ្នឹង"], # "That" usually
                     'confidence': 0.98,
                     'type': 'GRAMMAR_C_EOS',
                     'error_type': 'contextual'
                 }
            elif token == "នឹង": # "Will" at end -> "Still" or "That"?
                 # User says "usually ហ្នឹង (casual) or នឹង (stay still), but almost never និង."
                 # So "នឹង" is technically valid if it means "Stay still" (នៅ នឹង).
                 # But if it stands alone or follows Noun?
                 # "អី ហ្នឹង?" (What is that?) -> "អី នឹង?" is wrong.
                 # "នៅ នឹង?" (Stay still?) -> Valid.
                 
                 # Heuristic: If preceded by "នៅ" (Stay), keep "នឹង".
                 prev_idx = i - 1
                 while prev_idx >= 0 and tagged_tokens[prev_idx]["type"] == "OTHER":
                    prev_idx -= 1
                 
                 prev_word = tagged_tokens[prev_idx]["token"] if prev_idx >= 0 else ""
                 
                 if prev_word == "នៅ":
                     continue # Valid "Stay still"
                 
                 # Otherwise often casual "That" -> "ហ្នឹង"
                 # Suggest "ហ្នឹង" with high confidence?
                 # Or just lower confidence?
                 pass 
                 # Given user request specially mentions "almost never និង" as the error case.
                 # I will strictly flag "និង" -> "ហ្នឹង".
                 # And maybe Suggest "ហ្នឹង" for "នឹង" if not "នៅ".
                 
                 if prev_word != "នៅ":
                      # Optional suggestion
                      # errors[i] = {'original': token, 'suggestions': ["ហ្នឹង"], 'confidence': 0.7}
                      pass

    
        # Rule D: នៅ (At) vs នូវ (Object Marker)
        # Usage: Transitive Verb + នូវ + Object
        # Incorrect: Transitive Verb + នៅ + Object (unless 'At')
        # if token == "នៅ":
        if False: # Disabled: Main loop handles this better
            prev_idx = i - 1
            while prev_idx >= 0 and tagged_tokens[prev_idx]["type"] == "OTHER":
                prev_idx -= 1
            
            if prev_idx >= 0:
                prev_tok = tagged_tokens[prev_idx]["token"]
                
                # List of verbs that strongly require 'នូវ' (Object Marker) when followed by an object
                # and rarely take 'នៅ' unless specifying location.
                TRANSITIVE_VERBS_NOV = {
                     "ផ្តល់", "ផ្ដល់", "បង្កើត", "បង្ហាញ", "អនុវត្ត", "អនុវត្តន៍",
                     "ដាក់ចេញ", "លើកកម្ពស់", "ពង្រឹង", "ការពារ", "ថែរក្សា", "រក្សា",
                     "បង្ក", "នាំមក", "នាំយក", "ទទួល", "ទទួលបាន", "មាន", "ប្រកាន់យក"
                }

                
                if prev_tok in TRANSITIVE_VERBS_NOV:
                    # Check next token to see if it's likely an object (Noun) vs Location
                    # Simplify: If it's a Noun, suggest 'នូវ'
                    next_idx = i + 1
                    while next_idx < len(tagged_tokens) and tagged_tokens[next_idx]["type"] == "OTHER":
                        next_idx += 1
                    
                    if next_idx < len(tagged_tokens):
                         # If next word is "ក្នុង", "លើ", "ក្រោម" (Prepositions), then 'នៅ' is correct (Stay in/at).
                         # e.g. "ថែរក្សា នៅ ក្នុង" (Maintain in...)
                         next_tok = tagged_tokens[next_idx]["token"]
                         if next_tok in {"ក្នុង", "លើ", "ក្រោម", "ឯ", "ក្បែរ", "ខាង"}:
                             continue
                             
                         # If next is Noun, huge chance it's 'នូវ'
                         if is_noun(next_idx):
                              errors[i] = {
                                  'original': token,
                                  'suggestions': ["នូវ"],
                                  'confidence': 0.85,
                                  'type': 'GRAMMAR_D_NOV',
                                  'error_type': 'contextual'
                              }
                              continue

        # Rule E: ពី (from) vs ពីរ (two)
        if token == "ពីរ":
            # If preceded by motion/origin verbs (e.g. ចេញ, មក, ទៅ)
            # AND not followed by a classifier (e.g. នាក់, គ្រឿង, ក្បាល)
            prev_idx = i - 1
            while prev_idx >= 0 and tagged_tokens[prev_idx]["type"] == "OTHER":
                prev_idx -= 1
            
            if prev_idx >= 0:
                prev_tok = tagged_tokens[prev_idx]["token"]
# MOTION_VERBS removed: imported from constants
                
                if prev_tok in MOTION_VERBS:
                    next_idx = i + 1
                    while next_idx < len(tagged_tokens) and tagged_tokens[next_idx]["type"] == "OTHER":
                        next_idx += 1
                    
                    if next_idx < len(tagged_tokens):
                        next_tok = tagged_tokens[next_idx]["token"]
                        CLASSIFIERS = {
                            "នាក់", "រូប", "អង្គ", "ព្រះ", "ក្បាល", "ច្បាប់", "គ្រឿង", "ដុំ",
                            "បន្ទះ", "សន្លឹក", "ដើម", "ផ្លែ", "ខ្នង", "ល្វែង", "គ្រាប់", "គូ",
                            "ប្រអប់", "កំប៉ុង", "ដប", "ម៉ោង", "នាទី", "វិនាទី", "ដុល្លារ", "រៀល",
                            "បាត", "ឆ្នាំ", "ខែ", "ថ្ងៃ", "ដង", "លើក", "ភាគរយ"
                        }
                        if next_tok not in CLASSIFIERS:
                            errors[i] = {
                                'original': token,
                                'suggestions': ["ពី"],
                                'confidence': 0.90,
                                'type': 'GRAMMAR_E_FROM',
                                'error_type': 'contextual'
                            }
                            continue
        
        # Rule E Reverse: ពី (from) vs ពីរ (two)
        if token == "ពី":
            # If followed by a classifier (e.g. នាក់, គ្រឿង, ក្បាល)
            next_idx = i + 1
            while next_idx < len(tagged_tokens) and tagged_tokens[next_idx]["type"] == "OTHER":
                next_idx += 1
            
            if next_idx < len(tagged_tokens):
                next_tok = tagged_tokens[next_idx]["token"]
                CLASSIFIERS = {
                    "នាក់", "រូប", "អង្គ", "ព្រះ", "ក្បាល", "ច្បាប់", "គ្រឿង", "ដុំ",
                    "បន្ទះ", "សន្លឹក", "ដើម", "ផ្លែ", "ខ្នង", "ល្វែង", "គ្រាប់", "គូ",
                    "ប្រអប់", "កំប៉ុង", "ដប", "ម៉ោង", "នាទី", "វិនាទី", "ដុល្លារ", "រៀល",
                    "បាត", "ឆ្នាំ", "ខែ", "ថ្ងៃ", "ដង", "លើក", "ភាគរយ"
                }
                if next_tok in CLASSIFIERS:
                    errors[i] = {
                        'original': token,
                        'suggestions': ["ពីរ"],
                        'confidence': 0.90,
                        'type': 'GRAMMAR_E_TWO',
                        'error_type': 'contextual'
                    }
                    continue
        
        # Rule 7: ដែរ (also) vs ដែល (relative pronoun)
        if token == "ដែរ":
            # ដែរ should be at end of sentence or before punctuation (means "also/too")
            # If followed by a verb/noun, it's likely wrong (should be ដែល)
            next_idx = i + 1
            while next_idx < len(tagged_tokens) and tagged_tokens[next_idx]["type"] == "OTHER":
                next_idx += 1
            
            if next_idx < len(tagged_tokens):
                next_tok = tagged_tokens[next_idx]
                # If followed by WORD (not punctuation), likely should be ដែល
                if next_tok["type"] == "WORD" and next_tok["token"] not in {"។", "?", "!"}:
                    errors[i] = {
                        'original': token,
                        'suggestions': ["ដែល"],
                        'confidence': 0.90,
                        'type': 'GRAMMAR_7_REL',
                        'error_type': 'contextual'
                    }
                    continue

        elif token == "ដែល":
            # ដែល should be followed by a clause (verb/noun)
            # If at end of sentence, it's wrong (should be ដែរ)
            next_idx = i + 1
            while next_idx < len(tagged_tokens) and tagged_tokens[next_idx]["type"] == "OTHER":
                next_idx += 1
            
            is_eos = next_idx >= len(tagged_tokens) or tagged_tokens[next_idx]["token"] in {"។", "?", "!", "\n"}
            
            if is_eos:
                errors[i] = {
                    'original': token,
                    'suggestions': ["ដែរ"],
                    'confidence': 0.95,
                    'type': 'GRAMMAR_7_ALSO',
                    'error_type': 'contextual'
                }
                continue
        
        # Rule 8: ដល់ (to/reach) vs ដ៏ (adjective marker)
        if token == "ដល់":
            # ដ៏ is used before adjectives as intensifier
            # ដល់ is used as "to/reach/until"
            next_idx = i + 1
            while next_idx < len(tagged_tokens) and tagged_tokens[next_idx]["type"] == "OTHER":
                next_idx += 1
            
            if next_idx < len(tagged_tokens):
                next_tok = tagged_tokens[next_idx]
                # If followed by common adjectives, should be ដ៏
                COMMON_ADJECTIVES = {"ល្អ", "ស្អាត", "ធំ", "តូច", "ខ្ពស់", "ទាប", "ស្រស់", "ត្រចះត្រចង់", "សម្បូរបែប", "វិសេសវិសាល", "អស្ចារ្យ"}
                if next_tok["token"] in COMMON_ADJECTIVES or "ADJ" in next_tok.get("pos", set()):
                    errors[i] = {
                        'original': token,
                        'suggestions': ["ដ៏"],
                        'confidence': 0.92,
                        'type': 'GRAMMAR_8_ADJ_MARKER',
                        'error_type': 'contextual'
                    }
                    continue

        elif token == "ដ៏":
            # ដ៏ should be followed by adjective
            # Only flag if clearly wrong (followed by location/verb)
            next_idx = i + 1
            while next_idx < len(tagged_tokens) and tagged_tokens[next_idx]["type"] == "OTHER":
                next_idx += 1
            
            if next_idx < len(tagged_tokens):
                next_tok = tagged_tokens[next_idx]
                # Only flag if followed by clear location/direction words
                LOCATION_DIRECTION = {"សាលារៀន", "ផ្ទះ", "ផ្សារ", "មន្ទីរពេទ្យ", "ក្រុង", "ខេត្ត"}
                if next_tok["token"] in LOCATION_DIRECTION:
                    errors[i] = {
                        'original': token,
                        'suggestions': ["ដល់"],
                        'confidence': 0.88,
                        'type': 'GRAMMAR_8_TO_REACH',
                        'error_type': 'contextual'
                    }
                    continue
        
        # Rule 9: ន័យ (meaning) vs នៃ (of/possessive)
        if token == "ន័យ":
            # ន័យ means "meaning" and should be preceded by "មាន" or similar
            # នៃ is possessive marker (of)
            prev_idx = i - 1
            while prev_idx >= 0 and tagged_tokens[prev_idx]["type"] == "OTHER":
                prev_idx -= 1
            
            # If preceded by noun (not "មាន"), likely should be នៃ
            if prev_idx >= 0:
                prev_tok = tagged_tokens[prev_idx]["token"]
                if prev_tok not in {"មាន", "ដឹង", "យល់", "ស្វែងរក"} and is_noun(prev_idx):
                    errors[i] = {
                        'original': token,
                        'suggestions': ["នៃ"],
                        'confidence': 0.90,
                        'type': 'GRAMMAR_9_OF',
                        'error_type': 'contextual'
                    }
                    continue

        elif token == "នៃ":
            # នៃ should be between two nouns (possessive)
            # If followed by verb "យ៉ាងដូចម្តេច" or similar, should be ន័យ
            next_idx = i + 1
            while next_idx < len(tagged_tokens) and tagged_tokens[next_idx]["type"] == "OTHER":
                next_idx += 1
            
            if next_idx < len(tagged_tokens):
                next_tok = tagged_tokens[next_idx]["token"]
                # Check for "នៃយ៉ាងដូចម្តេច" pattern (should be ន័យ)
                if next_tok in {"យ៉ាង", "ដូចម្តេច", "ថា"}:
                    errors[i] = {
                        'original': token,
                        'suggestions': ["ន័យ"],
                        'confidence': 0.85,
                        'type': 'GRAMMAR_9_MEANING',
                        'error_type': 'contextual'
                    }
                    continue
        
        # Rule 6: Detect incomplete words (missing final consonant/vowel)
        # Common pattern: words ending in ភា should be ភាព
        INCOMPLETE_PATTERNS = {
            "ការងា": "ការងារ",
            "ជីវភា": "ជីវភាព",
            "សកម្មភា": "សកម្មភាព",
            "សុខុមាលភា": "សុខុមាលភាព",
            "មោទនភា": "មោទនភាព",
            "ឯករាជ្យភា": "ឯករាជ្យភាព",
            "សេរីភា": "សេរីភាព",
            "សមភា": "សមភាព",
            "តម្លាភា": "តម្លាភាព",
            "គណនេយ្យភា": "គណនេយ្យភាព",
            "វិបុលភា": "វិបុលភាព",
            "ស្ថិរភា": "ស្ថិរភាព",
            "បរិស្ថា": "បរិស្ថាន",
            "ជនពិកា": "ជនពិការ",
            "កិច្ចសន្យ": "កិច្ចសន្យា",
            "សក្ខីកម": "សក្ខីកម្ម",
            "ឧស្សាហកម": "ឧស្សាហកម្ម",
            # Short forms if split
            "ងា": "ងារ", # Context check usually done by bigram/trigram logic, but 'ងា' is rare
            "ពិកា": "ពិការ",
        }
        
        if token in INCOMPLETE_PATTERNS:
            errors[i] = {
                'original': token,
                'suggestions': [INCOMPLETE_PATTERNS[token]],
                'confidence': 0.95,
                'type': 'INCOMPLETE_WORD',
                'error_type': 'spelling'
            }
            continue
        
        # Rule 2 Enhancement: នាក់ at sentence start (should be អ្នក)
        if token == "នាក់":
            # Check if at sentence start or after punctuation
            prev_idx = i - 1
            while prev_idx >= 0 and tagged_tokens[prev_idx]["type"] == "OTHER":
                prev_idx -= 1
            
            is_sentence_start = prev_idx < 0 or tagged_tokens[prev_idx]["token"] in {"។", "?", "!", "\n"}
            
            if is_sentence_start:
                errors[i] = {
                    'original': token,
                    'suggestions': ["អ្នក"],
                    'confidence': 0.95,
                    'type': 'GRAMMAR_2_TITLE',
                    'error_type': 'contextual'
                }
                continue
        
        # Rule D Reverse: នូវ (object marker) vs នៅ (location)
        if token == "នូវ":
            # នូវ should NOT be followed by location words
            next_idx = i + 1
            while next_idx < len(tagged_tokens) and tagged_tokens[next_idx]["type"] == "OTHER":
                next_idx += 1
            
            if next_idx < len(tagged_tokens):
                next_tok = tagged_tokens[next_idx]["token"]
                LOCATION_WORDS = {"ផ្ទះ", "សណ្ឋាគារ", "ក្នុង", "លើ", "ក្រោម", "ឯ", "ខាង", "ក្បែរ"}
                
                if next_tok in LOCATION_WORDS:
                    errors[i] = {
                        'original': token,
                        'suggestions': ["នៅ"],
                        'confidence': 0.90,
                        'type': 'GRAMMAR_D_LOCATION',
                        'error_type': 'contextual'
                    }
                    continue
        
        # Rule: ផ្សា vs ផ្សារ (Contextual spelling)
        # ផ្សារ = market/place, ផ្សា = sting/spicy sensation
        if token == "ផ្សា":
            # Check if preceded by ទៅ (go to) or នៅ (at) - should be ផ្សារ (market)
            prev_idx = i - 1
            while prev_idx >= 0 and tagged_tokens[prev_idx]["type"] == "OTHER":
                prev_idx -= 1
            
            if prev_idx >= 0:
                prev_tok = tagged_tokens[prev_idx]["token"]
                if prev_tok in {"ទៅ", "នៅ"}:
                    errors[i] = {
                        'original': token,
                        'suggestions': ["ផ្សារ"],
                        'confidence': 0.95,
                        'type': 'GRAMMAR_PHSA_LOCATION',
                        'error_type': 'contextual'
                    }
                    continue
            
            # Check if followed by ដែក (iron) or កញ្ចក់ (glass) - should be ផ្សារ
            next_idx = i + 1
            while next_idx < len(tagged_tokens) and tagged_tokens[next_idx]["type"] == "OTHER":
                next_idx += 1
            
            if next_idx < len(tagged_tokens):
                next_tok = tagged_tokens[next_idx]["token"]
                if next_tok in {"ដែក", "កញ្ចក់"}:
                    errors[i] = {
                        'original': token,
                        'suggestions': ["ផ្សារ"],
                        'confidence': 0.95,
                        'type': 'GRAMMAR_PHSA_MATERIAL',
                        'error_type': 'contextual'
                    }
                    continue
        
        elif token == "ផ្សារ":
            # Check if followed by ភ្នែក (eyes) or របួស (wound) - should be ផ្សា
            next_idx = i + 1
            while next_idx < len(tagged_tokens) and tagged_tokens[next_idx]["type"] == "OTHER":
                next_idx += 1
            
            if next_idx < len(tagged_tokens):
                next_tok = tagged_tokens[next_idx]["token"]
                if next_tok in {"ភ្នែក", "របួស"}:
                    errors[i] = {
                        'original': token,
                        'suggestions': ["ផ្សា"],
                        'confidence': 0.95,
                        'type': 'GRAMMAR_PHSAR_BODY',
                        'error_type': 'contextual'
                    }
                    continue
            
            # Check if preceded by ឈឺ (hurt) or ភ្នែក/របួស (within 3 words) - should be ផ្សា
            prev_idx = i - 1
            while prev_idx >= 0 and tagged_tokens[prev_idx]["type"] == "OTHER":
                prev_idx -= 1
            
            if prev_idx >= 0:
                prev_tok = tagged_tokens[prev_idx]["token"]
                if prev_tok == "ឈឺ":
                    errors[i] = {
                        'original': token,
                        'suggestions': ["ផ្សា"],
                        'confidence': 0.95,
                        'type': 'GRAMMAR_PHSAR_HURT',
                        'error_type': 'contextual'
                    }
                    continue
            
            # Also check if ភ្នែក or របួស appears within 3 words before ផ្សារ
            # This catches cases like "ភ្នែកខ្ញុំផ្សារ" (my eyes sting)
            check_idx = i - 1
            words_checked = 0
            while check_idx >= 0 and words_checked < 3:
                if tagged_tokens[check_idx]["type"] == "WORD":
                    if tagged_tokens[check_idx]["token"] in {"ភ្នែក", "របួស"}:
                        errors[i] = {
                            'original': token,
                            'suggestions': ["ផ្សា"],
                            'confidence': 0.90,
                            'type': 'GRAMMAR_PHSAR_BODY',
                            'error_type': 'contextual'
                        }
                        break
                    words_checked += 1
                check_idx -= 1


    return errors

# Candidate generation and scoring
def infer_expected_pos(tagged_tokens: List[dict], idx: int) -> Set[str]:
    """Infer expected POS at position"""
    left_pos = tagged_tokens[idx - 1]["pos"] if idx > 0 else set()
    expected = set()
    
    if "PRON" in left_pos:
        expected.update(["V", "ADV"])
    if "PREP" in left_pos:
        expected.update(["N", "PRON"])
    if "N" in left_pos:
        expected.update(["ADJ", "V", "PREP"])
    if "V" in left_pos:
        expected.update(["N", "PRON", "ADV", "V", "PREP"])
    if "ADJ" in left_pos:
        expected.add("ADV")
    if "ADV" in left_pos:
        expected.update(["V", "ADJ"])
    
    return expected


def pos_compatibility_score(candidate: str, expected_pos: Set[str],
                            word_to_pos: Dict[str, Set[str]]) -> float:
    """Score candidate based on POS compatibility"""
    if not expected_pos:
        return 0.5
    
    candidate_pos = normalize_pos(word_to_pos.get(candidate, set()))
    return 1.0 if candidate_pos & expected_pos else 0.0


def frequency_score(word: str, word_freq_ipm: Dict[str, float], max_ipm: float) -> float:
    """Score candidate based on frequency"""
    if max_ipm <= 0:
        return 0.0
    
    ipm = word_freq_ipm.get(word)
    return min(ipm / max_ipm, 1.0) if ipm is not None else 0.0


def final_candidate_score(levenshtein_score: float, pos_score: float,
                         freq_score: float, alpha: float = 0.5,
                         beta: float = 0.15, gamma: float = 0.35) -> float:
    """Combine scores"""
    weight_sum = alpha + beta + gamma
    return (alpha * levenshtein_score + beta * pos_score + gamma * freq_score) / weight_sum


# Common typos and whitelist extension removed: constants are now imported from spell_checker_constants.py

@lru_cache(maxsize=1024)
def generate_candidates(error_word: str, max_candidates: int = 8,
                       cutoff: float = 0.6) -> List[dict]:
    """Generate correction candidates"""
    word_set, _, _, _ = SpellCheckerData.build_tables()
    word_list = SpellCheckerData.get_word_list()
    
    results = []
    
    # Check manual typos first
    if error_word in COMMON_TYPOS:
        results.append({"word": COMMON_TYPOS[error_word], "levenshtein_score": 1.0})
        
    close = difflib.get_close_matches(error_word, word_list, n=max_candidates, cutoff=cutoff)
    for w in close:
        sim = difflib.SequenceMatcher(None, error_word, w).ratio()
        results.append({"word": w, "levenshtein_score": sim})
    
    
    # NOTE: For Khmer, we do NOT suggest splitting with spaces (e.g. "WordA WordB").
    # We disabled the loop that does: split_candidate = f"{left} {right}".
            
    # Check for extra character at end (e.g. "somethings" -> "something")
    if len(error_word) > 1:
        shorter = error_word[:-1]
        if shorter in word_set:
             # Add with very high score
             results.append({"word": shorter, "levenshtein_score": 0.99})

    final_results = []
    for r in results:
         # Aggressive space filtering and banned words
         if ' ' in r['word'] or '\u200b' in r['word'] or '\u00a0' in r['word']:
             continue
         if r['word'] in BANNED_WORDS:
             continue
         final_results.append(r)
         
    return final_results


@lru_cache(maxsize=1024)
def generate_concat_candidates(left: str, right: str,
                               max_candidates: int = 8, cutoff: float = 0.8) -> List[dict]:
    """Generate candidates for concatenation of two tokens (boundary error).
    Example: left='លោ', right='លក' => concat='លោលក' close to 'លោក'.
    """
    word_list = SpellCheckerData.get_word_list()
    import difflib as _dl
    concat = left + right
    close = _dl.get_close_matches(concat, word_list, n=max_candidates, cutoff=cutoff)
    results = []
    for w in close:
        # Aggressive space filtering to prevent "Ghost Space" suggestions
        if ' ' in w or '\u200b' in w or '\u00a0' in w:
            continue
        sim = _dl.SequenceMatcher(None, concat, w).ratio()
        results.append({"word": w, "levenshtein_score": sim})
    return results


def rerank_candidates(candidates: List[dict], tagged_tokens: List[dict],
                     error_idx: int, word_to_pos: Dict[str, Set[str]],
                     word_freq_ipm: Dict[str, float], max_ipm: float) -> List[dict]:
    """Rerank candidates using contextual scores"""
    expected_pos = infer_expected_pos(tagged_tokens, error_idx)
    
    for c in candidates:
        # Boost manual typos/fixes
        is_manual = False
        original_word = tagged_tokens[error_idx]["token"]
        
        if original_word in COMMON_TYPOS and COMMON_TYPOS[original_word] == c["word"]:
             c["final_score"] = 2.0 # Max priority
             continue

        c["pos_score"] = pos_compatibility_score(c["word"], expected_pos, word_to_pos)
        c["freq_score"] = frequency_score(c["word"], word_freq_ipm, max_ipm)
        c["final_score"] = final_candidate_score(c["levenshtein_score"],
                                                c["pos_score"], c["freq_score"])
    
    return sorted(candidates, key=lambda x: x["final_score"], reverse=True)


# Main spell checking function
def check_spelling(text: str) -> Dict[str, object]:
    """Check spelling and return errors with suggestions."""
    try:
        # Load data tables
        word_set, word_to_pos, word_freq_ipm, max_ipm = SpellCheckerData.build_tables()
        bigram_counts = SpellCheckerData.load_bigrams()
        trigram_counts = SpellCheckerData.load_trigrams()
        word_list = SpellCheckerData.get_word_list()

        # Segment and tag
        words_by_start = SpellCheckerData.get_words_by_start()
        tokens = segment_text(text, word_set, word_freq_ipm, words_by_start, is_known)
        tagged = pos_tag_tokens(tokens, word_to_pos, word_set)


        errors: Dict[int, Dict] = {}
        current_sentence_status = 1 # Track highest status subject in current sentence
        prev_sentence_status = 1    # Persist status from previous sentence (for pronouns)
        
        try:
             # Detect single-token errors
             error_indices = detect_error_slots(tagged, word_set, word_list,
                                               bigram_counts, trigram_counts, errors,
                                               word_freq_ipm)
        except Exception as e:
             print(f"CRITICAL ERROR in detect_error_slots: {e}")
             import traceback
             traceback.print_exc()
             raise e
        
        # NEW: Detect register mismatches (royal vs common language)
        try:
            register_errors = detect_register_mismatch(tagged)
            for idx, err in register_errors.items():
                if idx not in errors:  # Don't override existing errors
                    errors[idx] = err
        except Exception as e:
            print(f"Warning: Error in detect_register_mismatch: {e}")
        
        # NEW: Detect contextual word confusion
        try:
            contextual_errors = detect_contextual_confusion(tagged, text)
            for idx, err in contextual_errors.items():
                if idx not in errors:  # Don't override existing errors
                    errors[idx] = err
        except Exception as e:
            print(f"Warning: Error in detect_contextual_confusion: {e}")
        
        # NEW: Detect incomplete words
        try:
            incomplete_errors = detect_incomplete_words(tagged, word_set)
            for idx, err in incomplete_errors.items():
                if idx not in errors:  # Don't override existing errors
                    errors[idx] = err
        except Exception as e:
            print(f"Warning: Error in detect_incomplete_words: {e}")
        
        # ---------------------------------------------------------
        # Grammatical Rule: នៅ (At/Stay) vs នូវ (Object Marker)
        # ---------------------------------------------------------
# TRANSITIVE_VERBS_NOV logic removed: imported from constants (pre-updated)
        
        # Helper to get valid previous word token skipping spaces/punct
        def get_prev_word(idx, tokens):
            k = idx - 1
            while k >= 0:
                if tokens[k]["type"] == "WORD" or tokens[k]["type"] == "NUM":
                    return tokens[k]
                k -= 1
            return None

# KHMER_NUM_WORDS and CLASSIFIERS removed: imported from constants
# noun_classifier_map removed: imported from constants
        
        # Places and Times constants (Moved out of loop for efficiency)
# LOC_TIME_WORDS removed: imported from constants
        
        # 0. Pre-calculate token offsets in original text to detect spacing errors
        token_offsets = []
        _curr = 0
        for _t in tokens:
            _raw = _t.strip()
            if not _raw:
                token_offsets.append(-1)
                continue
            
            # Form 1: Literal
            _pos = text.find(_raw, _curr)
            
            # Form 2: Combined variant
            if _pos == -1:
                _alt = _raw.replace("\u17c1\u17b8", "\u17be")
                if _alt != _raw:
                    _pos = text.find(_alt, _curr)
            
            # Form 3: Split variant
            if _pos == -1:
                _alt = _raw.replace("\u17be", "\u17c1\u17b8")
                if _alt != _raw:
                    _pos = text.find(_alt, _curr)

            if _pos != -1:
                token_offsets.append(_pos)
                # Find length of the form that actually matched in the original text
                # We need to peek at the text to see which one it was for correct _curr shift
                # But for simplicity, we'll try to guess based on standard length
                # or just advance by the matched found text if possible.
                # Here we just use a heuristic or search again.
                # Actually, find() tells us exactly where it starts. 
                # We can check the text at that position to see how long it is.
                # A quick way: check if text[pos:pos+len(raw)] == raw else use alt length
                if text[_pos:_pos+len(_raw)] == _raw:
                    _curr = _pos + len(_raw)
                else:
                    # It matched one of the alternates. We'll find its length.
                    _curr = _pos + 1 # At least advance
                    # Better: try to find which one it was
                    if text[_pos:_pos+len(_raw.replace("\u17c1\u17b8", "\u17be"))] == _raw.replace("\u17c1\u17b8", "\u17be"):
                         _curr = _pos + len(_raw.replace("\u17c1\u17b8", "\u17be"))
                    elif text[_pos:_pos+len(_raw.replace("\u17be", "\u17c1\u17b8"))] == _raw.replace("\u17be", "\u17c1\u17b8"):
                         _curr = _pos + len(_raw.replace("\u17be", "\u17c1\u17b8"))
                    else:
                         _curr = _pos + len(_raw) # Fallback
            else:
                token_offsets.append(-1)

        # Multi-sentence tracking for Rule 9
        sentence_start_idx = 0
        last_sentence_content_idx = -1

        # Rule 5: Honorific Logic Definitions (Moved outside loop)
        SUBJECT_LEVELS = {
            "ខ្ញុំ": 1, "គាត់": 1, "អ្នក": 1, "គេ": 1, "យើង": 1, "វា": 1, "សត្វ": 1, "ឆ្កែ": 1, "ឆ្មា": 1,
            "កុមារ": 1, "ក្មេង": 1, "បុរស": 1, "ស្ត្រី": 1,
            "លោក": 2, "លោកស្រី": 2, "អ្នកគ្រូ": 2, "លោកគ្រូ": 2, "ចាស់ទុំ": 2, 
            "បង": 2, "បងស្រី": 2, "បងប្រុស": 2, "គ្រូ": 2, "គ្រូបង្រៀន": 2,
            "ឯកឧត្តម": 2, "លោកជំទាវ": 2, "ឧត្តម": 2, "ភ្ញៀវ": 2,
            "ព្រះសង្ឃ": 3, "ភិក្ខុ": 3, "សាមណេរ": 3, "លោកតា": 3, "សង្ឃ": 3, "ព្រះតេជគុណ": 3,
            "អាត្មា": 3, 
            "ព្រះមហាក្សត្រ": 4, "ស្ដេច": 4, "ស្តេច": 4, "ព្រះអង្គ": 4, "ទ្រង់": 4, "មហាក្សត្រ": 4,
            "រាជ": 4, "ក្សត្រ": 4, "ព្រះនាង": 4, "ព្រះរាជបុត្រ": 4, "សម្តេច": 4, "សម្ដេច": 4
        }
        
        VERB_LEVELS = {
            "ហូប": 1, "ញ៉ាំ": 1, "ស៊ី": 1, "មាំ": 0, "ពិសា": 2, "ទទួលទាន": 2, "ឆាន់": 3, "សោយ": 4, 
            "ដេក": 1, "សម្រាក": 2, "សឹង": 3, "ផ្ទុំ": 4,
            "ដើរ": 1, "ទៅ": 1, "មក": 1, "អញ្ជើញ": 2, "និមន្ត": 3, "យាង": 4,
            "និយាយ": 1, "ស្តី": 1, "ប្រសាសន៍": 2, "មានប្រសាសន៍": 2, "សង្ឃដីកា": 3, "មានសង្ឃដីកា": 3, "ព្រះបន្ទូល": 4, "មានព្រះបន្ទូល": 4,
            "ស្លាប់": 1, "ងាប់": 1, "មរណភាព": 2, "អនិច្ចកម្ម": 2, "សុគត": 3, "សោយទិវង្គត": 4,
            "កើត": 1, "ប្រសូត": 4, "ផឹក": 1, "ពិសា": 2, "ឆាន់": 3, "សេព": 4,
            "ងូតទឹក": 1, "ជម្រះកាយ": 2, "ស្រង់": 3, "ស្រង់ទឹក": 3, "សេពសោយ": 4, "ងូត": 1,
            "មើល": 1, "ទត": 4, "ទស្សនា": 2,
            "ឱ្យ": 1, "ឲ្យ": 1, "ផ្តល់": 2, "ប្រគេន": 3, "ថ្វាយ": 4, "ជូន": 2,
            "វិល": 1, "ត្រឡប់": 1, "និវត្ត": 4, "យាងត្រឡប់": 4, "និមន្តត្រឡប់": 3
        }
        
        VERB_CORRECTIONS = {
            "EAT": {1: "ញ៉ាំ", 2: "ពិសា", 3: "ឆាន់", 4: "សោយ"},
            "SLEEP": {1: "ដេក", 2: "សម្រាក", 3: "សឹង", 4: "ផ្ទុំ"},
            "WALK": {1: "ដើរ", 2: "អញ្ជើញ", 3: "និមន្ត", 4: "យាង"},
            "SPEAK": {1: "និយាយ", 2: "ប្រសាសន៍", 3: "សង្ឃដីកា", 4: "ព្រះបន្ទូល"},
            "DIE": {1: "ស្លាប់", 2: "អនិច្ចកម្ម", 3: "សុគត", 4: "សោយទិវង្គត"},
            "BORN": {1: "កើត", 2: "សម្រាលកូន", 3: "កើត", 4: "ប្រសូត"},
            "DRINK": {1: "ផឹក", 2: "ពិសា", 3: "ឆាន់", 4: "សេព"},
            "BATHE": {1: "ងូតទឹក", 2: "ជម្រះកាយ", 3: "ស្រង់", 4: "សេពសោយ"},
            "SEE": {1: "មើល", 2: "ទស្សនា", 3: "មើល", 4: "ទត"},
            "GIVE": {1: "ឱ្យ", 2: "ជូន", 3: "ប្រគេន", 4: "ថ្វាយ"},
            "RETURN": {1: "ត្រឡប់", 2: "ត្រឡប់", 3: "និមន្តត្រឡប់", 4: "យាងត្រឡប់"}
        }
        
        VERB_TO_ACTION = {
            "ហូប": "EAT", "ញ៉ាំ": "EAT", "ស៊ី": "EAT", "ពិសា": "EAT", "ទទួលទាន": "EAT", "ឆាន់": "EAT", "សោយ": "EAT",
            "ដេក": "SLEEP", "សម្រាក": "SLEEP", "សឹង": "SLEEP", "ផ្ទុំ": "SLEEP",
            "ដើរ": "WALK", "ទៅ": "WALK", "មក": "WALK", "អញ្ជើញ": "WALK", "និមន្ត": "WALK", "យាង": "WALK",
            "និយាយ": "SPEAK", "ប្រសាសន៍": "SPEAK", "សង្ឃដីកា": "SPEAK", "ព្រះបន្ទូល": "SPEAK",
            "ស្លាប់": "DIE", "ងាប់": "DIE", "មរណភាព": "DIE", "អនិច្ចកម្ម": "DIE", "សុគត": "DIE", "សោយទិវង្គត": "DIE",
            "កើត": "BORN", "សម្រាលកូន": "BORN", "ប្រសូត": "BORN",
            "ផឹក": "DRINK", "សេព": "DRINK",
            "ងូតទឹក": "BATHE", "ជម្រះកាយ": "BATHE", "ស្រង់": "BATHE", "ស្រង់ទឹក": "BATHE", "សេពសោយ": "BATHE", "ងូត": "BATHE",
            "មើល": "SEE", "ទត": "SEE", "ទស្សនា": "SEE",
            "ឱ្យ": "GIVE", "ឲ្យ": "GIVE", "ផ្តល់": "GIVE", "ប្រគេន": "GIVE", "ថ្វាយ": "GIVE", "ជូន": "GIVE",
            "វិល": "RETURN", "ត្រឡប់": "RETURN", "និវត្ត": "RETURN", "យាងត្រឡប់": "RETURN", "និមន្តត្រឡប់": "RETURN"
        }
        
        NOUN_LEVELS = {
            "បាយ": {3: "ចង្ហាន់", 4: "ព្រះស្ងោយ"},
            "ទឹក": {3: "ទឹក", 4: "ទឹក"},
            "ផ្ទះ": {3: "កុដិ", 4: "ព្រះរាជដំណាក់"},
            "លុយ": {3: "បច្ច័យ", 4: "ព្រះរាជទ្រព្យ"},
            "ប្រាក់": {3: "បច្ច័យ", 4: "ព្រះរាជទ្រព្យ"},
            "សំបុត្រ": {3: "លិខិត", 4: "ព្រះរាជសារ"},
            "ចិត្ត": {3: "ព្រះទ័យ", 4: "ព្រះរាជហឫទ័យ"},
            "ដៃ": {3: "ព្រះហស្ត", 4: "ព្រះហស្ត"},
            "ជើង": {3: "ព្រះបាទ", 4: "ព្រះបាទ"},
            "ក្បាល": {3: "ព្រះកេស", 4: "ព្រះកេស"},
            "ពោះ": {4: "ព្រះឧដរ"},
            "មាត់": {4: "ព្រះឱស្ឋ"},
            "ច្រមុះ": {4: "ព្រះនាសិក"},
            "ភ្នែក": {4: "ព្រះនេត្រ"},
            "ត្រចៀក": {4: "ព្រះសោតៈ"},
        }

        for i, t in enumerate(tagged):
            word = t["token"]
            # print(f"LOOP: i={i} word='{word}' type={t['type']}")
            # Grammar rules should only apply to context usage of valid words, or add new errors.
            if i in errors and errors[i].get('error_type') == 'spelling':
                 # Special Case Loophole for Rule 6 (Incomplete Word)
                 # If it looks like 'ការងា' (missing 'រ'), we want to suggest 'ការងារ' specifically
                 if len(word) >= 2 and word.endswith("ា") and is_known(word + "រ"):
                     pass 
                 else:
                     continue
            
            
            # Skip processing space tokens except punctuation symbols used in rules
            if t["type"] not in ("WORD", "NUM") and word not in ("។", "៕", "នូវ", "៖", "!", "?", "ៗ"):
                # But still track sentence ends for non-ignored punctuation if any
                if word in {"។", "៕", "?"}:
                   sentence_start_idx = i + 1
                   last_sentence_content_idx = -1
                # if word in ('ភិក្ខុ', 'ដេក'): print(f"TRACE: Skipped {word} due to type/punct check. Type: {t['type']}")
                continue

            if t["type"] in ("WORD", "NUM"):
                last_sentence_content_idx = i

            # Update sentence status FIRST (before any checks)
            # Reset on punctuation
            if t["type"] == "PUNCT" and word in ("។", "៕", "?"):
                prev_sentence_status = current_sentence_status
                current_sentence_status = 1
            
            # Update current sentence status based on subjects found
            if t["type"] == "WORD":
                norm_word = word.replace("\u17d2\u178a", "\u17d2\u178f")
                subj_val = -1
                for title, level in SUBJECT_LEVELS.items():
                     norm_title = title.replace("\u17d2\u178a", "\u17d2\u178f")
                     if norm_title in norm_word:
                          if level > subj_val:
                               subj_val = level
                
                if i > 0:
                     combined = (tagged[i-1]["token"] + word).replace("\u17d2\u178a", "\u17d2\u178f")
                     for title, level in SUBJECT_LEVELS.items():
                          norm_title = title.replace("\u17d2\u178a", "\u17d2\u178f")
                          if norm_title in combined:
                               if level > subj_val:
                                    subj_val = level
                
                if subj_val > current_sentence_status:
                    current_sentence_status = subj_val

            # NOW check noun honorifics (after status is updated)
            if t["type"] in ("WORD", "NUM"):
                if word in NOUN_LEVELS:
                    req_level = max(current_sentence_status, prev_sentence_status)
                    # Lookahead 
                    if req_level < 3:
                         m_la = i + 1
                         w_la = 0
                         while m_la < len(tagged) and w_la < 5:
                              if tagged[m_la]["type"] == "WORD":
                                   w_la += 1
                                   for title, level in SUBJECT_LEVELS.items():
                                        if title in tagged[m_la]["token"] and level > req_level:
                                             req_level = level
                              if tagged[m_la]["token"] in ("។", "៕", "?"): break
                              m_la += 1
                    if req_level >= 3:
                        mapping = NOUN_LEVELS[word]
                        sugg = mapping.get(req_level)
                        if sugg and sugg != word:
                             # Exclude monks giving 'លុយ'
                             skip_noun = False
                             if word == "លុយ":
                                  prev_tok = get_prev_word(i, tagged)
                                  if prev_tok and prev_tok["token"] in ("ឱ្យ", "ឲ្យ", "ផ្តល់"):
                                       skip_noun = True
                             if not skip_noun:
                                  errors[i] = {'original': word, 'suggestions': [sugg], 'confidence': 0.85, 'error_type': 'contextual'}

            prev = get_prev_word(i, tagged)
            
            # Places and Times that almost always use "នៅ"
# LOC_TIME_WORDS removed: imported from constants

            if word == "នូវ":
                # Check previous word
                is_wrong = False
# INTRANSITIVE_VERBS and AUXILIARIES removed: imported from constants

                if prev:
                    p_word = prev["token"]
                    # 1. Subjective check
                    if "PRON" in prev["pos"] or p_word in PRONOUNS:
                        is_wrong = True
                    # 2. Intransitive/Motion check
                    elif p_word in INTRANSITIVE_VERBS:
                        is_wrong = True
                    # 3. Location/Time check (Previous word)
                    elif any(loc in p_word for loc in LOC_TIME_WORDS):
                        is_wrong = True
                    # 4. Auxiliary check (unless auxiliary follows a transitive verb)
                    elif p_word in AUXILIARIES:
                        # Scan back for verb
                        verb_before = None
                        vk = i - 2
                        while vk >= max(0, i - 4):
                            if tagged[vk]["type"] == "WORD":
                                verb_before = tagged[vk]["token"]
                                break
                            vk -= 1
                        if not verb_before or verb_before not in TRANSITIVE_VERBS_NOV:
                            is_wrong = True
                else:
                    # Start of sentence
                    is_wrong = True
                
                # Check next word for Location/Time
                next_idx = i + 1
                while next_idx < len(tagged) and tagged[next_idx]["type"] == "OTHER":
                    next_idx += 1
                
                if not is_wrong and next_idx < len(tagged):
                    n_word = tagged[next_idx]["token"]
                    if any(loc in n_word for loc in LOC_TIME_WORDS):
                        is_wrong = True

                # Terminal Check: "នូវ" cannot end a sentence or precede punctuation
                if not is_wrong:
                    next_tok = None
                    if i + 1 < len(tagged):
                        next_tok = tagged[i+1]
                    
                    if not next_tok or next_tok["token"] in ("។", "៕", "?", "!", "៖", " ", "។\n"):
                        is_wrong = True

                if is_wrong:
                    # Special case: 'ទៅដ៏' is almost always 'ទៅដល់'
                    if p_word == "ទៅ":
                        errors[i] = {'original': word, 'suggestions': ["ដល់"], 'confidence': 0.99, 'error_type': 'contextual'}
                    else:
                        errors[i] = {'original': word, 'suggestions': ["នៅ"], 'confidence': 0.95, 'error_type': 'contextual'}


            elif word == "នៅ":
                # Add whitelist for location contexts where នៅ is correct
                LOCATION_CONTEXTS = {
                    "កម្ពុជា", "ភ្នំពេញ", "សៀមរាប", "ទន្លេសាប", "កំពត", "កណ្តាល",
                    "សាកលវិទ្យាល័យ", "វិទ្យាស្ថាន", "បណ្ណាល័យ", "បណ្ណាគារ",
                    "សាលារៀន", "មន្ទីរពេទ្យ", "ផ្សារ", "ផ្ទះ", "ក្រុង", "ខេត្ត",
                    "ភូមិន្ទ", "បច្ចេកវិទ្យា", "ស្រុក", "ឃុំ", "ភូមិ", "លើ", "ក្រោម",
                    "ដារ៉ា", "សោភា", "ធារា", "រដ្ឋ", "ជាតិ", "ស្ថាប័ន", "យូធូប"
                }
                
                # Check if next word is a location
                next_idx = i + 1
                while next_idx < len(tagged) and tagged[next_idx]["type"] == "OTHER":
                    next_idx += 1
                
                skip_check = False
                if next_idx < len(tagged):
                    next_tok = tagged[next_idx]["token"]
                    # If next word is location or contains location, នៅ is correct
                    is_loc = any(loc in next_tok for loc in LOCATION_CONTEXTS)
                    # print(f"DEBUG: Checking 'នៅ' followed by '{next_tok}'. Is Loc: {is_loc}")
                    if is_loc:
                        skip_check = True
                
                # Consolidate TRANSITIVE_VERBS_NOV usage
                # DISABLED: Too many false positives (e.g. ខ្ញុំញ៉ាំបាយនៅហាង -> នូវ)
                # It is safer to allow "នៅ" (At) than to incorrectly suggest "នូវ" (Obj Marker).
                # if not skip_check and prev and prev["token"] in TRANSITIVE_VERBS_NOV:
                #      # Check if next word looks like an object (not a preposition/time)
                #      next_idx = i + 1
                #      while next_idx < len(tagged) and tagged[next_idx]["type"] == "OTHER":
                #          next_idx += 1
                #      
                #      if next_idx < len(tagged):
                #          next_t = tagged[next_idx]
                #          # More conservative: Only flag if next word is clearly an abstract noun/concept
                #          # Avoid flagging if it could be location/time or adjective
                #          if (next_t["token"] not in LOC_TIME_WORDS and 
                #              next_t["pos"] and "ADJ" not in next_t["pos"] and
                #              next_t["token"] not in {"បៃតង", "ស្អាត", "ល្អ", "ធំ", "តូច"}):
                #              # Additional check: Ensure it's not a compound location phrase
                #              if not any(loc in next_t["token"] for loc in ["ក្នុង", "ក្រៅ", "លើ", "ក្រោម"]):
                #                  errors[i] = {'original': word, 'suggestions': ["នូវ"], 'confidence': 0.75, 'error_type': 'contextual'}


            # ---------------------------------------------------------
            # Rule 3: Classifiers (Khor-Kha Principle)
            # ---------------------------------------------------------
            if t["type"] == "NUM" or word in KHMER_NUM_WORDS or re.match(r'^[0-9០-៩]+$', word):
                # Look ahead for next WORD only
                k = i + 1
                next_word_token = None
                next_word_idx = -1
                while k < len(tagged):
                    if tagged[k]["type"] in ("WORD", "NUM") or tagged[k]["token"] in KHMER_NUM_WORDS:
                        next_word_token = tagged[k]
                        next_word_idx = k
                        break
                    k += 1
                
                found_classifier = False
                if next_word_token:
                    next_word = next_word_token["token"]
                    if next_word in CLASSIFIERS or next_word == "អ្នក":
                        found_classifier = True
                        
                        # Sub-rule: Validate existing classifier against noun (backwards or forwards)
                        found_noun_token = None
                        
                        # 1. Look backwards (skip spaces/junk)
                        temp_k = i - 1
                        word_count = 0
                        while temp_k >= 0 and word_count < 4:
                            tok = tagged[temp_k]
                            if tok["type"] == "WORD":
                                word_count += 1
                                if tok["token"] in noun_classifier_map:
                                    found_noun_token = tok["token"]
                                    break
                                # Check combined with previous if it's a prefix
                                if temp_k > 0 and tagged[temp_k-1]["token"] + tok["token"] in noun_classifier_map:
                                    found_noun_token = tagged[temp_k-1]["token"] + tok["token"]
                                    break
                            elif tok["type"] == "PUNCT": break
                            temp_k -= 1
                        
                        # 2. Look forwards if not found (skip spaces/junk)
                        if not found_noun_token:
                            temp_k = next_word_idx + 1
                            word_count = 0
                            while temp_k < len(tagged) and word_count < 3:
                                tok = tagged[temp_k]
                                if tok["type"] == "WORD":
                                    word_count += 1
                                    if tok["token"] in noun_classifier_map:
                                        found_noun_token = tok["token"]
                                        break
                                elif tok["type"] == "PUNCT": break
                                temp_k += 1

                        if found_noun_token:
                            valid_list = noun_classifier_map[found_noun_token]
                            if next_word not in valid_list:
                                errors[next_word_idx] = {
                                    'original': next_word,
                                    'suggestions': valid_list,
                                    'confidence': 0.98, # High confidence for specific classifier
                                    'locked': True, # Mark as locked so Rule 2 doesn't overwrite
                                    'error_type': 'contextual'
                                }
                
                if not found_classifier:
                    # Look backwards for noun to suggest missing classifier
                    found_noun_token = None
                    temp_k = i - 1
                    word_count = 0
                    while temp_k >= 0 and word_count < 4:
                        tok = tagged[temp_k]
                        if tok["type"] == "WORD":
                            word_count += 1
                            if tok["token"] in noun_classifier_map:
                                found_noun_token = tok["token"]
                                break
                            if temp_k > 0 and tagged[temp_k-1]["token"] + tok["token"] in noun_classifier_map:
                                found_noun_token = tagged[temp_k-1]["token"] + tok["token"]
                                break
                        elif tok["type"] == "PUNCT": break
                        temp_k -= 1

                    if found_noun_token:
                        sug_list = noun_classifier_map[found_noun_token]
                        if sug_list:
                            errors[i] = {
                                'original': word,
                                'suggestions': [f"{word} {c}" for c in sug_list],
                                'confidence': 0.90,
                                'error_type': 'contextual'
                            }

            # ---------------------------------------------------------
            # Rule 2: អ្នក (Person/Title) vs នាក់ (Classifier for humans)
            # ---------------------------------------------------------
            # Move below Rule 3 but make it respectful of precise classifier decisions
            if word in ("អ្នក", "នាក់"):
                # If Rule 3 already found a more specific issue, don't overwrite it
                if i not in errors or not errors[i].get('locked'):
                    is_after_num = False
                    if prev:
                        if prev["type"] == "NUM" or prev["token"] in KHMER_NUM_WORDS or re.match(r'^[0-9០-៩]+$', prev["token"]):
                            is_after_num = True
                        elif prev["token"] in {"ប៉ុន្មាន", "ច្រើន", "ខ្លះ", "រាប់"}:
                            is_after_num = True
                    
                    if word == "អ្នក" and is_after_num:
                        errors[i] = {'original': word, 'suggestions': ["នាក់"], 'confidence': 0.95, 'error_type': 'contextual'}
                    elif word == "នាក់" and not is_after_num:
                        errors[i] = {'original': word, 'suggestions': ["អ្នក"], 'confidence': 0.90, 'error_type': 'contextual'}

            # ---------------------------------------------------------
            # Rule 4: Terminal Punctuation (Khan vs Ko-mut)
            # ---------------------------------------------------------
            if word == "៕":
                # Ko-mut (៕) should only be at the very end of document.
                # Check if there's any content (WORD/NUM) after this.
                has_content_after = False
                for k in range(i + 1, len(tagged)):
                    if tagged[k]["type"] in ("WORD", "NUM"):
                        has_content_after = True
                        break
                if has_content_after:
                    errors[i] = {
                        'original': word,
                        'suggestions': ["។"],
                        'confidence': 0.85,
                        'error_type': 'spelling'
                    }

            # ---------------------------------------------------------
            # Rule 5: Honorific Logic (Status Consistency)
            # ---------------------------------------------------------
            
            # 1. Define Levels
            # Level 1: General/Self. Level 2: Polite. Level 3: Monk. Level 4: Royal.
            # (All honorific dictionaries are defined outside the loop)
            # (Sentence status update moved to earlier in loop)


            # If word is a known Status Verb
            if word in VERB_LEVELS:
                verb_level = VERB_LEVELS[word]

                
                # Look back for Subject (Noun/Pronoun)
                subj_word = None
                subj_level = -1
                
                # Scan backwards limited window
                k = i - 1
                word_count = 0
                while k >= 0 and word_count < 10:
                    tok_prev = tagged[k]
                    if tok_prev["type"] == "WORD":
                        # SKIP CLASSIFIERS
                        is_cl = False
                        if tok_prev["token"] in CLASSIFIERS or tok_prev["token"] == "អ្នក":
                            if k > 0 and (tagged[k-1]["type"] == "NUM" or tagged[k-1]["token"] in KHMER_NUM_WORDS):
                                is_cl = True
                        
                        if not is_cl:
                            word_count += 1
                            norm_tok_prev = tok_prev["token"].replace("\u17d2\u178a", "\u17d2\u178f")
                            # Check for exact or substring match in SUBJECT_LEVELS
                            for title, level in SUBJECT_LEVELS.items():
                                norm_title = title.replace("\u17d2\u178a", "\u17d2\u178f")
                                if norm_title in norm_tok_prev:
                                    subj_word = tok_prev["token"]
                                    if level > subj_level:
                                        subj_level = level
                            
                            if k > 0:
                                combined = (tagged[k-1]["token"] + tok_prev["token"]).replace("\u17d2\u178a", "\u17d2\u178f")
                                for title, level in SUBJECT_LEVELS.items():
                                    norm_title = title.replace("\u17d2\u178a", "\u17d2\u178f")
                                    if norm_title in combined:
                                        subj_word = combined
                                        if level > subj_level:
                                            subj_level = level
                            
                            if subj_level > 1:
                                break
                    if tok_prev["type"] == "PUNCT" and tok_prev["token"] in ("។", "៕", "?"):
                        break
                    k -= 1
                
                # Pronoun Inheritance: If subject found is a neutral pronoun, use inherited status
                NEUTRAL_PRONOUNS = {"គាត់", "គេ", "យើង", "វា", "លោក"}
                if subj_word and any(p in subj_word for p in NEUTRAL_PRONOUNS):
                     # Check current sentence first, then fallback to previous sentence
                     if current_sentence_status > subj_level:
                         subj_level = current_sentence_status
                     elif prev_sentence_status > subj_level:
                         subj_level = prev_sentence_status
                
                # Check for explicit title substring if still Level 1
                if subj_level == 1 and subj_word:
                    for title, level in SUBJECT_LEVELS.items():
                        if title in subj_word and level > subj_level:
                            subj_level = level
                
                # If still no subject level found, look ahead a bit (e.g. "ប្រគេន ចង្ហាន់ ដល់ ព្រះសង្ឃ")
                if subj_level == -1:
                     lookahead_level = 1
                     m = i + 1
                     w_seen = 0
                     while m < len(tagged) and w_seen < 5:
                          if tagged[m]["type"] == "WORD":
                               w_seen += 1
                               for title, level in SUBJECT_LEVELS.items():
                                    if title in tagged[m]["token"]:
                                         if level > lookahead_level: lookahead_level = level
                          if tagged[m]["token"] in ("។", "៕", "?"): break
                          m += 1
                     if lookahead_level > 1:
                          # This is more of a 'target' level for the action
                          pass 

                if subj_level != -1:
                    # Rule: Status Mismatch (Underuse or Overuse)
                    is_mm = False
                    if subj_level > verb_level:
                        is_mm = True
                    elif subj_level < 3 and verb_level >= 3:
                        is_mm = True
                    
                    if is_mm:
                        action = VERB_TO_ACTION.get(word)
                        if action:
                            correct_verb = VERB_CORRECTIONS[action].get(subj_level)
                            if correct_verb and correct_verb != word:
                                # Special Case: If this is an auxiliary direction verb (ទៅ/មក) 
                                # following a main verb of the SAME action, ignore it.
                                # Example: "យាងទៅ" - យាង (4), ទៅ (1). Both are WALK. 
                                is_aux = False
                                if i > 0:
                                     prev_w = tagged[i-1]["token"]
                                     if prev_w in VERB_TO_ACTION and VERB_TO_ACTION[prev_w] == action:
                                          if VERB_LEVELS.get(prev_w, 0) >= subj_level:
                                               is_aux = True
                                if not is_aux:
                                    # Rule 3a: Exception for PREPOSITIONS starting with WALK verbs
                                    # e.g. "ទៅកាន់" (to/towards) is stable. 
                                    if word == "ទៅ" and i + 1 < len(tagged) and tagged[i+1]["token"] == "កាន់":
                                         is_aux = True
                                    
                                    if not is_aux:
                                        # Rule 3b: Selective Giving (Respectful Directionality)
                                        # If Action is GIVE and Subject is Low, check if Object/Recipient is High.
                                        # "ខ្ញុំ ប្រគេន ដល់ ព្រះសង្ឃ" -> Subject(1) + Verb(3) + Recipient(3) = OK.
                                        skip_giving_error = False
                                        if action == "GIVE":
                                             # Case A: Low -> High (Respectful Giving)
                                             if subj_level < verb_level:
                                                 # Look forward for a higher level noun/subject in next few WORD tokens
                                                 m = i + 1
                                                 words_seen = 0
                                                 while m < len(tagged) and words_seen < 5:
                                                      tok_next = tagged[m]
                                                      if tok_next["type"] == "WORD":
                                                           words_seen += 1
                                                           for title, level in SUBJECT_LEVELS.items():
                                                                if title in tok_next["token"] and level >= verb_level:
                                                                     skip_giving_error = True
                                                                     break
                                                           if skip_giving_error: break
                                                      if tok_next["token"] in ("។", "៕", "?"): break
                                                      m += 1
                                             
                                             # Case B: High -> Low (Monk giving to child)
                                             # If Subject is High but Verb is Low/Polite, and Recipient is Low
                                             elif subj_level >= 3 and verb_level <= 2:
                                                 # Monk/King can use 'ឱ្យ' or 'ផ្តល់' to children/commoners
                                                 # Look for a LOW level recipient
                                                 m = i + 1
                                                 words_seen = 0
                                                 while m < len(tagged) and words_seen < 5:
                                                      if tagged[m]["type"] == "WORD":
                                                           words_seen += 1
                                                           t_word = tagged[m]["token"]
                                                           # If we find a common person/pronoun
                                                           if any(low in t_word for low in ("ក្មេង", "កុមារ", "ចៅ", "វា")):
                                                                skip_giving_error = True
                                                                break
                                                      if tagged[m]["token"] in ("។", "៕", "?"): break
                                                      m += 1
                                        
                                        if not skip_giving_error:
                                            errors[i] = {
                                                'original': word,
                                                'suggestions': [correct_verb],
                                                'confidence': 0.95,
                                                'error_type': 'contextual'
                                            }

                    # Rule 3: The Humble Rule (Self-Exaltation)
                    # Subject(Self) + Verb(>1) -> Error
                    # "ខ្ញុំ" (1) + "សោយ" (4) -> Error
                    elif subj_word == "ខ្ញុំ" and verb_level > 1:
                        # Suggest Level 1 or 2 (Polite)
                        action = VERB_TO_ACTION.get(word)
                        if action:
                            correct_verb = VERB_CORRECTIONS[action].get(1) # Suggest Level 1
                            polite_verb = VERB_CORRECTIONS[action].get(2) # Or Level 2
                            sugs = []
                            if polite_verb and polite_verb != word: sugs.append(polite_verb)
                            if correct_verb and correct_verb != word: sugs.append(correct_verb)
                            
                            if sugs:
                                errors[i] = {
                                    'original': word,
                                    'suggestions': sugs,
                                    'confidence': 0.90,
                                    'suggestions': sugs,
                                    'confidence': 0.90,
                                    'error_type': 'contextual'
                                }



            # ---------------------------------------------------------
            # Rule 6: Suffix Correction (Verb vs Noun with Bantak)
            # ---------------------------------------------------------
            # Pairs: Verb (No Suffix) -> Noun (Suffix -ន៍)
            SUFFIX_PAIRS = {
                "អភិវឌ្ឍ": "អភិវឌ្ឍន៍",
                "អនុវត្ត": "អនុវត្តន៍",
                "វិវត្ត": "វិវត្តន៍",
                "អភិរក្ស": "អភិរក្សណ៍" 
            }
            # Reverse map for detecting incorrect usage of Noun form
            REV_SUFFIX_PAIRS = {v: k for k, v in SUFFIX_PAIRS.items()}

            # Context definitions
            VERB_MARKERS = {"បាន", "នឹង", "កំពុង", "ធ្លាប់", "ត្រូវ", "គួរ", "អាច", "ចេះ", "មិន", "ពុំ", 
                            "ដើម្បី", "ជួយ", "នាំគ្នា", "សាកល្បង", "ប្រឹងប្រែង", "ចូលរួម", "ចាប់ផ្តើម", "បន្ត", "ឈប់"}
            NOUN_MARKERS = {"នៃ", "ផ្នែក", "ក្រសួង", "មន្ទីរ", "ក្រុមប្រឹក្សា", "គម្រោង", "កម្មវិធី", 
                            "អ្នក", "ការងារ", "វិស័យ", "ស្ថាប័ន", "ជាតិ", "អន្តរជាតិ", "ការ"}

            if word in SUFFIX_PAIRS:  # Current word is Verb form (e.g. អភិវឌ្ឍ)
                # Check if it should be Noun form (Suffix)
                # Look backwards for Noun Marker
                should_be_noun = False
                if prev:
                    # Exception: "ការ" + Verb is a nominalized phrase (valid)
                    # e.g., "ការអភិវឌ្ឍ" = "development" (the act of developing)
                    if prev["token"] == "ការ":
                        should_be_noun = False  # This is valid, don't flag
                    elif prev["token"] in NOUN_MARKERS:
                        should_be_noun = True
                    # Check "Noun + Verb" -> usually fine ("He develops")
                    # Check "Preposition + Verb" -> fine.
                    # Only strongly enforce NOUN markers.
                
                if should_be_noun:
                    errors[i] = {
                        'original': word,
                        'suggestions': [SUFFIX_PAIRS[word]],
                        'confidence': 0.90,
                        'error_type': 'contextual'
                    }

            elif word in REV_SUFFIX_PAIRS: # Current word is Noun form (e.g. អភិវឌ្ឍន៍)
                # Check if it should be Verb form (No Suffix)
                # Look backwards for Verb Marker
                should_be_verb = False
                if prev:
                    if prev["token"] in VERB_MARKERS:
                        should_be_verb = True
                    # Check "Subject + Noun" -> "He development"? -> Wrong.
                    # If prev is Pronoun or Noun, and word is Noun form, it counts as verb usage?
                    # "We development country" -> Wrong.
                    # But "Our development" -> "development of us" (No possessive in Khmer sometimes).
                    # "Development of country" -> "អភិវឌ្ឍន៍ប្រទេស" (Noun phrase head).
                    # Ambiguous without markers.
                    # Rely on markers for high confidence.
                
                if should_be_verb:
                    errors[i] = {
                        'original': word,
                        'suggestions': [REV_SUFFIX_PAIRS[word]],
                        'confidence': 0.95,
                        'error_type': 'contextual'
                    }

            # ---------------------------------------------------------
            # Rule 7: ដែល (That/Which) vs ដែរ (Also/Too)
            # ---------------------------------------------------------
            if word == "ដែល":
                # Check 1: End of sentence or Punctuation -> Likely "ដែរ"
                # Skip whitespace to find next meaningful token
                k = i + 1
                next_tok = None
                while k < len(tagged):
                    if tagged[k]["type"] != "OTHER":
                        next_tok = tagged[k]
                        break
                    k += 1

                if not next_tok or next_tok["token"] in ("។", "៕", "?", "!", "៖", "\n"):
                     errors[i] = {
                        'original': word,
                        'suggestions': ["ដែរ"],
                        'confidence': 0.95,
                        'error_type': 'contextual'
                    }

            elif word == "ដែរ":
                # Check 2: Relative Clause Usage (Noun + ដែរ + Verb/Adj) -> Should be ដែល
                if prev and i + 1 < len(tagged):
                    prev_tok = prev["token"]
                    
                    # 1. Negative Check: "មិន...ដែរ" -> Correct
                    is_neg = prev_tok in ("មិន", "ពុំ", "អត់")
                    
                    # 2. "Also" particle check: "Subject + ក៏ + Verb + ដែរ" -> Correct
                    # If "ក៏" appearing 1-3 tokens back?
                    has_kor = False
                    back_k = i - 1
                    while back_k >= max(0, i - 3):
                         if tagged[back_k]["token"] == "ក៏":
                             has_kor = True
                             break
                         back_k -= 1
                    
                    if not is_neg and not has_kor:
                        # If followed by a Verb/Adjective/Pronoun (Clause starter)
                        if tagged[i+1]["type"] == "WORD" and tagged[i+1]["token"] not in ("?", "!", "។"):
                             # Likely "Which/That"
                             errors[i] = {
                                'original': word,
                                'suggestions': ["ដែល"],
                                'confidence': 0.85,
                                'error_type': 'contextual'
                            }

            # ---------------------------------------------------------
            # Rule 8: ដ៏ (Adjective Marker) vs ដល់ (To/Arrive)
            # ---------------------------------------------------------
            if word == "ដ៏":
                 # If followed by Location/Time -> Likely "ដល់"
                 if i + 1 < len(tagged):
                     next_tok = tagged[i+1]["token"]
                     # Check if it IS a location word or STARTS with one (e.g. ផ្ទះបាយ)
                     if next_tok in LOC_TIME_WORDS or any(next_tok.startswith(loc) for loc in LOC_TIME_WORDS):
                         errors[i] = {
                            'original': word,
                            'suggestions': ["ដល់"],
                            'confidence': 0.99,
                            'error_type': 'contextual'
                        }
            
            # --- Rule 8 Reverse: ដល់ (To/Arrive) vs ដ៏ (Adjective Marker) ---
            # Example: ស្អាត ដល់ អស្ចារ្យ -> ស្អាត ដ៏ អស្ចារ្យ
            elif word == "ដល់":
                next_idx = i + 1
                while next_idx < len(tagged) and tagged[next_idx]["type"] == "OTHER":
                    next_idx += 1
                if next_idx < len(tagged):
                     # If next is Adjective, suggest ដ៏
                     # Exclude if next is also a Noun/Location? "ដល់ ផ្ទះ" (Arrive Home) -> OK.
                     # "ដ៏ ផ្ទះ" -> Wrong.
                     # Adjectives: ស្អាត, ល្អ, ធំ, តូច, វិសេស, ថ្លៃថ្លា
                     next_pos = tagged[next_idx].get("pos", set())
                     next_tok = tagged[next_idx]["token"]
                     
                     if "ADJ" in next_pos and "N" not in next_pos:
                         errors[i] = {
                            'original': word,
                            'suggestions': ["ដ៏"],
                            'confidence': 0.95,
                            'error_type': 'contextual'
                        }
                     elif next_tok in {"អស្ចារ្យ", "វិសេស", "ឧត្តម"}:
                          errors[i] = {
                            'original': word,
                            'suggestions': ["ដ៏"],
                            'confidence': 0.99,
                            'error_type': 'contextual'
                        }
            
            # ---------------------------------------------------------
            # Rule 9: នៃ (Of) vs ន័យ (Meaning)
            # ---------------------------------------------------------
            if word == "នៃ":
                # "មាននៃថា" -> "មានន័យថា"
                if prev and prev["token"] == "មាន":
                     errors[i] = {
                        'original': word,
                        'suggestions': ["ន័យ"],
                        'confidence': 0.99,
                        'error_type': 'spelling'
                    }
            elif word == "ន័យ":
                # "ការន័យ" -> "ការនៃ" (The development of...)
                # "ផ្នែកន័យ" -> "ផ្នែកនៃ"
                # Added: អភិវឌ្ឍ, សង្គម, ជាតិ, គម្រោង
                if prev and (prev["token"] in ("ការ", "ផ្នែក", "សេចក្តី", "ភាព", "ដំណើរ", "ផល", "អភិវឌ្ឍ", "សង្គម", "ជាតិ", "គម្រោង", "កម្មវិធី", "ឯកសារ", "គោលបំណង", "បញ្ហា", "សមិទ្ធផល", "លទ្ធផល") or 
                             prev["token"].startswith("ការ")):
                     errors[i] = {
                        'original': word,
                        'suggestions': ["នៃ"],
                        'confidence': 0.95,
                        'error_type': 'contextual'
                    }

            # ---------------------------------------------------------
            # Rule 6: Impossible Combinations (Diacritic Logic)
            # ---------------------------------------------------------
            # Check 1: Series B Consonant + Muusikatont (៊) -> Error
            # Check 2: Series A Consonant + Treisap (៉) -> Error (Except 'ប')
            
            SERIES_A = set("កខចឆដឋណតថបសហឡអ")
            SERIES_B = set("គឃងជឈញឌឍទធនពភមយរលវ") # Note: ង, ញ, ម, យ, រ, ល, វ can take Treisap to become A-series sound (e.g. ង៉). But they are distinct.
            
            # We need to check character pairs within the word
            if len(word) > 1:
                # Muusikatont Check (៊ / U+17CA)
                if '៊' in word:
                    for idx, char in enumerate(word):
                        if char == '៊' and idx > 0:
                            prev_char = word[idx-1]
                            if prev_char in SERIES_B:
                                errors[i] = {
                                    'original': word,
                                    'suggestions': [word.replace('៊', '')], # Suggest removing the mark
                                    'confidence': 0.99,
                                    'error_type': 'spelling'
                                    # 'description': "Series B consonants cannot take Muusikatont (៊)."
                                }
                                break

                # Treisap Check (៉ / U+17C9)
                if '៉' in word:
                    for idx, char in enumerate(word):
                        if char == '៉' and idx > 0:
                            prev_char = word[idx-1]
                            # Exception: 'ប' uses Treisap to become 'ប៉' (Hard P)
                            if prev_char in SERIES_A and prev_char != 'ប':
                                errors[i] = {
                                    'original': word,
                                    'suggestions': [word.replace('៉', '')], # Suggest removing the mark
                                    'confidence': 0.99,
                                    # 'description': "Series A consonants cannot take Treisap (៉)."
                                }
                                break

            # ---------------------------------------------------------
            # Rule 7: Chak-ka-veala (Khmer Colon ៖)
            # ---------------------------------------------------------
            # Rule: Must NOT be at end of document. Must be followed by list/text.
            if word == "៖":
                # Check directly if next token exists
                has_next = False
                for k in range(i + 1, len(tagged)):
                    if tagged[k]["type"] in ("WORD", "NUM"):
                        has_next = True
                        break
                if not has_next:
                     errors[i] = {
                        'original': word,
                        'suggestions': ["។"], # Suggest Khan instead if ending?
                        'confidence': 0.80,
                        'error_type': 'spelling'
                    }

            # ---------------------------------------------------------
            # Rule 8: Bantak (់) Logic
            # ---------------------------------------------------------
            # Rule: It can only be placed on the final consonant of a syllable.
            # Logic: Scan all characters. If ់ is followed by a Consonant, it's an error.
            # Exception: If word is in dictionary, assume it's a valid compound (e.g. បាត់បង់).
            if '់' in word and not t.get("in_dict", False):
                CONSONANTS = SERIES_A.union(SERIES_B)
                for c_idx, char in enumerate(word):
                    if char == '់':
                        # Check next char
                        if c_idx < len(word) - 1:
                            char_after = word[c_idx + 1]
                            if char_after in CONSONANTS:
                                errors[i] = {
                                    'original': word,
                                    'suggestions': [],
                                    'confidence': 0.70,
                                    'error_type': 'spelling'
                                }
                                # Suggest no space
                                # split_sug = word[:c_idx+1] + " " + word[c_idx+1:]
                                # We'll just suggest the compound without flagging if it might be valid?
                                # For now, don't suggest a space.
                                pass
                                break # Found one error in word, usually enough to flag


            # ---------------------------------------------------------
            # Rule 10 & 9: Punctuation Spacing and Question/Statement Logic
            # ---------------------------------------------------------
            PUNCT_SYMBOLS = {"។", "៕", "៖", "!", "?", "ៗ"}
            if word in PUNCT_SYMBOLS:
                pos = token_offsets[i]
                if pos != -1:
                    # Search version of word (reverting normalize)
                    search_word = word.replace("\u17be", "\u17c1\u17b8")
                    
                    # --- Rule 10: Spacing ---
                    # 1. Check for missing space after punctuation
                    # Exception: ៗ (repetition mark) doesn't need space after it
                    if word != "ៗ" and pos + len(search_word) < len(text):
                        char_after = text[pos + len(search_word)]
                        if not char_after.isspace() and char_after not in PUNCT_SYMBOLS and char_after not in {")", "]", "»", "", '"'}:
                             if i not in errors:
                                 errors[i] = {
                                     'original': word,
                                     'suggestions': [word + " "],

                                     'confidence': 0.85,
                                     'error_type': 'contextual'
                                 }

                    # 2. Check for extra space before
                    if pos > 0:
                        k = pos - 1
                        while k >= 0 and text[k].isspace():
                            k -= 1
                        num_spaces = pos - 1 - k
                        if num_spaces > 0 and word not in {"(", "[", "«"}:
                             if i not in errors: 
                                 errors[i] = {
                                     'original': text[k+1:pos] + word,
                                     'suggestions': [word],
                                     'confidence': 0.85,
                                     'error_type': 'contextual',
                                     'offset_override': k + 1
                                 }

                # --- Rule 9: Question vs Statement ---
                if word in {"។", "៕", "?"}:
                    last_punct_token = word
                    
                    # Identify First Word of current sentence
                    first_word = ""
                    for k in range(sentence_start_idx, i + 1):
                        if tagged[k]["type"] in ("WORD", "NUM"):
                            first_word = tagged[k]["token"]
                            break
                    
                    # Identify Last Word of current sentence
                    last_word = ""
                    if last_sentence_content_idx > -1:
                        last_word = tagged[last_sentence_content_idx]["token"]

                    # Determine if it's a question
                    is_question = False
                    QUESTION_STARTERS = {"តើ", "ហេតុអ្វី", "ម្តេច", "តាំងពីអង្កាល់", "ចូរ"}
                    if first_word in QUESTION_STARTERS:
                        is_question = True

                    QUESTION_PARTICLES = {"មែនទេ", "ឬ", "ដែរឬទេ", "ណា", "អត់", "រួច", "នៅ"}
                    has_negation = False
                    if last_word == "ទេ":
                        # Check for negation in current sentence scope - Scan full sentence to be safe
                        for j in range(sentence_start_idx, last_sentence_content_idx):
                            if tagged[j]["token"] in {"មិន", "គ្មាន", "ពុំ", "មិនបាន", "មិនមែន", "ពុំមែន", "អត់"}:
                                has_negation = True
                                break
                        if not has_negation:
                            is_question = True
                    
                    if not is_question and last_word in QUESTION_PARTICLES:
                        # "រួច" and "នៅ" are only particles if not used as verbs/preps or if question starter present
                        if last_word in {"រួច", "នៅ"}:
                            if first_word in QUESTION_STARTERS:
                                is_question = True
                        else:
                            is_question = True
                    
                    INTERROGATIVES = {"អ្វី", "ណា", "ប៉ុន្មាន", "ម៉េច", "ទេ", "មែនទេ"}
                    if not is_question and last_word in INTERROGATIVES:
                        # Only mark as question if not a clear statement negation
                        if last_word == "ទេ" and not has_negation:
                             is_question = True
                        elif last_word != "ទេ":
                             is_question = True

                    # Apply Question/Statement suggestions
                    if last_punct_token == "។" and is_question:
                        # Existing Rule 10 suggestion might exist, decide priority? 
                        # Usually punctuation type is more important than spacing.
                        if i not in errors or errors[i]['error_type'] == 'contextual':
                             errors[i] = {'original': word, 'suggestions': [word.replace("។", "?")], 'confidence': 0.90, 'error_type': 'contextual'}
                    elif last_punct_token == "?" and not is_question:
                        if last_word == "ទេ" and has_negation:
                             errors[i] = {'original': "?", 'suggestions': ["។"], 'confidence': 0.95, 'error_type': 'contextual'}
                        elif first_word not in QUESTION_STARTERS and last_word not in QUESTION_PARTICLES and last_word not in INTERROGATIVES:
                             errors[i] = {'original': "?", 'suggestions': ["។"], 'confidence': 0.85, 'error_type': 'contextual'}
                    
                    # Update sentence start for next sentence
                    sentence_start_idx = i + 1
                    last_sentence_content_idx = -1



        # Suggestions for single-token errors

        for idx in error_indices:
            if idx in errors:
                continue
            
            error_word = tagged[idx]["token"]
            candidates = generate_candidates(error_word)

            if candidates:
                reranked = rerank_candidates(candidates, tagged, idx, word_to_pos,
                                            word_freq_ipm, max_ipm)
                top_suggestions = [c["word"] for c in reranked[:5]]
                top_score = reranked[0]["final_score"] if reranked else 0.0
            else:
                top_suggestions = []
                top_score = 0.0

            errors[idx] = {
                'original': error_word,
                'suggestions': top_suggestions,
                'confidence': top_score,
                'error_type': 'spelling'
            }

        # Detect boundary errors by concatenating adjacent unknown tokens
        for i in range(len(tagged) - 1):

            
            t1, t2 = tagged[i], tagged[i + 1]
            if t1['type'] == 'WORD' and t2['type'] == 'WORD' and (not t1['in_dict']) and (not t2['in_dict']):
                concat_candidates = generate_concat_candidates(t1['token'], t2['token'])
                if concat_candidates:
                    # Favor concat corrections; rerank in context of i (left token)
                    reranked = rerank_candidates(concat_candidates, tagged, i, word_to_pos, word_freq_ipm, max_ipm)
                    top_suggestions = [c['word'] for c in reranked[:5]]
                    top_score = reranked[0]['final_score'] if reranked else 0.0
                    # If single-token error already exists, merge suggestions
                    orig = t1['token'] + t2['token']
                    prev = errors.get(i)
                    if prev:
                        # Merge unique suggestions and keep best confidence
                        merged_sugs = list(dict.fromkeys(prev['suggestions'] + top_suggestions))
                        errors[i] = {
                            'original': orig,
                            'suggestions': merged_sugs,
                            'confidence': max(prev['confidence'], top_score),
                            'error_type': 'spelling'
                        }
                    else:
                        errors[i] = {
                            'original': orig,
                            'suggestions': top_suggestions,
                            'confidence': top_score,
                            'error_type': 'spelling'
                        }

        # Final Whitelist Filtering to suppress known false positives
        final_errors = {}
        for idx, err in errors.items():
            # Check if entire original string is whitelisted
            o_str = err.get("original", "").strip()
            if not o_str: continue # Skip empty
            
            # Only apply whitelist to 'spelling' errors (unknown words).
            # Do NOT apply to 'contextual' or 'grammar' errors where a valid word is used wrongly.
            if err.get('error_type') == 'spelling':
                if o_str in WHITELIST_WORDS: continue
                # Check components (for split errors)
                parts = o_str.split()
                if parts and all(p.strip() in WHITELIST_WORDS for p in parts): continue
                # Check normalized/stripped versions
                if o_str.replace(" ", "") in WHITELIST_WORDS: continue
            elif err.get('error_type') == 'contextual':
                # Special Case: 'ស្រូវ' often flagged as 'ត្រូវ'
                if o_str == "ស្រូវ": continue
                # Special Case: 'តម្រូវ' flagged as 'ត្រូវ'
                if o_str == "តម្រូវ": continue
            
            final_errors[idx] = err
        errors = final_errors

        # Final Self-Correction Filter
        keys_to_remove = []
        for idx, err in errors.items():
            suggs = err.get('suggestions', [])
            original = err.get('original', '')
            if suggs and suggs[0] == original:
                keys_to_remove.append(idx)
        
        for k in keys_to_remove:
            del errors[k]

        return {
            'success': True,
            'tokens': tokens,
            'token_offsets': token_offsets,
            'errors': errors
        }

    except Exception as e:
        print(f"CRITICAL ERROR in check_spelling: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e),
            'tokens': [],
            'errors': {}
        }


if __name__ == "__main__":
    # Test the spell checker
    test_text = "សូមស្វាគមន៍ទៅក្រម Khmer spelling checker"
    result = check_spelling(test_text)
    print(json.dumps(result, ensure_ascii=False, indent=2))

def warmup():
    """Warm up the spell checker by loading data and pre-calculating tables"""
    print("Warming up spell checker...")
    SpellCheckerData.build_tables()
    SpellCheckerData.get_words_by_start()
    SpellCheckerData.load_semantic_map()
    # Trigger lru_cache for some common words
    for w in ["ខ្ញុំ", "អ្នក", "និង", "ដែល"]:
        is_known(w)
    print("Spell checker warmed up.")