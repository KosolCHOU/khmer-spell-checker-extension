
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

def run_30_sentences_with_errors_test():
    print("=" * 100)
    print("RUNNING KHMER SPELL CHECKER TEST: 30 SENTENCES WITH ONE ERROR EACH")
    print("=" * 100)
    
    print("Initializing Spell Checker Data...")
    start_load = time.time()
    word_set, word_to_pos, word_freq, _ = SpellCheckerData.build_tables()
    word_list = SpellCheckerData.get_word_list()
    bigrams = SpellCheckerData.load_bigrams()
    print(f"Data loaded in {time.time() - start_load:.2f}s")
    
    test_cases = [
        {"id": 1, "topic": "Education", "text": "និស្សិតជាច្រើនកំពុងសិក្សានៅសកលវិទ្យាល័យភូមិន្ទភ្នំពេញ។", "expected_errors": ["សកលវិទ្យាល័យ"]},
        {"id": 2, "topic": "Technology", "text": "បច្ចេកវិជ្ជាបានដើរតូនាទីយ៉ាងសំខាន់ក្នុងព៌តមានវិទ្យា។", "expected_errors": ["ព៌តមាន"]},
        {"id": 3, "topic": "Communication", "text": "សូមមេត្តាផ្ញើរឯកសារមកខ្ញុំតាមរយៈសារអេឡិចត្រូនិច។", "expected_errors": ["ផ្ញើរ"]},
        {"id": 4, "topic": "Formal", "text": "គម្រោងនេះត្រូវបានបង្កើតឡើងសំរាប់ជួយដល់ជនក្រីក្រ។", "expected_errors": ["សំរាប់"]},
        {"id": 5, "topic": "Innovation", "text": "យើងត្រូវធ្វើបច្ចុប្បន្នភាននៃប្រព័ន្ធការងាររបស់យើង។", "expected_errors": ["បច្ចុប្បន្នភាន"]},
        {"id": 6, "topic": "Politeness", "text": "អគុណច្រើនសម្រាប់ជំនួយបច្ចេកទេសរបស់អ្នកនៅថ្ងៃនេះ។", "expected_errors": ["អគុណ"]},
        {"id": 7, "topic": "General", "text": "ពួកយើងមានអារម្មណ៍សប្បាយយខ្លាំងណាស់ដែលបានជួបអ្នក។", "expected_errors": ["សប្បាយយ"]},
        {"id": 8, "topic": "Culture", "text": "ប្រាសាទអង្គរវត្តគឺជាមរតដ៏អស្ចារ្យរបស់បុព្វបុរសខ្មែរ។", "expected_errors": ["មរត"]},
        {"id": 9, "topic": "Success", "text": "ការខិតខំប្រឹងប្រែងនឹងនាំអ្នកទៅកាន់ជោគជយនាពេលអនាគត។", "expected_errors": ["ជោគជយ"]},
        {"id": 10, "topic": "Future", "text": "យើងត្រូវសម្លឹងមើលទៅលើអនាគតតដ៏យូរអង្វែងរបស់ជាតិ។", "expected_errors": ["អនាគតត"]},
        {"id": 11, "topic": "Emotion", "text": "ក្តីស្រឡាញ់ចេញពីបេះដូពិតជាមានតម្លៃលើសលប់។", "expected_errors": ["បេះដូ"]},
        {"id": 12, "topic": "Relationship", "text": "ខ្ញុំស្រលាញការអានសៀវភៅនៅពេលរសៀលជារៀងរាល់ថ្ងៃ។", "expected_errors": ["ស្រលាញ"]},
        {"id": 13, "topic": "Ethic", "text": "មន្ត្រីរាជការត្រូវមានមនសិការរវិជ្ជាជីវៈខ្ពស់ក្នុងការងារ។", "expected_errors": ["មនសិការរ"]},
        {"id": 14, "topic": "Heritage", "text": "សិល្បៈនិងវប្បធម៏គឺជាអត្តសញ្ញាណដ៏សំខាន់របស់ប្រជាជាតិ។", "expected_errors": ["វប្បធម៏"]},
        {"id": 15, "topic": "State", "text": "គ្រួសារដែលមានសុភមង្គលលគឺជាគ្រឹះនៃសង្គមដ៏រឹងមាំ។", "expected_errors": ["សុភមង្គលល"]},
        {"id": 16, "topic": "Responsibility", "text": "សិស្សគ្រប់រូបត្រូវបំពេញកិច្ចកាផ្ទះឱ្យបានរួចរាល់។", "expected_errors": ["កិច្ចកា"]},
        {"id": 17, "topic": "Order", "text": "ការរក្សាសណ្តាប់ធ្នបសាធារណៈគឺជាភារកិច្ចរបស់យើងទាំងអស់គ្នា។", "expected_errors": ["សណ្តាប់ធ្នប"]},
        {"id": 18, "topic": "Security", "text": "កងកម្លាំងមានសមត្ថកិច្ចកំពុងពង្រឹងសន្តិសុនៅក្នុងតំបន់។", "expected_errors": ["សន្តិសុ"]},
        {"id": 19, "topic": "Safety", "text": "មានអ្នកយាមកាកំពុងការពារសុវត្ថិភាពនៅមាត់ច្រកចេញចូល។", "expected_errors": ["យាមកា"]},
        {"id": 20, "topic": "Tradition", "text": "យុវជនខ្មែរត្រូវរួមគ្នាថែរក្សាប្រពៃណដ៏ល្អផូរផង់។", "expected_errors": ["ប្រពៃណ"]},
        {"id": 21, "topic": "Morality", "text": "ការគោរពសីលធម៏ក្នុងសង្គមគឺជាគុណតម្លៃរបស់មនុស្សជាតិ។", "expected_errors": ["សីលធម៏"]},
        {"id": 22, "topic": "Behavior", "text": "កុមារត្រូវរៀនសូត្រអំពីសុជីវធម៏ក្នុងការទំនាក់ទំនង។", "expected_errors": ["សុជីវធម៏"]},
        {"id": 23, "topic": "Gratitude", "text": "យើងត្រូវមានកតញ្ញខ្ពស់ចំពោះអ្នកដែលមានគុណលើរូបយើង។", "expected_errors": ["កតញ្ញ"]},
        {"id": 24, "topic": "Spirit", "text": "ជំនឿលើព្រលឹដូនតាគឺជាផ្នែកមួយនៃជំនឿបែបបូរាណ។", "expected_errors": ["ព្រលឹ"]},
        {"id": 25, "topic": "Soul", "text": "ការស្ងប់ក្នុងវិញ្ញាណណនាំឱ្យសម្រេចបាននូវសេចក្តីសុខពិត។", "expected_errors": ["វិញ្ញាណណ"]},
        {"id": 26, "topic": "Visual", "text": "រូបភាដ៏ស្រស់ត្រកាលនៃធម្មជាតិបង្កប់ដោយភាពស្ងប់ស្ងាត់។", "expected_errors": ["រូបភា"]},
        {"id": 27, "topic": "Color", "text": "មេឃមានព៌ណខៀវស្រឡះនៅថ្ងៃឈប់សម្រាកចុងសប្តាហ៍។", "expected_errors": ["ព៌ណ"]},
        {"id": 28, "topic": "Color", "text": "ផ្កាកុលាបមានពណ៌ក្រហដ៏ស្រស់ឆើតឆាយគួរឱ្យចង់ទស្សនា។", "expected_errors": ["ក្រហ"]},
        {"id": 29, "topic": "Nature", "text": "ស្លឹកឈើពណ៌បៃតផ្តល់នូវអារម្មណ៍ស្រស់ស្រាយដល់ភ្នែក។", "expected_errors": ["បៃត"]},
        {"id": 30, "topic": "Season", "text": "ស្រូវក្នុងស្រែមានពណ៌លឿទុំពេញវាលស្រែដ៏ធំល្វឹងល្វើយ។", "expected_errors": ["លឿ"]},
    ]

    print(f"\nRunning {len(test_cases)} Tests...\n")
    print(f"{'ID':<4} | {'Topic':<15} | {'Status':<10} | {'Details'}")
    print("-" * 120)

    passed = 0
    
    for case in test_cases:
        text = case["text"]
        
        # 1. Segment
        tokens = segment_text(text)
        
        # 2. Tag
        tagged = pos_tag_tokens(tuple(tokens), word_to_pos, word_set)
        
        # 3. Detect
        errors = {}
        error_indices = detect_error_slots(tagged, word_set, word_list, bigrams, {}, errors, word_freq)
        detect_grammar_errors(tagged, errors)
        
        # Collect detected tokens from both the returned indices and the errors dict
        detected_tokens = []
        
        # Add from errors dict first (includes suggestions/details)
        for idx in errors:
            detected_tokens.append(errors[idx]['original'])
            
        # Add from error_indices (might not have entries in errors dict yet)
        for idx in error_indices:
            token_text = tagged[idx]['token']
            if token_text not in detected_tokens:
                detected_tokens.append(token_text)
            
        detected_set = set(detected_tokens)
        
        # Pass if ANY of the expected errors are detected
        is_pass = False
        found_expected = [e for e in case['expected_errors'] if e in detected_set or any(e in d for d in detected_set)]
        
        if found_expected:
            is_pass = True
            passed += 1
        
        status_str = "PASS" if is_pass else "FAIL"
            
        # Format output
        detected_str = f"Found: {list(detected_set)}" if detected_set else "Found: None"
        if not is_pass:
            expected_str = f"Expected: {case['expected_errors']}"
            detail = f"{detected_str} | {expected_str}"
        else:
             detail = f"{detected_str}"

        print(f"{case['id']:<4} | {case['topic']:<15} | {status_str:<10} | {detail}")

    print("-" * 120)
    print(f"Final Detection Success Rate: {passed}/{len(test_cases)} ({passed/len(test_cases)*100:.1f}%)")
    print("=" * 100)

if __name__ == "__main__":
    run_30_sentences_with_errors_test()
