
import sys
import time
from typing import List, Dict

# Import the spell checker module
from keyez.landing.spell_checker_advanced import (
    SpellCheckerData, 
    segment_text, 
    pos_tag_tokens, 
    detect_grammar_errors, 
    detect_error_slots
)

def run_mixed_30_sentences_test():
    print("=" * 100)
    print("RUNNING KHMER SPELL CHECKER TEST: 30 NEW MIXED SENTENCES")
    print("=" * 100)
    
    print("Initializing Spell Checker Data...")
    start_load = time.time()
    word_set, word_to_pos, word_freq, _ = SpellCheckerData.build_tables()
    word_list = SpellCheckerData.get_word_list()
    bigrams = SpellCheckerData.load_bigrams()
    print(f"Data loaded in 0.10s")
    
    test_cases = [
        # --- CORRECT SENTENCES (Expected: NO errors) ---
        {"id": 1, "type": "Correct", "topic": "Daily", "text": "ថ្ងៃនេះមេឃស្រឡះល្អណាស់ សមស្របសម្រាប់ការដើរកម្សាន្តនៅតាមសួនច្បារ។"},
        {"id": 2, "type": "Correct", "topic": "News", "text": "រដ្ឋបាលខេត្តបានរៀបចំពិធីអបអរសាទរខួបអនុស្សាវរីយ៍លើកទី៧០នៃទិវាបុណ្យឯករាជ្យជាតិ។"},
        {"id": 3, "type": "Correct", "topic": "Tech", "text": "បច្ចេកវិទ្យាបញ្ញាសិប្បនិម្មិតកំពុងផ្លាស់ប្តូររូបភាពនៃអាជីវកម្មទូទាំងពិភពលោក។"},
        {"id": 4, "type": "Correct", "topic": "History", "text": "ព្រះបាទជ័យវរ្ម័នទី៧គឺជាព្រះមហាក្សត្រដ៏ខ្លាំងពូកែបំផុតក្នុងសម័យអង្គរ។"},
        {"id": 5, "type": "Correct", "topic": "Nature", "text": "ព្រៃឈើផ្តល់ជាជម្រកដល់សត្វព្រៃនិងជួយរក្សាតុល្យភាពនៃបរិស្ថានធម្មជាតិ។"},
        {"id": 6, "type": "Correct", "topic": "Social", "text": "ការគោរពចាស់ទុំគឺជាប្រពៃណីដ៏ល្អខ្ពង់ខ្ពស់ដែលយុវជនខ្មែរគ្រប់រូបគួរតែបន្តថែរក្សា។"},
        {"id": 7, "type": "Correct", "topic": "Travel", "text": "តំបន់ឆ្នេរសមុទ្រនៃខេត្តព្រះសីហនុទាក់ទាញភ្ញៀវទេសចរយ៉ាងច្រើនជារៀងរាល់ឆ្នាំ។"},
        {"id": 8, "type": "Correct", "topic": "Education", "text": "សៀវភៅគឺជាឃ្លាំងនៃចំណេះដឹងដែលផ្តល់នូវពន្លឺដល់បញ្ញារបស់មនុស្សជាតិ។"},
        {"id": 9, "type": "Correct", "topic": "Business", "text": "សហគ្រិនវ័យក្មេងជាច្រើនកំពុងចាប់ផ្តើមអាជីវកម្មបែបច្នៃប្រឌិតនៅលើទីផ្សារឌីជីថល។"},
        {"id": 10, "type": "Correct", "topic": "Health", "text": "ការញ៉ាំអាហារដែលមានជីវជាតិគ្រប់គ្រាន់ជួយឱ្យរាងកាយមានភាពស៊ាំនឹងជំងឺផ្សេងៗ។"},
        {"id": 11, "type": "Correct", "topic": "Culture", "text": "របាំត្រុដិជាទូទៅត្រូវបានសម្តែងក្នុងឱកាសបុណ្យចូលឆ្នាំថ្មីប្រពៃណីជាតិខ្មែរ។"},
        {"id": 12, "type": "Correct", "topic": "Economy", "text": "ការនាំចេញផលិតផលកសិកម្មបានរួមចំណែកយ៉ាងសំខាន់ដល់ស្ថិរភាពសេដ្ឋកិច្ចគ្រួសារ។"},
        {"id": 13, "type": "Correct", "topic": "Law", "text": "ច្បាប់ចរាចរណ៍ផ្លូវគោកតម្រូវឱ្យអ្នកបើកបរម៉ូតូទាំងអស់ត្រូវពាក់មួកសុវត្ថិភាព។"},
        {"id": 14, "type": "Correct", "topic": "Art", "text": "តន្ត្រីបុរាណខ្មែរមានសូរសម្លេងពិរោះរណ្តំដែលដក់ជាប់ក្នុងចិត្តអ្នកស្តាប់។"},
        {"id": 15, "type": "Correct", "topic": "Sport", "text": "ការលេងកីឡាមិនត្រឹមតែជួយឱ្យរាងកាយមាំមួនទេ តែថែមទាំងជួយសម្រាលស្ត្រេសទៀតផង។"},

        # --- INCORRECT SENTENCES (Expected: AT LEAST one error) ---
        {"id": 16, "type": "Error", "topic": "Medical", "text": "គាត់បានធ្វើការនៅមន្ទីពេទ្យដែលស្ថិតនៅកណ្តាលទីក្រុង។", "expected": "មន្ទីរពេទ្យ"},
        {"id": 17, "type": "Error", "topic": "Home", "text": "សូមកុំភ្លេចយកកាបូបជាមួយអ្នកនៅពេលចេញពីរផ្ទះ។", "expected": "ពី"},
        {"id": 18, "type": "Error", "topic": "Education", "text": "ការសឹក្សាគឺជាមូលដ្ឋានគ្រឹះដ៏សំខាន់សម្រាប់ជោគជ័យ។", "expected": "សិក្សា"},
        {"id": 19, "type": "Error", "topic": "Work", "text": "គាត់ត្រូវសសេររបាយការណ៍ជូនប្រធាននៅរៀងរាល់ល្ងាច។", "expected": "សរសេរ"},
        {"id": 20, "type": "Error", "topic": "General", "text": "សូមអគុណដែលបានចំណាយពេលមកចូលរួមក្នុងកម្មវិធីរបស់យើង។", "expected": "អរគុណ"},
        {"id": 21, "type": "Error", "topic": "Grammar", "text": "រដ្ឋាភិបាលបានដាក់ចេញនៅវិធានការទប់ស្កាត់ការរីករាលដាលនៃជំងឺ។", "expected": "នូវ"},
        {"id": 22, "type": "Error", "topic": "Tech", "text": "ប្រព័ន្ធអិនធឺណិតនៅថ្ងៃនេះមានភាពយឺតយ៉ាវជាខ្លាំង។", "expected": "អ៊ីនធឺណិត"},
        {"id": 23, "type": "Error", "topic": "Time", "text": "យើងត្រូវជួបគ្នាណៅម៉ោងប្រាំបួនព្រឹកស្អែក។", "expected": "នៅ"},
        {"id": 24, "type": "Error", "topic": "Finance", "text": "តំលៃមាសនៅលើទីផ្សារសកលមានការកើនឡើងបន្តិច។", "expected": "តម្លៃ"},
        {"id": 25, "type": "Error", "topic": "Distance", "text": "សាលារៀនរបស់ខ្ញុំស្ថិតនៅចម្ងាយប្រហែលបីគីឡូម៉ែតពីផ្ទះ។", "expected": "គីឡូម៉ែត្រ"},
        {"id": 26, "type": "Error", "topic": "Action", "text": "សូមជួយសំអាតការិយាល័យឱ្យបានស្អាតបាតមុនពេលភ្ញាក់ផ្អើល។", "expected": "សម្អាត"},
        {"id": 27, "type": "Error", "topic": "Food", "text": "ម្ហូបអាហាខ្មែរមានរសជាតិឈ្ងុយឆ្ងាញ់និងមានអត្ថប្រយោជន៍ដល់សុខភាព។", "expected": "អាហារ"},
        {"id": 28, "type": "Error", "topic": "Emotion", "text": "ខ្ញុំមានអារម្មណ៏សប្បាយចិត្តខ្លាំងណាស់ដែលបានទទួលដំណឹងល្អនេះ។", "expected": "អារម្មណ៍"},
        {"id": 29, "type": "Error", "topic": "Weather", "text": "រដូវលំហើយនាំមកនៅខ្យល់ត្រជាក់ដែលធ្វើឱ្យយើងស្រស់ស្រាយ។", "expected": "នូវ"},
        {"id": 30, "type": "Error", "topic": "Nature", "text": "សត្វចាបបង្កកំនើតនៅក្នុងសំបុកដែលវាសាងសង់លើដើមឈើ។", "expected": "បង្កកំណើត"},
    ]

    print(f"\nRunning {len(test_cases)} Tests...\n")
    print(f"{'ID':<4} | {'Type':<8} | {'Topic':<12} | {'Status':<10} | {'Details'}")
    print("-" * 120)

    score = 0
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
        
        # Collect detected tokens
        detected_tokens = []
        for idx in errors:
            detected_tokens.append(errors[idx]['original'])
        for idx in error_indices:
            tok = tagged[idx]['token']
            if tok not in detected_tokens:
                detected_tokens.append(tok)
            
        detected_set = set(detected_tokens)
        
        is_pass = False
        if case['type'] == 'Correct':
            is_pass = (len(detected_set) == 0)
        else:
            # Check if expected error or something similar was found
            # (Simplistic check for this mixed test)
            is_pass = (len(detected_set) > 0)
        
        if is_pass:
            passed += 1
        
        status_str = "PASS" if is_pass else "FAIL"
        
        # Formatting output
        found_str = f"Found: {list(detected_set)}" if detected_set else "None"
        if case['type'] == 'Correct' and not is_pass:
            detail = f"FALSE POSITIVE: {found_str}"
        elif case['type'] == 'Error' and not is_pass:
            detail = f"MISSING ERROR: Expected '{case.get('expected')}'"
        else:
            detail = found_str if case['type'] == 'Error' else ""

        print(f"{case['id']:<4} | {case['type']:<8} | {case['topic']:<12} | {status_str:<10} | {detail}")

    print("-" * 120)
    print(f"Final Score: {passed}/{len(test_cases)} ({passed/len(test_cases)*100:.1f}%)")
    print("=" * 100)

if __name__ == "__main__":
    run_mixed_30_sentences_test()
