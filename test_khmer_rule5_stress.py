from keyez.landing.spell_checker_advanced import check_spelling

def test_rule_5_stress():
    """
    Stress test for Rule 5 (Honorific Logic) and Rule 6 (Suffix Correction)
    """
    
    test_cases = [
        # --- Basic Honorific Mismatches ---
        ("ខ្ញុំ សោយ បាយ ។", True, "Self-exaltation: I + royal verb"),
        ("ស្ដេច ញ៉ាំ បាយ ។", True, "King + common verb"),
        ("ព្រះសង្ឃ ហូប បាយ ។", True, "Monk + common verb"),
        ("លោក ឆាន់ ទឹក ។", True, "Polite person + monk verb"),
        
        # --- Correct Usage ---
        ("ខ្ញុំ ញ៉ាំ បាយ ។", False, "Correct: I + common verb"),
        ("ស្ដេច សោយ បាយ ។", False, "Correct: King + royal verb"),
        ("ព្រះសង្ឃ ឆាន់ ទឹក ។", False, "Correct: Monk + monk verb"),
        ("លោក ពិសា បាយ ។", False, "Correct: Polite + polite verb"),
        
        # --- Pronoun Inheritance (Same Sentence) ---
        ("ស្ដេច ទៅ ។ គាត់ ញ៉ាំ បាយ ។", True, "King -> pronoun (should inherit)"),
        ("ព្រះសង្ឃ ទៅ ។ គាត់ ហូប បាយ ។", True, "Monk -> pronoun (should inherit)"),
        ("លោកតា សឹង ហើយ ។ គាត់ ជើង ឈឺ ។", True, "Monk inheritance (his leg - though noun honorifics might miss)"),
        
        # --- Neutral Pronouns ---
        ("គាត់ ញ៉ាំ បាយ ។", False, "Neutral pronoun (no context)"),
        ("យើង ញ៉ាំ បាយ ។", False, "Neutral pronoun (no context)"),
        
        # --- Verb Mismatch (Level Jumping) ---
        ("លោក សោយ បាយ ។", True, "Polite (L2) + Royal verb (L4)"),
        ("ព្រះសង្ឃ សោយ បាយ ។", True, "Monk (L3) + Royal verb (L4)"),
        ("ស្ដេច ឆាន់ ទឹក ។", True, "King (L4) + Monk verb (L3)"),
        
        # --- Noun Honorifics ---
        ("ស្ដេច ចូល ក្នុង ផ្ទះ ។", True, "King in common house"),
        ("ព្រះសង្ឃ ចូល ក្នុង ផ្ទះ ។", True, "Monk in common house"),
        ("ព្រះនាង ក្បាល ឈឺ ។", True, "Princess head (common)"),
        ("លោក ចិត្ត ល្អ ។", False, "Polite person + common noun (OK)"),
        
        # --- Verb Mismatch (Underuse) ---
        ("ស្ដេច ដេក ។", True, "King + common sleep"),
        ("ព្រះសង្ឃ ដើរ ។", True, "Monk + common walk"),
        ("លោក ហូប បាយ ។", True, "Polite + common eat"),
        
        # --- Verb Mismatch (Overuse) ---
        ("ខ្ញុំ សោយ បាយ ។", True, "I + royal eat"),
        ("គាត់ ផ្ទុំ ។", True, "He + royal sleep (no context)"),
        ("កុមារ យាង ទៅ ។", True, "Child + royal walk"),
        
        # --- Auxiliary Verbs (Should NOT flag) ---
        ("ស្ដេច យាង ទៅ ផ្សារ ។", False, "Royal walk + direction (auxiliary)"),
        ("ព្រះសង្ឃ និមន្ត ទៅ វត្ត ។", False, "Monk walk + direction (auxiliary)"),
        
        # --- Prepositional Phrases ---
        ("លោកស្រី មាន ប្រសាសន៍ ទៅកាន់ បុគ្គលិក ។", False, "Polite speak + prepositional phrase"),
        
        # --- Humble Rule (Self-Exaltation) ---
        ("ខ្ញុំ សោយ បាយ ។", True, "I + royal verb"),
        ("ខ្ញុំ ផ្ទុំ ។", True, "I + royal sleep"),
        ("ខ្ញុំ យាង ទៅ ។", True, "I + royal walk"),
        
        # --- Monk/King Verb Mismatch ---
        ("លោកតា ចង់ សោយ ទឹក ។", True, "Monk (L3) eating royal (L4) - mismatch"),
        ("ស្ដេច ចង់ ឆាន់ ទឹក ។", True, "King (L4) eating monk (L3) - mismatch"),
        
        # --- Cross-Sentence Inheritance ---
        ("ស្ដេច ទៅ ផ្សារ ។ គាត់ ញ៉ាំ បាយ ។", True, "King inheritance (common verb)"),
        ("ព្រះសង្ឃ លោក និមន្ត ទៅ ។ គាត់ ហូប បាយ ។", True, "Monk inheritance across sentence (verb)"),
        ("លោកតា និមន្ត ទៅ ។ គាត់ ជើង ឈឺ ។", True, "Monk inheritance across sentence (noun)"),
        
        # --- Give Directionality (Respectful Giving) ---
        ("ខ្ញុំ ប្រគេន ចង្ហាន់ ដល់ ព្រះសង្ឃ ។", False, "Correct: Humble person giving to monk"),
        ("ខ្ញុំ ថ្វាយ ផ្កា ដល់ ស្ដេច ។", False, "Correct: Humble person giving to King"),
        ("ព្រះសង្ឃ ឱ្យ លុយ ក្មេង ។", False, "Correct: Monk giving to child (might need 'ផ្តល់')"),
        
        # --- Compound Subjects & Substrings ---
        ("សម្តេច ព្រះអង្គ ហូប បាយ ។", True, "Compound royal subject"),
        ("ឯកឧត្តម លោក ជំទាវ អញ្ជើញ ហូប បាយ ។", True, "Multiple guests eating common"),
        
        # --- More Noun Honorifics ---
        ("ស្ដេច ឈឺ ដៃ ។", True, "King's hand (L4)"),
        ("ព្រះសង្ឃ ឈឺ ក្បាល ។", True, "Monk's head (L3)"),
        ("ព្រះអង្គ ចង់ ទិញ ផ្ទះ ។", True, "King wants house (L4)"),
    ]
    
    print("=" * 100)
    print(f"{'KHMER SPELL CHECKER - RULE 5 & 6 STRESS TEST':^100}")
    print("=" * 100)
    print(f"{'Description':<60} | {'Status':<10} | {'Details'}")
    print("-" * 100)
    
    total = len(test_cases)
    passed = 0
    false_positives = 0
    false_negatives = 0
    
    for text, expect_error, desc in test_cases:
        results = check_spelling(text)
        found_error = False
        error_details = []
        
        # Filter for Rule 5 / Rule 6 specific errors
        for err in results['errors'].values():
            orig = err['original'].strip()
            # Ignore punctuation-only errors for this specific stress test assessment
            if orig in ("។", "៕", "?", "!"):
                continue
            
            # Rule 5 errors are usually 'contextual' or 'register_mismatch'
            # Rule 6 errors are usually 'contextual' (verb/noun pairs) or 'spelling'
            if err['error_type'] in ('contextual', 'register_mismatch', 'spelling'):
                found_error = True
                error_details.append(f"{orig} -> {err['suggestions'][0] if err['suggestions'] else 'N/A'}")
        
        status = "FAIL"
        details = ""
        
        if found_error == expect_error:
            status = "PASS"
            passed += 1
            if found_error:
                details = f"Detected: {', '.join(error_details)}"
        else:
            if expect_error and not found_error:
                status = "FAIL (FN)"
                false_negatives += 1
                details = "Expected error not detected"
            elif not expect_error and found_error:
                status = "FAIL (FP)"
                false_positives += 1
                details = f"False positive: {', '.join(error_details)}"
        
        print(f"{desc[:58]:<60} | {status:<10} | {details}")
    
    print("=" * 100)
    print(f"SUMMARY: {passed}/{total} Passed ({passed/total*100:.1f}%)")
    print(f"- Correct Detections: {passed}")
    print(f"- False Positives:    {false_positives}")
    print(f"- False Negatives:    {false_negatives}")
    print("=" * 100)

if __name__ == "__main__":
    test_rule_5_stress()
