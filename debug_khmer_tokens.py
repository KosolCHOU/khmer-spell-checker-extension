from keyez.landing.spell_checker_advanced import SpellCheckerData, segment_text, pos_tag_tokens, classify_token

def debug():
    SpellCheckerData.build_tables()
    text = "ស្ដេច ដើរ ទៅ លេង សួន ។"
    word_set, word_to_pos, word_freq_ipm, max_ipm = SpellCheckerData.build_tables()
    words_by_start = SpellCheckerData.get_words_by_start()
    
    tokens = segment_text(text, word_set, word_freq_ipm, words_by_start, lambda x: True)
    print(f"Tokens: {tokens}")
    for t in tokens:
        print(f"Token: '{t}' Type: {classify_token(t)}")
    
    tagged = pos_tag_tokens(tokens, word_to_pos, word_set)
    for t in tagged:
        print(f"Tagged: {t}")

if __name__ == "__main__":
    debug()
