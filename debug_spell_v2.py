
from keyez.landing.spell_checker_advanced import SpellCheckerData, segment_text, pos_tag_tokens, detect_grammar_errors

def debug_v2():
    SpellCheckerData.build_tables()
    word_set, word_to_pos, word_freq, _ = SpellCheckerData.build_tables()
    
    # Check 'ដាក់ចេញ' in Whitelist
    from keyez.landing.spell_checker_advanced import WHITELIST_WORDS
    print(f"'ដាក់ចេញ' in WHITELIST: {'ដាក់ចេញ' in WHITELIST_WORDS}")
    
    # Trace Case 3
    text2 = "យើងត្រូវតែរួមគ្នាថែរក្សានៅសម្បត្តិវប្បធម៌"
    tokens2 = segment_text(text2)
    print(f"Tokens Case 3: {tokens2}")
    
    tagged2 = pos_tag_tokens(tuple(tokens2), word_to_pos, word_set)
    
    # Check 'ថែរក្សា'
    for t in tagged2:
        print(f"Token: {t['token']}, InDict: {t['in_dict']}, POS: {t['pos']}")
        
    errors = {}
    detect_grammar_errors(tagged2, errors)
    print(f"Errors: {errors}")

if __name__ == "__main__":
    debug_v2()
