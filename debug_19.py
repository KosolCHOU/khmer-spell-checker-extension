
import sys
import time
from typing import List, Dict

# Import the spell checker module
from keyez.landing.spell_checker_advanced import (
    SpellCheckerData, 
    segment_text, 
    pos_tag_tokens, 
    detect_grammar_errors, 
    detect_error_slots,
    detect_semantic_suspicion
)

def run_debug_19():
    word_set, word_to_pos, word_freq, _ = SpellCheckerData.build_tables()
    word_list = SpellCheckerData.get_word_list()
    bigrams = SpellCheckerData.load_bigrams()
    
    text = "កុមារត្រូវរៀនសូត្រពីកតញ្ញនិងការគោរពចាស់ទុំម"
    expected = ["កតញ្ញ", "ចាស់ទុំម"]
    
    tokens = segment_text(text)
    tagged = pos_tag_tokens(tuple(tokens), word_to_pos, word_set)
    errors = {}
    error_indices = detect_error_slots(tagged, word_set, word_list, bigrams, {}, errors, word_freq)
    detect_grammar_errors(tagged, errors)
    
    detected_tokens = []
    for idx in errors:
        detected_tokens.append(errors[idx]['original'])
    for idx in error_indices:
        token_text = tagged[idx]['token']
        if token_text not in detected_tokens:
            detected_tokens.append(token_text)
            
    detected_set = set(detected_tokens)
    print(f"Tokens: {tokens}")
    print(f"Detected Set: {detected_set}")
    print(f"Errors Dict Keys: {list(errors.keys())}")
    
    found_expected = [e for e in expected if e in detected_set or any(e in d for d in detected_set)]
    print(f"Found Expected: {found_expected}")

if __name__ == "__main__":
    run_debug_19()
