
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

def run_30_sentences_stress_test():
    print("=" * 100)
    print("RUNNING KHMER SPELL CHECKER STRESS TEST: 30 SENTENCES WITH TWO ERRORS EACH")
    print("=" * 100)
    
    print("Initializing Spell Checker Data...")
    start_load = time.time()
    word_set, word_to_pos, word_freq, _ = SpellCheckerData.build_tables()
    word_list = SpellCheckerData.get_word_list()
    bigrams = SpellCheckerData.load_bigrams()
    print(f"Data loaded in {time.time() - start_load:.2f}s")
    
    test_cases = [
        {"id": 1, "text": "សិស្សនុសិស្សទាំងអស់ត្រូវគោរពនៅវិន័យសាលា។", "expected_errors": ["សិស្សនុសិស្ស", "នៅ"]},
        {"id": 2, "text": "អគុណច្រើនសំរាប់ការជួយដល់ខ្ញុំ។", "expected_errors": ["អគុណ", "សំរាប់"]},
        {"id": 3, "text": "ខ្ញុំចង់ទៅលេងប្រទសថៃនៅខែក្រោយជារៀងរាល់ឆ្មាំ។", "expected_errors": ["ប្រទស", "ឆ្មាំ"]},
        {"id": 4, "text": "សូមមេត្តាផ្ញើរពត៌មានមកខ្ញុំឲ្យបានឆាប់។", "expected_errors": ["ផ្ញើរ", "ពត៌មាន"]},
        {"id": 5, "text": "កំលាំងពលកម្មគឺជាកត្តាសំខាន់ក្នុងការសំរេចជោគជ័យ។", "expected_errors": ["កំលាំង", "សំរេច"]},
        {"id": 6, "text": "តំលៃទំនិញមានការប្រែប្រួលរាល់ថ្ងែ។", "expected_errors": ["តំលៃ", "ថ្ងែ"]},
        {"id": 7, "text": "បញ្ហាចរាចរណ៏គឺជាបញ្ហាប្រឈមធំនៅពេលបច្ចុប្បន្នន។", "expected_errors": ["ចរាចរណ៏", "បច្ចុប្បន្នន"]},
        {"id": 8, "text": "សូមអោយលោកអ្នកជួបតែសំណាងល្អនឹងសុភមង្គលល។", "expected_errors": ["អោយ", "សុភមង្គលល"]},
        {"id": 9, "text": "យើងត្រូវការពារនៅធនធានធម្មជាតិដើម្បីរក្សាតុល្យភា។", "expected_errors": ["នៅ", "តុល្យភា"]},
        {"id": 10, "text": "ការប្រកួតប្រជែនេះមានភាពតានតឹងខ្លាំងណាស់សំរាប់យើង។", "expected_errors": ["ប្រកួតប្រជែ", "សំរាប់"]},
        {"id": 11, "text": "បច្ចេកវិជ្ជាពត៌មានគឺជាផ្នែកមួយនៃជីវិត។", "expected_errors": ["បច្ចេកវិជ្ជា", "ពត៌មាន"]},
        {"id": 12, "text": "ខ្ញុំប្រើអិនធឺណិតដើម្បីស្រាវជ្រាវចំណេះដឺងថ្មីៗ។", "expected_errors": ["អិនធឺណិត", "ចំណេះដឺង"]},
        {"id": 13, "text": "សិល្បៈនិងវប្បធម៏ខ្មែរគឺជាមរតដ៏អស្ចារ្យ។", "expected_errors": ["វប្បធម៏", "មរត"]},
        {"id": 14, "text": "ការសិក្សារនៅសកលវិទ្យាល័យតម្រូវឱ្យមានការខិតខំខ្លាំងណាស់។", "expected_errors": ["សិក្សារ", "សកលវិទ្យាល័យ"]},
        {"id": 15, "text": "សូមអានសៀវភៅនេះដើម្បីពង្រីកចំណេះដឺងនិងបញ្ញារ។", "expected_errors": ["ចំណេះដឺង", "បញ្ញារ"]},
        {"id": 16, "text": "គម្រោងនេះត្រូវបានបញ្ចប់សព្វគ្របនៅរសៀលថ្ងែនេះ។", "expected_errors": ["សព្វគ្រប", "ថ្ងែ"]},
        {"id": 17, "text": "មន្ត្រីរាជការត្រូវមានមនសិការរនិងសីលធម៏ខ្ពស់។", "expected_errors": ["មនសិការរ", "សីលធម៏"]},
        {"id": 18, "text": "យើងត្រូវរួមគ្នាថែរក្សាប្រពៃណនិងសុជីវធម៏ខ្មែរ។", "expected_errors": ["ប្រពៃណ", "សុជីវធម៏"]},
        {"id": 19, "text": "កុមារត្រូវរៀនសូត្រពីកតញ្ញនិងការគោរពចាស់ទុំម។", "expected_errors": ["កតញ្ញ", "ចាស់ទុំម"]},
        {"id": 20, "text": "ជំនឿលើព្រលឹដូនតាគឺជាផ្នែកមួយនៃជំនឿបូរាណណ។", "expected_errors": ["ព្រលឹ", "បូរាណណ"]},
        {"id": 21, "text": "រូបភាដ៏ស្រស់បំព្រងនៃធម្មជាតិធ្វើឱ្យយើងសប្បាយយចិត្ត។", "expected_errors": ["រូបភា", "សប្បាយយ"]},
        {"id": 22, "text": "មេឃមានព៌ណខៀវស្រឡះនៅថ្ងៃឈប់សំរាក។", "expected_errors": ["ព៌ណ", "សំរាក"]},
        {"id": 23, "text": "ផ្កាកុលាបមានពណ៌ក្រហដ៏ស្រស់ស្អាណាស់។", "expected_errors": ["ក្រហ", "ស្អា"]},
        {"id": 24, "text": "ស្រូវក្នុងស្រែមានពណ៌លឿទុំពេញវាលស្រែដ៏ធំល្វឹងល្វើយយ។", "expected_errors": ["លឿ", "ល្វឹងល្វើយយ"]},
        {"id": 25, "text": "សន្តិសុនៅក្នុងតំបន់ត្រូវបានត្រួតពិនិត្យយ៉ាងមោះមុតត។", "expected_errors": ["សន្តិសុ", "មោះមុតត"]},
        {"id": 26, "text": "យាមកាកំពុងការពារសុវត្ថិភានៅតាមច្រកចេញចូល។", "expected_errors": ["យាមកា", "សុវត្ថិភា"]},
        {"id": 27, "text": "ក្តីស្រឡាញ់ចេញពីបេះដូពិតជាមានតំលៃណាស់។", "expected_errors": ["បេះដូ", "តំលៃ"]},
        {"id": 28, "text": "ការខិតខំប្រឹងប្រែងនឹងនាំអ្នកទៅកាន់ជោគជយនាពេលអនាគតត។", "expected_errors": ["ជោគជយ", "អនាគតត"]},
        {"id": 29, "text": "គម្រោងនេះត្រូវបានបង្កើតឡើងសំរាប់ជួយដល់ជនក្រីគ្រ។", "expected_errors": ["សំរាប់", "ក្រីគ្រ"]},
        {"id": 30, "text": "អគុណច្រើនសម្រាប់ជំនួយបច្ចេកទេសរបស់អ្នកនាថ្ងែនេះ។", "expected_errors": ["អគុណ", "ថ្ងែ"]},
    ]

    print(f"\nRunning {len(test_cases)} Stress Tests...\n")
    print(f"{'ID':<4} | {'Status':<10} | {'Errors Detected':<4} | {'Details'}")
    print("-" * 120)

    total_expected = 0
    total_found = 0
    sentences_fully_correct = 0
    
    for case in test_cases:
        text = case["text"]
        expected = case["expected_errors"]
        total_expected += len(expected)
        
        # 1. Segment
        tokens = segment_text(text)
        
        # 2. Tag
        tagged = pos_tag_tokens(tuple(tokens), word_to_pos, word_set)
        
        # 3. Detect
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
        
        if case['id'] == 19:
            print(f"DEBUG ID 19: Tokens={tokens}, Detected={detected_tokens}, Indices={error_indices}")
        
        found_expected = [e for e in expected if e in detected_set or any(e in d for d in detected_set)]
        num_found = len(found_expected)
        total_found += num_found
        
        is_fully_detected = num_found == len(expected)
        if is_fully_detected:
            sentences_fully_correct += 1
            
        status_str = "PASS" if is_fully_detected else "PARTIAL" if num_found > 0 else "FAIL"
        
        detected_str = f"Found: {list(detected_set)}"
        expected_str = f"Expected: {expected}"
        detail = f"{detected_str} | {expected_str}"

        print(f"{case['id']:<4} | {status_str:<10} | {num_found}/{len(expected)} | {detail}")

    print("-" * 120)
    print(f"Total Errors Detected: {total_found}/{total_expected} ({total_found/total_expected*100:.1f}%)")
    print(f"Sentences Fully Detected: {sentences_fully_correct}/{len(test_cases)} ({sentences_fully_correct/len(test_cases)*100:.1f}%)")
    print("=" * 100)

if __name__ == "__main__":
    run_30_sentences_stress_test()
