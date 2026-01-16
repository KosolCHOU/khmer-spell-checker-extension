
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

def run_stress_test_correct_sentences():
    print("=" * 100)
    print("RUNNING KHMER SPELL CHECKER STRESS TEST: 30 COMPLEX CORRECT SENTENCES")
    print("Goal: Verify zero false positives (No errors detected in correct text)")
    print("=" * 100)
    
    print("Initializing Spell Checker Data...")
    start_load = time.time()
    word_set, word_to_pos, word_freq, _ = SpellCheckerData.build_tables()
    word_list = SpellCheckerData.get_word_list()
    bigrams = SpellCheckerData.load_bigrams()
    print(f"Data loaded in {time.time() - start_load:.2f}s")
    
    test_cases = [
        {"id": 1, "topic": "Law", "text": "នីតិបុគ្គលនៃនីតិសាធារណៈមានកាតព្វកិច្ចបម្រើផលប្រយោជន៍រួម។"},
        {"id": 2, "topic": "Science", "text": "បាតុភូតរូបវិទ្យានៃការសាយភាយពន្លឺក្នុងបរិយាកាសបង្កើតឱ្យមានពណ៌មេឃ។"},
        {"id": 3, "topic": "Medicine", "text": "ការវះកាត់ដោយប្រើបច្ចេកវិទ្យាឡាស៊ែរជួយកាត់បន្ថយការបាត់បង់ឈាមរបស់អ្នកជំងឺ។"},
        {"id": 4, "topic": "Philosophy", "text": "ទស្សនវិជ្ជានៃអត្ថិភាពនិយមសង្កត់ធ្ងន់លើសេរីភាពនិងការទទួលខុសត្រូវរបស់បុគ្គល។"},
        {"id": 5, "topic": "Royal", "text": "ព្រះករុណាព្រះបាទសម្តេចព្រះបរមនាថនរោត្តមសីហមុនីទ្រង់សព្វព្រះរាជហឫទ័យ។"},
        {"id": 6, "topic": "Finance", "text": "អតិផរណាជះឥទ្ធិពលអាក្រក់ដល់អំណាចទិញរបស់ប្រជាជនដែលមានចំណូលទាប។"},
        {"id": 7, "topic": "Diplomacy", "text": "ទំនាក់ទំនងការទូតរវាងប្រទេសទាំងពីរត្រូវបានពង្រឹងតាមរយៈកិច្ចសហប្រតិបត្តិការ។"},
        {"id": 8, "topic": "Archaeology", "text": "ការជីកកកាយបុរាណវត្ថុវិទ្យានៅតំបន់អង្គរបានបង្ហាញនូវភស្តុតាងថ្មីៗនៃប្រវត្តិសាស្ត្រ។"},
        {"id": 9, "topic": "Environment", "text": "ការប្រែប្រួលអាកាសធាតុបង្កឱ្យមានគ្រោះមហន្តរាយធម្មជាតិកាន់តែខ្លាំងក្លានិងញឹកញាប់។"},
        {"id": 10, "topic": "Education", "text": "ការអប់រំពេញមួយជីវិតគឺជាគន្លឹះក្នុងការអភិវឌ្ឍសមត្ថភាពក្នុងយុគសម័យឌីជីថល។"},
        {"id": 11, "topic": "Grammar (នូវ)", "text": "សហគ្រាសត្រូវអនុវត្តនូវវិធានសុវត្ថិភាពការងារឱ្យបានខ្ជាប់ខ្ជួនបំផុត។"},
        {"id": 12, "topic": "Grammar (នៅ)", "text": "សិស្សានុសិស្សកំពុងរង់ចាំលទ្ធផលប្រឡងនៅមុខក្តារខៀននៃសាលារៀន។"},
        {"id": 13, "topic": "Grammar (នឹង)", "text": "យើងនឹងខិតខំប្រឹងប្រែងឱ្យអស់ពីសមត្ថភាពដើម្បីសម្រេចបាននូវគោលដៅ។"},
        {"id": 14, "topic": "Grammar (និង)", "text": "ឪពុកម្តាយនិងអាណាព្យាបាលមានតួនាទីសំខាន់ក្នុងការអប់រំកូនចៅនៅផ្ទះ។"},
        {"id": 15, "topic": "Technical", "text": "ការកំណត់រចនាសម្ព័ន្ធប្រព័ន្ធសុវត្ថិភាពបណ្តាញតម្រូវឱ្យមានការយកចិត្តទុកដាក់ខ្ពស់។"},
        {"id": 16, "topic": "Literature", "text": "អក្សរសិល្ប៍ខ្មែរឆ្លុះបញ្ចាំងពីតថភាពសង្គមនិងវប្បធម៌ដ៏សម្បូរបែបរបស់ជាតិ។"},
        {"id": 17, "topic": "Agriculture", "text": "ប្រព័ន្ធធារាសាស្ត្រទំនើបជួយឱ្យកសិករអាចបង្កបង្កើនផលបានច្រើនដងក្នុងមួយឆ្នាំ។"},
        {"id": 18, "topic": "Spirituality", "text": "ការធ្វើសមាធិជួយឱ្យចិត្តស្ងប់និងបង្កើនការយល់ដឹងអំពីខ្លួនឯងកាន់តែច្បាស់។"},
        {"id": 19, "topic": "Architecture", "text": "ស្ថាបត្យកម្មខ្មែរមានលក្ខណៈពិសេសដែលរួមបញ្ចូលគ្នារវាងសិល្បៈនិងជំនឿសាសនា។"},
        {"id": 20, "topic": "Sociology", "text": "សមភាពយេនឌ័រគឺជាកត្តាចាំបាច់សម្រាប់ការអភិវឌ្ឍសង្គមប្រកបដោយចីរភាព។"},
        {"id": 21, "topic": "Sports", "text": "កីឡាការិនីកម្ពុជាបានឈ្នះមេដាយមាសក្នុងការប្រកួតកីឡាអាស៊ីអាគ្នេយ៍ថ្មីៗនេះ។"},
        {"id": 22, "topic": "Information", "text": "ការយល់ដឹងអំពីប្រព័ន្ធផ្សព្វផ្សាយជួយឱ្យយើងអាចវិភាគព័ត៌មានបានត្រឹមត្រូវ។"},
        {"id": 23, "topic": "Space", "text": "តារាវិទូប្រើប្រាស់តេឡេស្កុបវិទ្យុដើម្បីអង្កេតមើលកាឡាក់ស៊ីដែលនៅឆ្ងាយដាច់ស្រយាល។"},
        {"id": 24, "topic": "Economics", "text": "ការវិនិយោគផ្ទាល់ពីបរទេសបានរួមចំណែកយ៉ាងសំខាន់ដល់កំណើនសេដ្ឋកិច្ចជាតិ។"},
        {"id": 25, "topic": "Judiciary", "text": "ចៅក្រមត្រូវមានឯករាជ្យភាពពេញលេញក្នុងការផ្តល់យុត្តិធម៌ជូនប្រជាពលរដ្ឋ។"},
        {"id": 26, "topic": "Logistics", "text": "ខ្សែសង្វាក់ផ្គត់ផ្គង់សកលត្រូវបានរំខានដោយសារការរីករាលដាលនៃជំងឺឆ្លង។"},
        {"id": 27, "topic": "Psychology", "text": "សុខភាពផ្លូវចិត្តមានសារៈសំខាន់មិនចាញ់សុខភាពផ្លូវកាយនោះឡើយក្នុងជីវិតរស់នៅ។"},
        {"id": 28, "topic": "Botany", "text": "រុក្ខជាតិប្រើប្រាស់ពន្លឺព្រះអាទិត្យដើម្បីធ្វើរស្មីសំយោគនិងបង្កើតជាអាហារ។"},
        {"id": 29, "topic": "Engineering", "text": "វិស្វករកំពុងសិក្សាអំពីលទ្ធភាពនៃការសាងសង់ស្ពានឆ្លងកាត់ទន្លេមេគង្គថ្មីមួយទៀត។"},
        {"id": 30, "topic": "Art", "text": "គំនូរបុរាណតាមជញ្ជាំងវត្តអារាមគឺជាបេតិកភណ្ឌសិល្បៈដ៏មានតម្លៃរបស់ខ្មែរ។"},
    ]

    print(f"\nRunning {len(test_cases)} Tests...\n")
    print(f"{'ID':<4} | {'Topic':<15} | {'Status':<10} | {'Found Errors'}")
    print("-" * 120)

    false_positives = 0
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
        
        # Stress test: Pass if NO errors detected
        is_pass = len(detected_set) == 0
        
        if is_pass:
            passed += 1
        else:
            false_positives += 1
        
        status_str = "PASS" if is_pass else "FAIL"
        detected_str = f"{list(detected_set)}" if not is_pass else ""

        print(f"{case['id']:<4} | {case['topic']:<15} | {status_str:<10} | {detected_str}")

    print("-" * 120)
    print(f"Stress Test Result: {passed}/{len(test_cases)} Passed (No False Positives)")
    print(f"False Positive Rate: {false_positives/len(test_cases)*100:.1f}%")
    print("=" * 100)

if __name__ == "__main__":
    run_stress_test_correct_sentences()
