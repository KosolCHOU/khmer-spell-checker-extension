
from keyez.landing.spell_checker_advanced import SpellCheckerData, segment_text, pos_tag_tokens, detect_grammar_errors, is_strict_word, detect_semantic_suspicion

def debug_issue():
    SpellCheckerData.build_tables()
    word_set, word_to_pos, word_freq, _ = SpellCheckerData.build_tables()
    
    # Debug 1: "ដាក់ចេញ"
    word = "ដាក់ចេញ"
    print(f"Checking '{word}':")
    print(f"  In word_set: {word in word_set}")
    print(f"  is_strict_word: {is_strict_word(word)}")
    
    text1 = "រដ្ឋាភិបាលបានដាក់ចេញនូវ"
    tokens1 = segment_text(text1)
    print(f"  Tokens: {tokens1}")
    tagged1 = pos_tag_tokens(tuple(tokens1), word_to_pos, word_set)
    for t in tagged1:
        if t['token'] == "ដាក់ចេញ":
            print(f"  Tagged 'ដាក់ចេញ': in_dict={t['in_dict']}")

    # Debug 2: "ថែរក្សា នៅ"
    text2 = "យើងត្រូវតែរួមគ្នាថែរក្សានៅសម្បត្តិវប្បធម៌"
    print(f"\nChecking Case 3: '{text2}'")
    tokens2 = segment_text(text2)
    print(f"  Tokens: {tokens2}")
    tagged2 = pos_tag_tokens(tuple(tokens2), word_to_pos, word_set)
    
    errors = {}
    detect_grammar_errors(tagged2, errors)
    print(f"  Errors detected: {errors}")
    
    # Check POS of "សម្បត្តិ"
    for t in tagged2:
        if t['token'] == "សម្បត្តិ":
            print(f"  'សម្បត្តិ' POS: {t['pos']}")
        if t['token'] == "ថែរក្សា":
            print(f"  'ថែរក្សា' POS: {t['pos']}")

if __name__ == "__main__":
    debug_issue()
