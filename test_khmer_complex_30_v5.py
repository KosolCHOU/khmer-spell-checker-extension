
import sys
import time
from typing import List, Dict
import os

# Ensure the project root is in sys.path if running directly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from keyez.landing.spell_checker_advanced import (
    SpellCheckerData, 
    segment_text, 
    pos_tag_tokens, 
    detect_grammar_errors, 
    detect_error_slots,
    detect_semantic_suspicion,
    COMMON_TYPOS
)

def run_complex_sentences_test_v5():
    print("Initializing Spell Checker Data...")
    start_load = time.time()
    # Initialize data
    word_set, word_to_pos, word_freq, _ = SpellCheckerData.build_tables()
    word_list = SpellCheckerData.get_word_list()
    bigrams = SpellCheckerData.load_bigrams()
    trigrams = SpellCheckerData.load_trigrams()
    print(f"Data loaded in {time.time() - start_load:.2f}s")
    
    # 30 New Complex Sentences (Set 5 - Tourism, Real Estate, Diplomacy, Logistics)
    test_cases = [
        # --- Tourism & Hospitality ---
        {
            "id": 1, "type": "Correct", "topic": "Tourism",
            "text": "វិស័យទេសចរណ៍ត្រូវបានចាត់ទុកជាមាសបៃតងដែលចូលរួមចំណែកយ៉ាងសំខាន់ក្នុងការអភិវឌ្ឍសេដ្ឋកិច្ចជាតិ។",
            "expected_errors": []
        },
        {
            "id": 2, "type": "Correct", "topic": "Tourism",
            "text": "រមណីយដ្ឋានធម្មជាតិនិងវប្បធម៌ជាច្រើនកំពុងទាក់ទាញភ្ញៀវទេសចរជាតិនិងអន្តរជាតិឱ្យមកទស្សនាកម្សាន្ត។",
            "expected_errors": []
        },
        {
            "id": 3, "type": "Correct", "topic": "Tourism",
            "text": "ការផ្តល់សេវាកម្មបដិសណ្ឋារកិច្ចល្អគឺជាកត្តាគន្លឹះក្នុងការធ្វើឱ្យភ្ញៀវទេសចរមានការពេញចិត្តនិងចង់ត្រឡប់មកវិញ។",
            "expected_errors": []
        },
        {
            "id": 4, "type": "Correct", "topic": "Tourism",
            "text": "ក្រសួងទេសចរណ៍បានដាក់ចេញនូវយុទ្ធនាការផ្សព្វផ្សាយសក្តានុពលទេសចរណ៍កម្ពុជានៅលើឆាកអន្តរជាតិ។",
            "expected_errors": []
        },
        {
            "id": 5, "type": "Correct", "topic": "Tourism",
            "text": "ការអភិវឌ្ឍទេសចរណ៍សហគមន៍ជួយបង្កើតប្រាក់ចំណូលផ្ទាល់ដល់ប្រជាពលរដ្ឋនៅតាមតំបន់ដាច់ស្រយាល។",
            "expected_errors": []
        },

        # --- Real Estate & Urban Planning ---
        {
            "id": 6, "type": "Correct", "topic": "Real Estate",
            "text": "វិស័យអចលនទ្រព្យនៅកម្ពុជាកំពុងមានសន្ទុះរីកចម្រើនយ៉ាងខ្លាំងជាពិសេសនៅរាជធានីភ្នំពេញនិងក្រុងព្រះសីហនុ។",
            "expected_errors": []
        },
        {
            "id": 7, "type": "Correct", "topic": "Real Estate",
            "text": "ការរៀបចំផែនការមេសម្រាប់ការអភិវឌ្ឍទីក្រុងគឺចាំបាច់ណាស់ដើម្បីធានានូវនិរន្តរភាពនិងសោភ័ណភាព។",
            "expected_errors": []
        },
        {
            "id": 8, "type": "Correct", "topic": "Real Estate",
            "text": "គម្រោងសាងសង់ខុនដូនិងបុរីជាច្រើនកំពុងលេចចេញជារូបរាងឡើងដើម្បីឆ្លើយតបនឹងតម្រូវការលំនៅឋាន។",
            "expected_errors": []
        },
        {
            "id": 9, "type": "Correct", "topic": "Real Estate",
            "text": "ការវិនិយោគលើដីធ្លីទាមទារឱ្យមានការសិក្សាច្បាស់លាស់អំពីច្បាប់កម្មសិទ្ធិនិងសក្តានុពលនៃតំបន់នោះ។",
            "expected_errors": []
        },
        {
            "id": 10, "type": "Correct", "topic": "Real Estate",
            "text": "ស្ថាបត្យកម្មនៃអគារខ្ពស់ៗបានផ្លាស់ប្តូរមុខមាត់ទីក្រុងឱ្យកាន់តែមានភាពស៊ីវិល័យនិងទំនើបកម្ម។",
            "expected_errors": []
        },

        # --- Diplomacy & International Relations ---
        {
            "id": 11, "type": "Correct", "topic": "Diplomacy",
            "text": "កម្ពុជាប្រកាន់ខ្ជាប់នូវគោលនយោបាយការបរទេសឯករាជ្យដោយផ្អែកលើច្បាប់អន្តរជាតិនិងការគោរពអធិបតេយ្យភាព។",
            "expected_errors": []
        },
        {
            "id": 12, "type": "Correct", "topic": "Diplomacy",
            "text": "កិច្ចសហប្រតិបត្តិការទ្វេភាគីនិងពហុភាគីត្រូវបានពង្រឹងដើម្បីផលប្រយោជន៍រួមនិងសន្តិភាពក្នុងតំបន់។",
            "expected_errors": []
        },
        {
            "id": 13, "type": "Correct", "topic": "Diplomacy",
            "text": "ដំណើរទស្សនកិច្ចផ្លូវការរបស់ថ្នាក់ដឹកនាំជាន់ខ្ពស់បានបើកទំព័រថ្មីនៃទំនាក់ទំនងមិត្តភាពរវាងប្រទេសទាំងពីរ។",
            "expected_errors": []
        },
        {
            "id": 14, "type": "Correct", "topic": "Diplomacy",
            "text": "កម្ពុជាបានចូលរួមយ៉ាងសកម្មនៅក្នុងបេសកកម្មរក្សាសន្តិភាពរបស់អង្គការសហប្រជាជាតិនៅតាមបណ្តាប្រទេសនានា។",
            "expected_errors": []
        },
        {
            "id": 15, "type": "Correct", "topic": "Diplomacy",
            "text": "វេទិកាអាស៊ានគឺជាយន្តការដ៏សំខាន់សម្រាប់ការដោះស្រាយបញ្ហាតំបន់និងការជំរុញសមាហរណកម្មសេដ្ឋកិច្ច។",
            "expected_errors": []
        },

        # --- Logistics & Infrastructure ---
        {
            "id": 16, "type": "Correct", "topic": "Logistics",
            "text": "ការតភ្ជាប់ហេដ្ឋារចនាសម្ព័ន្ធផ្លូវថ្នល់និងស្ពានគឺជាសរសៃឈាមសេដ្ឋកិច្ចដែលមិនអាចខ្វះបានសម្រាប់ការដឹកជញ្ជូន។",
            "expected_errors": []
        },
        {
            "id": 17, "type": "Correct", "topic": "Logistics",
            "text": "គម្រោងផ្លូវល្បឿនលឿនភ្នំពេញក្រុងព្រះសីហនុបានជួយកាត់បន្ថយពេលវេលាធ្វើដំណើរនិងចំណាយលើការដឹកជញ្ជូនទំនិញ។",
            "expected_errors": []
        },
        {
            "id": 18, "type": "Correct", "topic": "Logistics",
            "text": "កំពង់ផែស្វយ័តក្រុងព្រះសីហនុគឺជាច្រកទ្វារសេដ្ឋកិច្ចដ៏សំខាន់សម្រាប់ការនាំចេញនិងនាំចូលទំនិញអន្តរជាតិ។",
            "expected_errors": []
        },
        {
            "id": 19, "type": "Correct", "topic": "Logistics",
            "text": "ការអភិវឌ្ឍប្រព័ន្ធដឹកជញ្ជូនសាធារណៈនៅក្នុងរាជធានីភ្នំពេញជួយកាត់បន្ថយការកកស្ទះចរាចរណ៍និងការបំពុលបរិស្ថាន។",
            "expected_errors": []
        },
        {
            "id": 20, "type": "Correct", "topic": "Logistics",
            "text": "អាកាសយានដ្ឋានអន្តរជាតិថ្មីនឹងបង្កើនសមត្ថភាពទទួលអ្នកដំណើរនិងជើងហោះហើរពីគ្រប់ទិសទីនៃពិភពលោក។",
            "expected_errors": []
        },

        # --- Vocational Training & Employment ---
        {
            "id": 21, "type": "Correct", "topic": "Employment",
            "text": "ទីផ្សារការងារបច្ចុប្បន្នទាមទារឱ្យយុវជនមានជំនាញបច្ចេកទេសច្បាស់លាស់និងសមត្ថភាពភាសាបរទេស។",
            "expected_errors": []
        },
        {
            "id": 22, "type": "Correct", "topic": "Employment",
            "text": "ក្រសួងការងារបានខិតខំស្វែងរកឱកាសការងារជូនពលករខ្មែរទាំងនៅក្នុងប្រទេសនិងនៅក្រៅប្រទេសដោយស្របច្បាប់។",
            "expected_errors": []
        },
        {
            "id": 23, "type": "Correct", "topic": "Employment",
            "text": "ការបណ្តុះបណ្តាលភាពជាអ្នកដឹកនាំនិងជំនាញទន់គឺចាំបាច់សម្រាប់ការរីកចម្រើនក្នុងអាជីពការងារ។",
            "expected_errors": []
        },
        {
            "id": 24, "type": "Correct", "topic": "Employment",
            "text": "សហគ្រិនភាពគឺជាកម្លាំងចលករដ៏សំខាន់ក្នុងការបង្កើតការងារថ្មីនិងការច្នៃប្រឌិតនៅក្នុងវិស័យធុរកិច្ច។",
            "expected_errors": []
        },
        {
            "id": 25, "type": "Correct", "topic": "Employment",
            "text": "កម្មករនិយោជិតមានសិទ្ធិទទួលបានប្រាក់ឈ្នួលសមរម្យនិងលក្ខខណ្ឌការងារល្អប្រសើរស្របតាមច្បាប់ការងារ។",
            "expected_errors": []
        },

        # --- Disaster Management ---
        {
            "id": 26, "type": "Correct", "topic": "Disaster",
            "text": "គណៈកម្មាធិការជាតិគ្រប់គ្រងគ្រោះមហន្តរាយបានត្រៀមលក្ខណៈរួចរាល់ដើម្បីឆ្លើយតបនឹងគ្រោះទឹកជំនន់។",
            "expected_errors": []
        },
        {
            "id": 27, "type": "Correct", "topic": "Disaster",
            "text": "ការផ្តល់ជំនួយសង្គ្រោះបន្ទាន់ដល់ជនរងគ្រោះដោយសារគ្រោះធម្មជាតិគឺជាកិច្ចការមនុស្សធម៌ដ៏ចាំបាច់បំផុត។",
            "expected_errors": []
        },
        {
            "id": 28, "type": "Correct", "topic": "Disaster",
            "text": "ប្រព័ន្ធប្រកាសអាសន្នជាមុនត្រូវបានដំឡើងដើម្បីជូនដំណឹងដល់ប្រជាពលរដ្ឋឱ្យមានការប្រុងប្រយ័ត្នខ្ពស់។",
            "expected_errors": []
        },
        {
            "id": 29, "type": "Correct", "topic": "Disaster",
            "text": "ការស្តារឡើងវិញនូវហេដ្ឋារចនាសម្ព័ន្ធដែលខូចខាតក្រោយគ្រោះមហន្តរាយទាមទារឱ្យមានថវិកានិងពេលវេលាច្រើន។",
            "expected_errors": []
        },
        {
            "id": 30, "type": "Correct", "topic": "Disaster",
            "text": "ការចូលរួមរបស់សហគមន៍ក្នុងការកាត់បន្ថយហានិភ័យគ្រោះមហន្តរាយគឺជាយុទ្ធសាស្ត្រដ៏មានប្រសិទ្ធភាព។",
            "expected_errors": []
        }
    ]

    passed_count = 0
    total_count = len(test_cases)
    
    print(f"\nRunning {total_count} Complex Test Cases (Set 5)...")
    print("="*60)

    for case in test_cases:
        text = case["text"]
        expected = case["expected_errors"]
        
        # 1. Segment
        tokens = segment_text(text)
        
        # 2. POS Tag
        pos_tags = pos_tag_tokens(tokens, word_to_pos, word_set)
        
        # 3. Detect Errors
        errors = {}
        
        # Check grammar
        detect_grammar_errors(pos_tags, errors)
        
        # Check dictionary/typos
        detect_error_slots(pos_tags, word_set, word_list, bigrams, trigrams, errors, word_freq)
        
        # Check semantic suspicion
        semantic_errors = detect_semantic_suspicion(pos_tags, bigrams, trigrams, word_list)
        errors.update(semantic_errors)
        
        # Evaluate
        is_correct = False
        if len(expected) == 0:
            if len(errors) == 0:
                is_correct = True
        else:
            # For now, we are mostly testing False Positives, so we expect 0 errors for correct sentences
            pass

        status = "PASS" if is_correct else "FAIL"
        if is_correct:
            passed_count += 1
        
        print(f"ID {case['id']} [{case['topic']}]: {status}")
        print(f"Text: {text}")
        if not is_correct:
            print(f"  Expected: {expected}")
            for idx, err in errors.items():
                print(f"   - {err.get('type', 'Unknown')}: {err.get('original', '')} -> {err.get('suggestions', [])} ({err.get('message', '')})")
        print("-" * 60)

    print(f"\nTest Summary: {passed_count}/{total_count} Passed")
    accuracy = (passed_count / total_count) * 100
    print(f"Accuracy: {accuracy:.2f}%")
    
    if accuracy >= 90:
        print("SUCCESS: Accuracy is >= 90%")
    else:
        print("FAILURE: Accuracy is < 90%")

if __name__ == "__main__":
    run_complex_sentences_test_v5()
