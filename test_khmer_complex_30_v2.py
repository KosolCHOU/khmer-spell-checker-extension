
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

def run_complex_sentences_test_v2():
    print("Initializing Spell Checker Data...")
    start_load = time.time()
    # Initialize data
    word_set, word_to_pos, word_freq, _ = SpellCheckerData.build_tables()
    word_list = SpellCheckerData.get_word_list()
    bigrams = SpellCheckerData.load_bigrams()
    trigrams = SpellCheckerData.load_trigrams()
    print(f"Data loaded in {time.time() - start_load:.2f}s")
    
    # 30 New Complex Sentences
    test_cases = [
        # --- Science & Astronomy ---
        {
            "id": 1, "type": "Correct", "topic": "Science",
            "text": "ការរកឃើញភពថ្មីៗនៅក្នុងប្រព័ន្ធព្រះអាទិត្យបានធ្វើឱ្យអ្នកវិទ្យាសាស្ត្រមានការភ្ញាក់ផ្អើលយ៉ាងខ្លាំង។",
            "expected_errors": []
        },
        {
            "id": 2, "type": "Correct", "topic": "Science",
            "text": "បាតុភូតគ្រោះធម្មជាតិដូចជាការរញ្ជួយដីនិងព្យុះសង្ឃរាគឺជាបញ្ហាដែលពិបាកនឹងព្យាករណ៍ទុកជាមុន។",
            "expected_errors": []
        },
        {
            "id": 3, "type": "Correct", "topic": "Science",
            "text": "ការពិសោធន៍ទៅលើហ្សែនរបស់មនុស្សអាចនាំមកនូវការផ្លាស់ប្តូរដ៏ធំមួយនៅក្នុងវិស័យវេជ្ជសាស្ត្រទំនើប។",
            "expected_errors": []
        },

        # --- Literature & Arts ---
        {
            "id": 4, "type": "Correct", "topic": "Literature",
            "text": "ស្នាដៃអក្សរសិល្ប៍ខ្មែររឿងទុំទាវបានឆ្លុះបញ្ចាំងពីតថភាពសង្គមនិងការតស៊ូដើម្បីសេចក្តីស្នេហាស្មោះស្ម័គ្រ។",
            "expected_errors": []
        },
        {
            "id": 5, "type": "Correct", "topic": "Literature",
            "text": "កវីនិពន្ធល្បីៗបានប្រើប្រាស់ពាក្យពេចន៍យ៉ាងប៉ិនប្រសប់ដើម្បីរៀបរាប់ពីសម្រស់ធម្មជាតិនិងជីវិតជនបទ។",
            "expected_errors": []
        },
        {
            "id": 6, "type": "Correct", "topic": "Arts",
            "text": "សិល្បៈចម្លាក់លើប្រាក់និងស្ពាន់គឺជាជំនាញបុរាណដែលត្រូវបានផ្ទេរពីមួយជំនាន់ទៅមួយជំនាន់។",
            "expected_errors": []
        },

        # --- Sports ---
        {
            "id": 7, "type": "Correct", "topic": "Sports",
            "text": "កីឡាករជម្រើសជាតិកម្ពុជាបានខិតខំប្រឹងប្រែងហ្វឹកហាត់យ៉ាងខ្លាំងដើម្បីដណ្តើមមេដាយមាសជូនជាតិមាតុភូមិ។",
            "expected_errors": []
        },
        {
            "id": 8, "type": "Correct", "topic": "Sports",
            "text": "ការរៀបចំព្រឹត្តិការណ៍កីឡាស៊ីហ្គេមលើកទី៣២គឺជាមោទនភាពដ៏ធំធេងសម្រាប់ប្រជាជនកម្ពុជាទាំងមូល។",
            "expected_errors": []
        },
        {
            "id": 9, "type": "Correct", "topic": "Sports",
            "text": "កីឡាបាល់ទាត់ទទួលបានការគាំទ្រយ៉ាងពេញទំហឹងពីសំណាក់យុវជននិងមហាជននៅទូទាំងប្រទេស។",
            "expected_errors": []
        },

        # --- Tourism ---
        {
            "id": 10, "type": "Correct", "topic": "Tourism",
            "text": "រមណីយដ្ឋានធម្មជាតិនៅខេត្តមណ្ឌលគិរីទាក់ទាញភ្ញៀវទេសចរជាតិនិងអន្តរជាតិមកកម្សាន្តយ៉ាងច្រើនកុះករ។",
            "expected_errors": []
        },
        {
            "id": 11, "type": "Correct", "topic": "Tourism",
            "text": "ការអភិវឌ្ឍវិស័យទេសចរណ៍អេកូឡូស៊ីជួយលើកកម្ពស់ជីវភាពសហគមន៍មូលដ្ឋាននិងការពារធនធានធម្មជាតិ។",
            "expected_errors": []
        },
        {
            "id": 12, "type": "Correct", "topic": "Tourism",
            "text": "ឆ្នេរសមុទ្រកម្ពុជាត្រូវបានប្រសិទ្ធនាមថាជាតារារះនៅទិសនិរតីដែលមានសម្រស់ស្រស់ស្អាតដាច់គេ។",
            "expected_errors": []
        },

        # --- Agriculture ---
        {
            "id": 13, "type": "Correct", "topic": "Agriculture",
            "text": "កសិករនៅខេត្តបាត់ដំបងកំពុងមមាញឹកក្នុងការប្រមូលផលស្រូវវស្សាដើម្បីផ្គត់ផ្គង់ទីផ្សារក្នុងស្រុកនិងនាំចេញ។",
            "expected_errors": []
        },
        {
            "id": 14, "type": "Correct", "topic": "Agriculture",
            "text": "ការដាំដំណាំម្រេចនៅកំពតទទួលបានការទទួលស្គាល់ជាផលិតផលសម្គាល់ភូមិសាស្ត្រដែលមានគុណភាពខ្ពស់។",
            "expected_errors": []
        },
        {
            "id": 15, "type": "Correct", "topic": "Agriculture",
            "text": "ក្រសួងកសិកម្មបានណែនាំឱ្យកសិករប្រើប្រាស់ពូជស្រូវដែលធន់នឹងអាកាសធាតុដើម្បីទទួលបានទិន្នផលខ្ពស់។",
            "expected_errors": []
        },

        # --- Infrastructure ---
        {
            "id": 16, "type": "Correct", "topic": "Infrastructure",
            "text": "ស្ពានមិត្តភាពកម្ពុជាជប៉ុនបានជួយសម្រួលដល់ការធ្វើដំណើរនិងការដឹកជញ្ជូនទំនិញឆ្លងកាត់ទន្លេមេគង្គ។",
            "expected_errors": []
        },
        {
            "id": 17, "type": "Correct", "topic": "Infrastructure",
            "text": "គម្រោងសាងសង់ផ្លូវល្បឿនលឿនភ្នំពេញក្រុងព្រះសីហនុបានកាត់បន្ថយពេលវេលាធ្វើដំណើរយ៉ាងច្រើន។",
            "expected_errors": []
        },
        {
            "id": 18, "type": "Correct", "topic": "Infrastructure",
            "text": "ការផ្គត់ផ្គង់ទឹកស្អាតនិងអគ្គិសនីនៅតំបន់ជនបទគឺជាគោលដៅសំខាន់របស់រាជរដ្ឋាភិបាលក្នុងអាណត្តិនេះ។",
            "expected_errors": []
        },

        # --- Diplomacy ---
        {
            "id": 19, "type": "Correct", "topic": "Diplomacy",
            "text": "កម្ពុជាប្រកាន់ខ្ជាប់នូវគោលនយោបាយការបរទេសឯករាជ្យដោយផ្អែកលើច្បាប់អន្តរជាតិនិងការគោរពគ្នាទៅវិញទៅមក។",
            "expected_errors": []
        },
        {
            "id": 20, "type": "Correct", "topic": "Diplomacy",
            "text": "ដំណើរទស្សនកិច្ចផ្លូវការរបស់ប្រមុខរដ្ឋបរទេសបានពង្រឹងចំណងមិត្តភាពនិងកិច្ចសហប្រតិបត្តិការទ្វេភាគី។",
            "expected_errors": []
        },
        {
            "id": 21, "type": "Correct", "topic": "Diplomacy",
            "text": "កម្ពុជាបានចូលរួមយ៉ាងសកម្មនៅក្នុងបេសកកម្មរក្សាសន្តិភាពរបស់អង្គការសហប្រជាជាតិនៅតាមបណ្ដាប្រទេសនានា។",
            "expected_errors": []
        },

        # --- Business ---
        {
            "id": 22, "type": "Correct", "topic": "Business",
            "text": "សហគ្រិនវ័យក្មេងជាច្រើនកំពុងបង្កើតអាជីវកម្មថ្មីៗដែលផ្តោតលើបច្ចេកវិទ្យានិងនវានុវត្តន៍។",
            "expected_errors": []
        },
        {
            "id": 23, "type": "Correct", "topic": "Business",
            "text": "ការចុះបញ្ជីពាណិជ្ជកម្មតាមប្រព័ន្ធអនឡាញបានជួយកាត់បន្ថយការចំណាយនិងពេលវេលាសម្រាប់អ្នកវិនិយោគ។",
            "expected_errors": []
        },
        {
            "id": 24, "type": "Correct", "topic": "Business",
            "text": "វិស័យអចលនទ្រព្យនៅរាជធានីភ្នំពេញនៅតែបន្តរីកចម្រើនទោះបីជាមានបញ្ហាប្រឈមសេដ្ឋកិច្ចសកលក៏ដោយ។",
            "expected_errors": []
        },

        # --- Tradition ---
        {
            "id": 25, "type": "Correct", "topic": "Tradition",
            "text": "ពិធីមង្គលការតាមបែបប្រពៃណីខ្មែរមានច្រើនដំណាក់កាលដែលបង្ហាញពីភាពថ្លៃថ្នូរនិងការគោរពដឹងគុណ។",
            "expected_errors": []
        },
        {
            "id": 26, "type": "Correct", "topic": "Tradition",
            "text": "ការស្លៀកពាក់សម្លៀកបំពាក់បុរាណក្នុងពិធីបុណ្យជាតិបានក្លាយជាការពេញនិយមក្នុងចំណោមយុវវ័យសម័យថ្មី។",
            "expected_errors": []
        },
        {
            "id": 27, "type": "Correct", "topic": "Tradition",
            "text": "ពិធីបុណ្យចូលឆ្នាំថ្មីប្រពៃណីជាតិគឺជាឱកាសសម្រាប់ជួបជុំក្រុមគ្រួសារនិងលេងល្បែងប្រជាប្រិយយ៉ាងសប្បាយរីករាយ។",
            "expected_errors": []
        },

        # --- Philosophy/General ---
        {
            "id": 28, "type": "Correct", "topic": "Philosophy",
            "text": "ការអប់រំផ្លូវចិត្តតាមរយៈព្រះពុទ្ធសាសនាជួយឱ្យមនុស្សមានសេចក្ដីស្ងប់ក្នុងចិត្តនិងចេះអត់ឱនឱ្យគ្នា។",
            "expected_errors": []
        },
        {
            "id": 29, "type": "Correct", "topic": "General",
            "text": "ការអានសៀវភៅគឺជាគន្លឹះនៃចំណេះដឹងដែលមិនចេះរីងស្ងួតនិងជួយបើកទូលាយនូវការយល់ដឹងរបស់មនុស្ស។",
            "expected_errors": []
        },
        {
            "id": 30, "type": "Correct", "topic": "General",
            "text": "សុខភាពផ្លូវចិត្តមានសារៈសំខាន់ដូចគ្នានឹងសុខភាពផ្លូវកាយដែរដែលទាមទារឱ្យមានការថែទាំយ៉ាងយកចិត្តទុកដាក់។",
            "expected_errors": []
        }
    ]

    print(f"\nRunning {len(test_cases)} Complex Sentence Tests (Set 2)...")
    
    passed_count = 0
    failed_count = 0
    
    for case in test_cases:
        text = case["text"]
        expected = case["expected_errors"]
        
        # Run detection
        tokens = segment_text(text)
        pos_tags = pos_tag_tokens(tokens, word_to_pos, word_set)
        
        # Collect all errors
        errors = {}
        
        # 1. Grammar
        detect_grammar_errors(pos_tags, errors)
        
        # 2. Error Slots (Typos)
        detect_error_slots(pos_tags, word_set, word_list, bigrams, trigrams, errors, word_freq)
        
        # 3. Semantic Suspicion
        semantic_errors = detect_semantic_suspicion(pos_tags, bigrams, trigrams, word_list)
        errors.update(semantic_errors)
        
        # Check results
        # For this test suite, we expect NO errors (False Positive Check)
        if len(errors) == 0:
            passed_count += 1
            # print(f"✅ Case {case['id']} Passed")
        else:
            failed_count += 1
            print(f"❌ Case {case['id']} Failed: {text}")
            print(f"   Found {len(errors)} errors, expected 0.")
            for idx, err in errors.items():
                print(f"   - {err.get('type', 'Unknown')}: {err.get('original', '')} -> {err.get('suggestions', [])} ({err.get('message', '')})")
    
    print("\n" + "="*40)
    print(f"Test Summary: {passed_count}/{len(test_cases)} Passed")
    print("="*40)

if __name__ == "__main__":
    run_complex_sentences_test_v2()
