
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

def run_stress_test_phase4():
    print("=" * 100)
    print("RUNNING KHMER SEGMENTATION/SPELL STRESS TEST PHASE 4: 30 SPLIT/CONTEXT PHRASES")
    print("=" * 100)
    
    print("Initializing Spell Checker Data...")
    word_set, word_to_pos, word_freq, _ = SpellCheckerData.build_tables()
    word_list = SpellCheckerData.get_word_list()
    bigrams = SpellCheckerData.load_bigrams()
    
    # Simulating users incorrectly adding spaces in compounds OR ambiguous segmentation
    # Focus on cases where parts are valid words.
    test_cases = [
        # 1. "សេដ្ឋកិច្ច" (Economy). Split: "សេដ្ឋ កិច្ច". 
        # "សេដ្ឋ" (Noble/Best - Sanskrit). "កិច្ច" (Work/Task).
        {"id": 1, "text": "ការរីកចម្រើននៃសេដ្ឋ កិច្ចជាតិ។", "expected_errors": ["សេដ្ឋ កិច្ច"]},
        
        # 2. "វប្បធម៌" (Culture). Split: "វប្ប ធម៌".
        # "វប្ប" (Sowing/Seed). "ធម៌" (Dharma).
        {"id": 2, "text": "ថែរក្សាវប្ប ធម៌ខ្មែរ។", "expected_errors": ["វប្ប ធម៌"]},

        # 3. "នយោបាយ" (Politics). Split: "ន យោបាយ".
        # "ន" (The/Method?). "យោបាយ" (Strategy).
        {"id": 3, "text": "ស្ថិរភាពន យោបាយ។", "expected_errors": ["ន យោបាយ"]},

        # 4. "ប្រជាធិបតេយ្យ" (Democracy). Split: "ប្រជា ធិបតេយ្យ".
        # "ប្រជា" (People). "ធិបតេយ្យ" (Sovereignty/Dominance).
        {"id": 4, "text": "លទ្ធិប្រជា ធិបតេយ្យ។", "expected_errors": ["ប្រជា ធិបតេយ្យ"]},

        # 5. "បច្ចេកទេស" (Technical). Split: "បច្ចេក ទេស".
        # "បច្ចេក" (Individual/Specific). "ទេស" (Country/Region/Show).
        {"id": 5, "text": "ជំនាញបច្ចេក ទេស។", "expected_errors": ["បច្ចេក ទេស"]},

        # 6. "អន្តរជាតិ" (International). Split: "អន្តរ ជាតិ".
        # "អន្តរ" (Inter/Between). "ជាតិ" (Nation).
        {"id": 6, "text": "កិច្ចសហប្រតិបត្តិការអន្តរ ជាតិ។", "expected_errors": ["អន្តរ ជាតិ"]},

        # 7. "កសិកម្ម" (Agriculture). Split: "កសិ កម្ម".
        # "កសិ" (Farmer). "កម្ម" (Action/Karma).
        {"id": 7, "text": "វិស័យកសិ កម្ម។", "expected_errors": ["កសិ កម្ម"]},

        # 8. "ទេសចរណ៍" (Tourism). Split: "ទេស ចរណ៍".
        # "ទេស" (Land). "ចរណ៍" (Travel).
        {"id": 8, "text": "តំបន់ទេស ចរណ៍។", "expected_errors": ["ទេស ចរណ៍"]},

        # 9. "ឧស្សាហកម្ម" (Industry). Split: "ឧស្សាហ កម្ម".
        # "ឧស្សាហ" (Diligence/Energy). "កម្ម".
        {"id": 9, "text": "រោងចក្រឧស្សាហ កម្ម។", "expected_errors": ["ឧស្សាហ កម្ម"]},

        # 10. "ពាណិជ្ជកម្ម" (Commerce). Split: "ពាណិជ្ជ កម្ម".
        # "ពាណិជ្ជ" (Merchant). "កម្ម".
        {"id": 10, "text": "ធ្វើពាណិជ្ជ កម្ម។", "expected_errors": ["ពាណិជ្ជ កម្ម"]},

        # 11. "ទំនាក់ទំនង" (Communication). Split: "ទំនាក់ ទំនង".
        # "ទំនាក់" (Trap/Snare - wait, Tomnak is Relation base). "ទំនង" (Likely/Pattern).
        {"id": 11, "text": "មានទំនាក់ ទំនងល្អ។", "expected_errors": ["ទំនាក់ ទំនង"]}, # Already added rule

        # 12. "សុខភាព" (Health). Split: "សុខ ភាព".
        # "សុខ" (Happy). "ភាព" (State).
        {"id": 12, "text": "ថែរក្សាសុខ ភាព។", "expected_errors": ["សុខ ភាព"]},

        # 13. "សន្តិសុខ" (Security). Split: "សន្តិ សុខ".
        # "សន្តិ" (Peace). "សុខ" (Happy).
        {"id": 13, "text": "ការពារសន្តិ សុខសង្គម។", "expected_errors": ["សន្តិ សុខ"]},

        # 14. "អប់រំ" (Education). Split: "អប់ រំ".
        # "អប់" (Incense/Perfume/Educate). "រំ" (Cover/Wrapp).
        {"id": 14, "text": "ក្រសួងអប់ រំ។", "expected_errors": ["អប់ រំ"]},

        # 15. "អភិវឌ្ឍ" (Develop). Split: "អភិ វឌ្ឍ".
        # "អភិ" (Over/Super). "វឌ្ឍ" (Growth).
        {"id": 15, "text": "ការអភិ វឌ្ឍប្រទេស។", "expected_errors": ["អភិ វឌ្ឍ"]},

        # 16. "បរិស្ថាន" (Environment). Split: "បរិ ស្ថាន".
        # "បរិ" (Around). "ស្ថាន" (Place).
        {"id": 16, "text": "ស្រឡាញ់បរិ ស្ថាន។", "expected_errors": ["បរិ ស្ថាន"]},

        # 17. "ប្រតិបត្តិ" (Execute/Practice). Split: "ប្រតិ បត្តិ".
        # "ប្រតិ" (Counter/Towards). "បត្តិ" (Fall/Go?).
        {"id": 17, "text": "ប្រតិ បត្តិការ។", "expected_errors": ["ប្រតិ បត្តិ"]},

        # 18. "សហគមន៍" (Community). Split: "សហ គមន៍".
        # "សហ" (Co-/Together). "គមន៍" (Coming/Going).
        {"id": 18, "text": "អភិវឌ្ឍសហ គមន៍។", "expected_errors": ["សហ គមន៍"]},

        # 19. "វិនិយោគ" (Invest). Split: "វិនិ យោគ".
        # "វិនិ" (Decision?). "យោគ" (??).
        {"id": 19, "text": "ការវិនិ យោគបរទេស។", "expected_errors": ["វិនិ យោគ"]},

        # 20. "អនុវត្ត" (Implement). Split: "អនុ វត្ត".
        # "អនុ" (Sub/Minor). "វត្ត" (Cycle/Temple).
        {"id": 20, "text": "ដាក់ចេញអនុ វត្ត។", "expected_errors": ["អនុ វត្ត"]},

        # 21. "បណ្តុះបណ្តាល" (Training). Split: "បណ្តុះ បណ្តាល".
        # "បណ្តុះ" (Grow/Sprout). "បណ្តាល" (Cause).
        {"id": 21, "text": "វគ្គបណ្តុះ បណ្តាល។", "expected_errors": ["បណ្តុះ បណ្តាល"]},

        # 22. "ពិភពលោក" (World). Split: "ពិភព លោក".
        # "ពិភព" (World/Plane). "លោក" (Mr./World). "World Mr."? "World World".
        {"id": 22, "text": "នៅជុំវិញពិភព លោក។", "expected_errors": ["ពិភព លោក"]},

        # 23. "កីឡា" (Sport). Split: "កី ឡា".
        # "កី" (Loom). "ឡា" (Yard/???).
        {"id": 23, "text": "លេងកី ឡា។", "expected_errors": ["កី ឡា"]},

        # 24. "តន្ត្រី" (Music). Split: "តន្ត ្រី". No space usually inside.
        # "តន្ត្រី" -> "តន ្រ្តី"? "តន" (Musical instrument base). 
        # Let's try "សិល្បៈ" (Art). "សិល្ប ៈ" (Wrong). "សិល្ប" + "ៈ".
        {"id": 24, "text": "សិល្ប ៈវប្បធម៌។", "expected_errors": ["សិល្ប ៈ"]},

        # 25. "ជីវភាព" (Livelihood). Split: "ជីវ ភាព".
        # "ជីវ" (Life). "ភាព" (State). "Life State".
        {"id": 25, "text": "កែលម្អជីវ ភាព។", "expected_errors": ["ជីវ ភាព"]},

        # 26. "សកម្មភាព" (Activity). Split: "សកម្ម ភាព".
        # "សកម្ម" (Active). "ភាព" (State). "Active State".
        {"id": 26, "text": "សកម្ម ភាពប្រចាំថ្ងៃ។", "expected_errors": ["សកម្ម ភាព"]},

        # 27. "សមត្ថភាព" (Ability). Split: "សមត្ថ ភាព".
        # "សមត្ថ" (Capable). "ភាព".
        {"id": 27, "text": "ពង្រឹងសមត្ថ ភាព។", "expected_errors": ["សមត្ថ ភាព"]},

        # 28. "គុណភាព" (Quality). Split: "គុណ ភាព".
        # "គុណ" (Merit/Multiply). "ភាព".
        {"id": 28, "text": "ធានាគុណ ភាព។", "expected_errors": ["គុណ ភាព"]},

        # 29. "ប្រសិទ្ធភាព" (Efficiency). Split: "ប្រសិទ្ធ ភាព".
        # "ប្រសិទ្ធ" (Effective/Holy). "ភាព".
        {"id": 29, "text": "មានប្រសិទ្ធ ភាពខ្ពស់។", "expected_errors": ["ប្រសិទ្ធ ភាព"]}, # Already detected?

        # 30. "ឯករាជ្យ" (Independence). Split: "ឯក រាជ្យ".
        # "ឯក" (One/First). "រាជ្យ" (Reign). "One Reign".
        {"id": 30, "text": "បុណ្យឯក រាជ្យជាតិ។", "expected_errors": ["ឯក រាជ្យ"]},
    ]

    print(f"\nRunning {len(test_cases)} Segmentation/Spell Stress Tests Phase 4 (Split Compounds)...\n")
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
        
        # In phase 4, we expect 'errors' dict to contain PHRASE errors (key is index, suggestions has merged)
        # We need to reconstruct the DETECTED PHRASES.
        
        detected_phrases = []
        
        # Check explicit errors (from detect_grammar_errors/suspicious bigrams)
        sorted_indices = sorted(errors.keys())
        processed_indices = set()
        
        for idx in sorted_indices:
            if idx in processed_indices: continue
            
            err = errors[idx]
            # If it's a context/phrase error, it might span multiple tokens
            # We want to see if we detected "Word A" + "Word B" as an error.
            # In detect_grammar_errors, we mark idx and idx+1.
            
            detected_phrases.append(err['original']) 
            
            # If next index is also error and suggestion matches, it's a phrase detection
            # But here we just list what was flagged.
            
            # Wait, if we detect "សេដ្ឋ" and "កិច្ច" separately, that counts?
            # User wants "Merge" suggestion.
            # So looking at 'suggestions'.
            
        # Helper to see if expected split phrase was found and merged
        # Case specific logic
        detected_merged = []
        for idx in errors:
            if 'suggestions' in errors[idx] and len(errors[idx]['suggestions']) > 0:
                sugg = errors[idx]['suggestions'][0]
                # Check if suggestion is the merged form of the expected split
                detected_merged.append(sugg)
        
        found_matches = 0
        for exp in expected_list:
             # Exp is "A B". Sugg should be "AB".
             target = exp.replace(" ", "")
             if target in detected_merged:
                 found_matches += 1
             # special case: if we flagged the individual words
        
        if found_matches >= len(expected_list):
            status = "PASS"
            sentences_passed += 1
            total_found += len(expected_list)
        else:
            status = "FAIL"
            
        print(f"{case['id']:<4} | {status:<15} | {str(detected_merged):<40} | {str(expected_list):<20}")

    print("-" * 120)
    print(f"Total Detected: {total_found}/{total_expected}")
    print(f"Sentences Passed: {sentences_passed}/{len(test_cases)}")
    print("=" * 100)

if __name__ == "__main__":
    run_stress_test_phase4()
