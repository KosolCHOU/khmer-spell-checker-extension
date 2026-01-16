
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

def run_stress_test_phase2():
    print("=" * 100)
    print("RUNNING KHMER SEGMENTATION/SPELL STRESS TEST PHASE 2: 30 NEW SENTENCES")
    print("=" * 100)
    
    # Pre-patch whitelist for test purposes if needed
    SpellCheckerData.build_tables()
    SpellCheckerData._word_set.add("តម្លើង") # Whitelist this common variant to focus on 'ប្រពន្ធ' error
    word_set, word_to_pos, word_freq, _ = SpellCheckerData.build_tables()
    word_list = SpellCheckerData.get_word_list()
    bigrams = SpellCheckerData.load_bigrams()
    
    test_cases = [
        # 1. "សប្តាហ៍" (Week). Typo "សប្តាហ" (Missing mark). "សប្តាហនេះ" (Week+This merge risk).
        {"id": 1, "text": "យើងជួបគ្នានៅសប្តាហនេះ។", "expected_errors": ["សប្តាហ"]},
        
        # 2. "បញ្ចប់" (Finish). Typo "បន្ចប់" (Wrong char). "បន្ចប់ការងារ".
        {"id": 2, "text": "ខ្ញុំបានបន្ចប់ការងារហើយ។", "expected_errors": ["បន្ចប់"]},

        # 3. "សម្រស់" (Beauty). Typo "សំរស់" (Common spelling var/typo). "សំរស់ធម្មជាតិ".
        {"id": 3, "text": "សំរស់ធម្មជាតិស្រស់បំព្រង។", "expected_errors": ["សំរស់"]},

        # 4. "វិស្វករ" (Engineer). Typo "វិស្វក្រ" (Spelling).
        {"id": 4, "text": "គាត់គឺជាវិស្វក្រសំណង់។", "expected_errors": ["វិស្វក្រ"]},

        # 5. "យុទ្ធសាស្ត្រ" (Strategy). Typo "យុទ្ឋសាស្ត្រ" (Subscript).
        {"id": 5, "text": "ផែនការយុទ្ឋសាស្ត្រថ្មី។", "expected_errors": ["យុទ្ឋសាស្ត្រ"]},

        # 6. "អន្តរជាតិ" (International). Typo "អន្តរជាត" (Missing vowel). "អន្តរជាតិនេះ" risk.
        {"id": 6, "text": "កិច្ចសហប្រតិបត្តិការអន្តរជាត។", "expected_errors": ["អន្តរជាត"]},

        # 7. "ប្រជាធិបតេយ្យ" (Democracy). Typo "ប្រជាធិបតេយ" (Missing final mark).
        {"id": 7, "text": "គោលការណ៍ប្រជាធិបតេយ។", "expected_errors": ["ប្រជាធិបតេយ"]},

        # 8. "កីឡា" (Sport). Typo "កីឡារ" (Extra char). "កីឡារបាល់ទាត់".
        {"id": 8, "text": "ចូលចិត្តលេងកីឡារបាល់ទាត់។", "expected_errors": ["កីឡារ"]},

        # 9. "តន្ត្រី" (Music). Typo "តន្រ្តី" (Subscript variation? Or spelling). 
        # Actually standard is តន្ត្រី (Ta + N + Coeng Ta + Ro + I).
        # Typo "តន្រ្តី" (Ta + N + Coeng Ro ... wait). Let's use "តន្តី" (Missing Ro).
        {"id": 9, "text": "ស្តាប់តន្តីបុរាណ។", "expected_errors": ["តន្តី"]},

        # 10. "ស្ថាប័ន" (Institution). Typo "ស្ថាបន" (Missing mark). "ស្ថាបនជាតិ".
        {"id": 10, "text": "ពង្រឹងស្ថាបនជាតិ។", "expected_errors": ["ស្ថាបន"]},

        # 11. "ប្រព័ន្ធ" (System). Typo "ប្រពន្ធ" (Wife - valid word). 
        # Context: "ប្រពន្ធគ្រប់គ្រង" (Wife manages) vs "ប្រព័ន្ធគ្រប់គ្រង" (Management System).
        # This is context error.
        {"id": 11, "text": "តម្លើងប្រពន្ធគ្រប់គ្រងទិន្នន័យ។", "expected_errors": ["ប្រពន្ធ"]},

        # 12. "សហគមន៍" (Community). Typo "សហគមន៏" (Wrong mark).
        {"id": 12, "text": "អភិវឌ្ឍន៍សហគមន៏កសិកម្ម។", "expected_errors": ["សហគមន៏"]},

        # 13. "ផលិតផល" (Product). Typo "ផលិផល" (Missing Ta). "ផលិផលខ្មែរ".
        {"id": 13, "text": "គាំទ្រផលិផលខ្មែរ។", "expected_errors": ["ផលិផល"]},

        # 14. "បម្រើ" (Serve). Typo "បំរើ" (Common var). "បំរើសេវា".
        {"id": 14, "text": "បុគ្គលិកបំរើសេវា។", "expected_errors": ["បំរើ"]},

        # 15. "ទំនាក់ទំនង" (Communication). Typo "ទំនាកទំនង" (Missing Subscript/Char). "ទំនាកទំនងល្អ".
        {"id": 15, "text": "រក្សាទំនាកទំនងល្អ។", "expected_errors": ["ទំនាកទំនង"]},

        # 16. "អនុវត្ត" (Implement). Typo "អនុវត្តន៏" (Noun form usage as Verb or spelling).
        # "អនុវត្ត" is Verb, "ការអនុវត្ត" is Noun. "អនុវត្តន៍" is Noun.
        # Typo "អនុវត្តន" (Missing mark).
        {"id": 16, "text": "ត្រូវអនុវត្តនច្បាប់។", "expected_errors": ["អនុវត្តន"]},

        # 17. "កិច្ចការ" (Task). Typo "កិចការ" (Subscript).
        {"id": 17, "text": "ធ្វើកិចការផ្ទះ។", "expected_errors": ["កិចការ"]},

        # 18. "សន្និសីទ" (Conference). Typo "សន្និសិទ" (Vowel I vs II).
        {"id": 18, "text": "ចូលរួមសន្និសិទកាសែត។", "expected_errors": ["សន្និសិទ"]},

        # 19. "វិស័យ" (Sector). Typo "វិសយ" (Missing mark). "វិសយអប់រំ".
        {"id": 19, "text": "កែលំអវិសយអប់រំ។", "expected_errors": ["វិសយ"]},

        # 20. "គណនេយ្យ" (Accounting). Typo "គណនេយ" (Missing mark).
        {"id": 20, "text": "ផ្នែកគណនេយនិងហិរញ្ញវត្ថុ។", "expected_errors": ["គណនេយ"]},

        # 21. "ធនធាន" (Resource). Typo "ធនធានា" (Extra vowel). "ធនធានាមនុស្ស".
        {"id": 21, "text": "អភិវឌ្ឍធនធានាមនុស្ស។", "expected_errors": ["ធនធានា"]},

        # 22. "បរិស្ថាន" (Environment). Typo "បរិស្ឋាន" (Wrong char).
        {"id": 22, "text": "ការពារបរិស្ឋានធម្មជាតិ។", "expected_errors": ["បរិស្ឋាន"]},

        # 23. "អរិយធម៌" (Civilization). Typo "អរិយធម" (Missing mark). "អរិយធមខ្មែរ".
        {"id": 23, "text": "រុងរឿងនៃអរិយធមខ្មែរ។", "expected_errors": ["អរិយធម"]},

        # 24. "ឥទ្ធិពល" (Influence). Typo "ឥទ្ឋិពល" (Subscript).
        {"id": 24, "text": "មានឥទ្ឋិពលខ្លាំង។", "expected_errors": ["ឥទ្ឋិពល"]},

        # 25. "បតិវត្តន៍" (Revolution - wait spelling "បដិវត្តន៍"). 
        # Typo "បតិវត្តន៏".
        {"id": 25, "text": "សម័យបតិវត្តន៏ឧស្សាហកម្ម។", "expected_errors": ["បតិវត្តន៏"]},

        # 26. "សមាជិក" (Member). Typo "សមាជិ" (Missing char). "សមាជិគ្រួសារ".
        {"id": 26, "text": "ជាសមាជិគ្រួសារតែមួយ។", "expected_errors": ["សមាជិ"]},

        # 27. "សកម្មភាព" (Activity). Typo "សកម្មភា". "សកម្មភាសង្គម".
        {"id": 27, "text": "ចូលរួមសកម្មភាសង្គម។", "expected_errors": ["សកម្មភា"]},

        # 28. "អាហារូបករណ៍" (Scholarship). Typo "អាហារូបករណ៏".
        # Typo "អាហារូបករ".
        {"id": 28, "text": "ទទួលបានអាហារូបករទៅបរទេស។", "expected_errors": ["អាហារូបករ"]},

        # 29. "បច្ចុប្បន្ន" (Present). Typo "បច្ចុប្បន" (Missing mark).
        {"id": 29, "text": "ស្ថិតក្នុងស្ថានភាពបច្ចុប្បន។", "expected_errors": ["បច្ចុប្បន"]},

        # 30. "ប្រពៃណី" (Tradition). Typo "ប្រពៃណ" (Missing vowel). "ប្រពៃណខ្មែរ".
        {"id": 30, "text": "ថែរក្សាទំនៀមទម្លាប់ប្រពៃណខ្មែរ។", "expected_errors": ["ប្រពៃណ"]},
    ]

    print(f"\nRunning {len(test_cases)} Segmentation/Spell Stress Tests Phase 2...\n")
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
        pass_relaxed = False
        
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
                    matches.append(det) # Log what we found
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
    run_stress_test_phase2()
