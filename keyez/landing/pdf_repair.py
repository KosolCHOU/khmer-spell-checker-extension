from .spell_checker_advanced import segment_text, SpellCheckerData

def repair_khmer_text(text: str) -> str:
    """
    Repairs common PDF extraction errors in Khmer text.
    Specific focus: 'េ' (E) typically misread as '្រ' (Coeng + Ro).
    """
    if not text:
        return text

    # Step 0: Apply Force Repairs for known high-frequency PDF artifacts
    # These are safe, context-independent fixes for this specific encoding issue.
    FORCE_REPAIRS = {
        'យ្រីង': 'យើង',   # We
        'ច្រ្រីន': 'ច្រើន', # Many
        'ន្រះ': 'នេះ',    # This
        'ក្រ្រយ': 'ក្រោយ', # Behind/After
        'ល្រីក': 'លើក',   # Lift/Raise
        'កេេយ': 'ក្រោយ',  # Variation
        'ចេេីន': 'ច្រើន',  # Variation
    }
    for bad, good in FORCE_REPAIRS.items():
        text = text.replace(bad, good)

    # Step 1: Segment text to handle sentence-level inputs correctly
    words = segment_text(text)
    repaired_words = []
    
    corrections = {}
    
    word_set, _, _, _ = SpellCheckerData.build_tables()
    
    for word in words:

        # Check if word contains the problematic sequence '្រ' (\u17d2\u179a)
        if '\u17d2\u179a' in word:
            if word in corrections:
                repaired_words.append(corrections[word])
                continue

            # Check validity
            valid_original = word in word_set

            
            # Generate candidate: Replace ALL '្រ' with 'េ'
            # Note: This is a simplification. Sometimes a word has valid AND invalid '្រ'.
            # But usually PDF extraction error affects the whole font/glyph mapping.
            candidate = word.replace('\u17d2\u179a', '\u17c1')
            valid_candidate = candidate in word_set

            
            should_replace = False
            
            if valid_candidate:
                if not valid_original:
                    # Clear winner: Original Invalid, Candidate Valid -> Repair
                    print(f"DEBUG: REPAIRING '{word}' -> '{candidate}'")
                    should_replace = True
                else:
                    # Ambiguous: Both Valid. 
                    # Prioritize repair only if we are confident (e.g. known common error)
                    # OR if we assume PDF extraction is likely faulty on these characters.
                    # As per recent fix, we prioritize the candidate to fix 'េ' issues.
                    print(f"DEBUG: REPAIRING AMBIGUOUS '{word}' -> '{candidate}' (Assume extraction error)")
                    should_replace = True
            
            if should_replace:
                corrections[word] = candidate
                repaired_words.append(candidate)
            else:
                corrections[word] = word
                repaired_words.append(word)
        else:
            repaired_words.append(word)
            
    # Join words. 
    # Since Khmer has no spaces, we can join with empty string.
    # However, segmentation might have stripped spaces if they existed. 
    # But usually segmentation consumes the string.
    # A safer join checking if original had spaces might be too complex.
    # For now, join with empty string is standard for Khmer.
    # BUT, if the original text had spaces (e.g. English mix), this breaks.
    # Ideally we should tokenize preserving whitespace?
    # Our `segment_text` implementation splits by `|` and strips. 
    # Let's assume standard Khmer text for now.
    
    return "".join(repaired_words)

