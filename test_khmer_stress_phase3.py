
import sys
import time
from typing import List, Dict

# Import the spell checker module
from keyez.landing.spell_checker_advanced import (
    SpellCheckerData, 
    segment_text, 
    pos_tag_tokens, 
    detect_error_slots,
)

def run_stress_test_phase3():
    print("=" * 100)
    print("RUNNING KHMER SEGMENTATION/SPELL STRESS TEST PHASE 3: 30 NEW GENERALIZATION CHECKS")
    print("=" * 100)
    
    print("Initializing Spell Checker Data...")
    word_set, word_to_pos, word_freq, _ = SpellCheckerData.build_tables()
    word_list = SpellCheckerData.get_word_list()
    bigrams = SpellCheckerData.load_bigrams()
    
    test_cases = [
        # 1. "កម្រាល" (Mat/Floor). Typo "កំរាល" (Common old spelling).
        {"id": 1, "text": "កំរាលព្រំនេះស្អាតណាស់។", "expected_errors": ["កំរាល"]},
        
        # 2. "កំណើត" (Birth). Typo "កំនើត".
        {"id": 2, "text": "ថ្ងៃកំនើតរបស់អ្នក។", "expected_errors": ["កំនើត"]},

        # 3. "ប្រយោជន៍" (Benefit). Typo "ប្រយោជន៏".
        {"id": 3, "text": "មានប្រយោជន៏ច្រើនចំពោះសុខភាព។", "expected_errors": ["ប្រយោជន៏"]},

        # 4. "បញ្ចប" (Typo of បញ្ចប់?? Or similar). "បញ្ចប់" (Finish). Typo "បញ្ចប". 
        {"id": 4, "text": "សូមបញ្ចបការងារនៅទីនេះ។", "expected_errors": ["បញ្ចប"]},

        # 5. "សរសេរ" (Write). Typo "សរសេ".
        {"id": 5, "text": "គាត់កំពុងសរសេសំបុត្រ។", "expected_errors": ["សរសេ"]},

        # 6. "ពិសេ" (Typo of ពិសេស Special).
        {"id": 6, "text": "មានការបញ្ចុះតម្លៃពិសេ។", "expected_errors": ["ពិសេ"]},

        # 7. "សង្ឃឹម" (Hope). Typo "សង្ខឹម".
        {"id": 7, "text": "ខ្ញុំសង្ខឹមថានឹងបានជួបគ្នា។", "expected_errors": ["សង្ខឹម"]},

        # 8. "ជោគជៃ" (Success). Typo of "ជោគជ័យ".
        {"id": 8, "text": "ជូនពរឱ្យទទួលបានជោគជៃ។", "expected_errors": ["ជោគជៃ"]},

        # 9. "កិតិយស" (Honor). Typo of "កិត្តិយស".
        {"id": 9, "text": "ជាកិតិយសដ៏ធំធេង។", "expected_errors": ["កិតិយស"]},

        # 10. "មោទនភា" (Pride). Typo of "មោទនភាព".
        {"id": 10, "text": "មានមោទនភាជាតិ។", "expected_errors": ["មោទនភា"]},

        # 11. "សាមគី" (Unity). Typo of "សាមគ្គី".
        {"id": 11, "text": "យើងត្រូវចេះសាមគីគ្នា។", "expected_errors": ["សាមគី"]},

        # 12. "បដិសេដ" (Reject). Typo of "បដិសេធ".
        {"id": 12, "text": "កុំបដិសេដសំណើនេះ។", "expected_errors": ["បដិសេដ"]},

        # 13. "ជ្រើសរើ" (Choose). Typo of "ជ្រើសរើស".
        {"id": 13, "text": "សូមជ្រើសរើចម្លើយត្រឹមត្រូវ។", "expected_errors": ["ជ្រើសរើ"]},

        # 14. "អនុគ្រោ" (Tolerate). Typo of "អនុគ្រោះ".
        {"id": 14, "text": "សូមមេត្តាអនុគ្រោចំពោះកំហុស។", "expected_errors": ["អនុគ្រោ"]},

        # 15. "សង្សា" (Lover). Typo of "សង្សារ".
        {"id": 15, "text": "គាត់មានសង្សាថ្មី។", "expected_errors": ["សង្សា"]},

        # 16. "ដង្ហើ" (Breath). Typo of "ដង្ហើម".
        {"id": 16, "text": "ពិបាកដកដង្ហើណាស់។", "expected_errors": ["ដង្ហើ"]},

        # 17. "ចង្កៀ" (Lamp). Typo of "ចង្កៀង".
        {"id": 17, "text": "បំភ្លឺចង្កៀប្រេង។", "expected_errors": ["ចង្កៀ"]},

        # 18. "បង្កើ" (Increase/Create). Typo of "បង្កើន" or "បង្កើត".
        # "បង្កើន" (Increase).
        {"id": 18, "text": "បង្កើប្រាក់ចំណូល។", "expected_errors": ["បង្កើ"]},

        # 19. "កំចាត់" (Eliminate). Typo of "កម្ចាត់".
        {"id": 19, "text": "ចូលរួមកំចាត់គ្រឿងញៀន។", "expected_errors": ["កំចាត់"]},

        # 20. "បំផ្លាន" (Destroy). Typo of "បំផ្លាញ".
        {"id": 20, "text": "កុំបំផ្លានទ្រព្យសម្បត្តិរដ្ឋ។", "expected_errors": ["បំផ្លាន"]},

        # 21. "សាងសង" (Build). Typo of "សាងសង់".
        {"id": 21, "text": "កំពុងសាងសងអគារថ្មី។", "expected_errors": ["សាងសង"]},

        # 22. "ប្រស្រើរ" (Better). Typo of "ប្រសើរ".
        {"id": 22, "text": "ជូនពរឱ្យឆាប់ជាសះស្បើយប្រស្រើរឡើង។", "expected_errors": ["ប្រស្រើរ"]},

        # 23. "ច្រេន" (Many). Typo of "ច្រើន".
        {"id": 23, "text": "មានមនុស្សច្រេនណាស់។", "expected_errors": ["ច្រេន"]},

        # 24. "ខា្លង" (Strong). Typo of "ខ្លាំង" (Subscript order).
        {"id": 24, "text": "ខ្យល់បក់ខា្លងណាស់។", "expected_errors": ["ខា្លង"]},

        # 25. "បង្រៀ" (Teach). Typo of "បង្រៀន".
        {"id": 25, "text": "គ្រូកំពុងបង្រៀសិស្ស។", "expected_errors": ["បង្រៀ"]},

        # 26. "រងចាំ" (Wait - common error). "រង់ចាំ" (Correct).
        {"id": 26, "text": "សូមរងចាំមួយភ្លែត។", "expected_errors": ["រងចាំ"]},

        # 27. "ស្តាយ" (Regret). Typo "ស្តា" (Missing 'y'). "ស្តាយក្រោយ".
        {"id": 27, "text": "កុំឱ្យស្តាក្រោយ។", "expected_errors": ["ស្តា"]},

        # 28. "ចម្រើ" (Prosper/Song?). "ចម្រើន" (Prosper). Typo "ចម្រើ".
        {"id": 28, "text": "សង្គមជាតិរីកចម្រើ។", "expected_errors": ["ចម្រើ"]},

        # 29. "បណ្តាល" (Cause). Typo "បណ្តា" (Countries - valid word). 
        # Context: "បណ្តាលឱ្យ" (Cause to). "បណ្តាឱ្យ" (Countries to?? No).
        # This is strictly a Context Error if "បណ្តា" is valid but wrong here.
        # "បណ្ដា" (Plural marker/Countries).
        {"id": 29, "text": "គ្រោះថ្នាក់នេះបណ្តាឱ្យមានអ្នករបួស។", "expected_errors": ["បណ្តា"]},

        # 30. "អភិរក្ស" (Conserve). Typo "អភិរក" (Missing subscript/sa).
        {"id": 30, "text": "ចូលរួមអភិរកវប្បធម៌។", "expected_errors": ["អភិរក"]},
    ]

    print(f"\nRunning {len(test_cases)} Segmentation/Spell Stress Tests Phase 3 (Generalization)...\n")
    print(f"{'ID':<4} | {'Status':<15} | {'Detected':<40} | {'Expected':<20}")
    print("-" * 120)

    total_found = 0
    total_expected = 0
    sentences_passed = 0
    
    for case in test_cases:
        text = case["text"]
        expected_list = case["expected_errors"]
        total_expected += len(expected_list)
        
        # 1. Segment
        tokens = segment_text(text)
        
        # 2. Tag
        tagged = pos_tag_tokens(tuple(tokens), word_to_pos, word_set)
        
        # 3. Detect
        errors = {}
        error_indices = detect_error_slots(tagged, word_set, word_list, bigrams, {}, errors, word_freq)
        
        detected_errors = []
        for idx in errors:
            detected_errors.append(errors[idx]['original'])
        for idx in error_indices:
             t = tagged[idx]['token']
             if t not in detected_errors:
                 detected_errors.append(t)
                 
        # Evaluate
        found_count = 0
        detected_set = set(detected_errors)
        matches = []
        
        for exp in expected_list:
            if exp in detected_set:
                matches.append(exp)
                continue
            
            # Relaxed check
            found_part = False
            for det in detected_errors:
                if (det in exp and len(det) > 1) or (exp in det):
                    matches.append(det) 
                    found_part = True
                    break
            if found_part:
                continue
                
        if len(matches) >= len(expected_list):
            status = "PASS"
            sentences_passed += 1
            total_found += len(expected_list)
        else:
            status = "FAIL"
            
        print(f"{case['id']:<4} | {status:<15} | {str(detected_errors):<40} | {str(expected_list):<20}")
        if status == "FAIL":
             print(f"      Tokens: {tokens}")

    print("-" * 120)
    print(f"Total Detected: {total_found}/{total_expected}")
    print(f"Sentences Passed: {sentences_passed}/{len(test_cases)}")
    print("=" * 100)

if __name__ == "__main__":
    run_stress_test_phase3()
