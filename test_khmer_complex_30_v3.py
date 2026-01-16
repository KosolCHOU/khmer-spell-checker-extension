
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

def run_complex_sentences_test_v3():
    print("Initializing Spell Checker Data...")
    start_load = time.time()
    # Initialize data
    word_set, word_to_pos, word_freq, _ = SpellCheckerData.build_tables()
    word_list = SpellCheckerData.get_word_list()
    bigrams = SpellCheckerData.load_bigrams()
    trigrams = SpellCheckerData.load_trigrams()
    print(f"Data loaded in {time.time() - start_load:.2f}s")
    
    # 30 New Complex Sentences (Set 3)
    test_cases = [
        # --- Environment & Climate Change ---
        {
            "id": 1, "type": "Correct", "topic": "Environment",
            "text": "ការប្រែប្រួលអាកាសធាតុគឺជាការគំរាមកំហែងដ៏ធំបំផុតចំពោះមនុស្សជាតិនិងប្រព័ន្ធអេកូឡូស៊ី។",
            "expected_errors": []
        },
        {
            "id": 2, "type": "Correct", "topic": "Environment",
            "text": "ការកាប់បំផ្លាញព្រៃឈើខុសច្បាប់ត្រូវតែត្រូវបានទប់ស្កាត់ដើម្បីការពារសត្វព្រៃដែលជិតផុតពូជ។",
            "expected_errors": []
        },
        {
            "id": 3, "type": "Correct", "topic": "Environment",
            "text": "ថាមពលកកើតឡើងវិញដូចជាថាមពលពន្លឺព្រះអាទិត្យកំពុងដើរតួនាទីយ៉ាងសំខាន់ក្នុងការកាត់បន្ថយការបញ្ចេញឧស្ម័នកាបូន។",
            "expected_errors": []
        },

        # --- Digital Economy & Fintech ---
        {
            "id": 4, "type": "Correct", "topic": "Fintech",
            "text": "ការទូទាត់ប្រាក់តាមរយៈប្រព័ន្ធឃ្យូអរកូដបានក្លាយជាមធ្យោបាយដ៏ពេញនិយមនិងងាយស្រួលសម្រាប់ប្រជាជនកម្ពុជា។",
            "expected_errors": []
        },
        {
            "id": 5, "type": "Correct", "topic": "Fintech",
            "text": "ធនាគារឌីជីថលអនុញ្ញាតឱ្យអតិថិជនធ្វើប្រតិបត្តិការហិរញ្ញវត្ថុបានគ្រប់ពេលវេលានិងគ្រប់ទីកន្លែងដោយសុវត្ថិភាព។",
            "expected_errors": []
        },
        {
            "id": 6, "type": "Correct", "topic": "Fintech",
            "text": "បច្ចេកវិទ្យាប្លុកឆេនអាចជួយបង្កើនតម្លាភាពនិងប្រសិទ្ធភាពនៅក្នុងវិស័យហិរញ្ញវត្ថុនិងធនាគារ។",
            "expected_errors": []
        },

        # --- Mental Health ---
        {
            "id": 7, "type": "Correct", "topic": "Mental Health",
            "text": "ការយល់ដឹងអំពីសុខភាពផ្លូវចិត្តជួយកាត់បន្ថយការរើសអើងនិងលើកទឹកចិត្តឱ្យអ្នកជំងឺស្វែងរកជំនួយ។",
            "expected_errors": []
        },
        {
            "id": 8, "type": "Correct", "topic": "Mental Health",
            "text": "ភាពតានតឹងពីការងារអាចបណ្ដាលឱ្យមានបញ្ហាសុខភាពធ្ងន់ធ្ងរប្រសិនបើមិនបានដោះស្រាយទាន់ពេលវេលា។",
            "expected_errors": []
        },
        {
            "id": 9, "type": "Correct", "topic": "Mental Health",
            "text": "ការប្រឹក្សាយោបល់ជាមួយអ្នកជំនាញចិត្តសាស្ត្រគឺជាវិធីសាស្ត្រដ៏ល្អមួយដើម្បីព្យាបាលជំងឺបាក់ទឹកចិត្ត។",
            "expected_errors": []
        },

        # --- Legal & Justice ---
        {
            "id": 10, "type": "Correct", "topic": "Legal",
            "text": "រដ្ឋធម្មនុញ្ញគឺជាច្បាប់កំពូលរបស់ជាតិដែលធានានូវសិទ្ធិសេរីភាពនិងកាតព្វកិច្ចរបស់ពលរដ្ឋគ្រប់រូប។",
            "expected_errors": []
        },
        {
            "id": 11, "type": "Correct", "topic": "Legal",
            "text": "ដំណើរការកាត់ក្តីនៅតុលាការត្រូវតែប្រព្រឹត្តទៅដោយយុត្តិធម៌និងមិនលំអៀងដើម្បីផ្ដល់ភាពត្រឹមត្រូវដល់ជនរងគ្រោះ។",
            "expected_errors": []
        },
        {
            "id": 12, "type": "Correct", "topic": "Legal",
            "text": "ការយល់ដឹងអំពីច្បាប់ចរាចរណ៍ផ្លូវគោកជួយកាត់បន្ថយគ្រោះថ្នាក់និងការពារអាយុជីវិតអ្នកដំណើរ។",
            "expected_errors": []
        },

        # --- Architecture ---
        {
            "id": 13, "type": "Correct", "topic": "Architecture",
            "text": "ស្ថាបត្យកម្មខ្មែរសម័យទំនើបបានរួមបញ្ចូលគ្នារវាងរចនាប័ទ្មប្រពៃណីនិងបច្ចេកទេសសាងសង់ថ្មីៗ។",
            "expected_errors": []
        },
        {
            "id": 14, "type": "Correct", "topic": "Architecture",
            "text": "ការរៀបចំផែនការទីក្រុងឱ្យមានសោភ័ណភាពនិងបរិស្ថានល្អគឺជាកត្តាសំខាន់សម្រាប់ទាក់ទាញភ្ញៀវទេសចរ។",
            "expected_errors": []
        },
        {
            "id": 15, "type": "Correct", "topic": "Architecture",
            "text": "អគារខ្ពស់ៗនៅរាជធានីភ្នំពេញបានផ្លាស់ប្តូរមុខមាត់ទីក្រុងឱ្យកាន់តែមានភាពស៊ីវិល័យនិងរីកចម្រើន។",
            "expected_errors": []
        },

        # --- Culinary Arts ---
        {
            "id": 16, "type": "Correct", "topic": "Culinary",
            "text": "អាហារខ្មែរមានរសជាតិឆ្ងាញ់ពិសារនិងមានលក្ខណៈពិសេសដែលឆ្លុះបញ្ចាំងពីវប្បធម៌ដ៏យូរលង់។",
            "expected_errors": []
        },
        {
            "id": 17, "type": "Correct", "topic": "Culinary",
            "text": "ការធានាសុវត្ថិភាពចំណីអាហារគឺជាការទទួលខុសត្រូវរួមរបស់អ្នកផលិតអ្នកលក់និងអ្នកប្រើប្រាស់។",
            "expected_errors": []
        },
        {
            "id": 18, "type": "Correct", "topic": "Culinary",
            "text": "វិស័យកែច្នៃម្ហូបអាហារកំពុងមានសក្តានុពលខ្ពស់ក្នុងការនាំចេញទៅកាន់ទីផ្សារអន្តរជាតិ។",
            "expected_errors": []
        },

        # --- Logistics ---
        {
            "id": 19, "type": "Correct", "topic": "Logistics",
            "text": "ការតភ្ជាប់ប្រព័ន្ធដឹកជញ្ជូនពហុមធ្យោបាយជួយកាត់បន្ថយថ្លៃដើមនិងបង្កើនសមត្ថភាពប្រកួតប្រជែងរបស់កម្ពុជា។",
            "expected_errors": []
        },
        {
            "id": 20, "type": "Correct", "topic": "Logistics",
            "text": "កំពង់ផែស្វយ័តក្រុងព្រះសីហនុគឺជាច្រកទ្វារសេដ្ឋកិច្ចដ៏សំខាន់សម្រាប់ការនាំចេញនិងនាំចូលទំនិញ។",
            "expected_errors": []
        },
        {
            "id": 21, "type": "Correct", "topic": "Logistics",
            "text": "ការពង្រីកផ្លូវជាតិនិងផ្លូវល្បឿនលឿនបានជួយសម្រួលដល់ការធ្វើដំណើររបស់ប្រជាពលរដ្ឋនៅទូទាំងប្រទេស។",
            "expected_errors": []
        },

        # --- ASEAN & International ---
        {
            "id": 22, "type": "Correct", "topic": "ASEAN",
            "text": "កម្ពុជាបានដើរតួនាទីយ៉ាងសំខាន់ក្នុងការសម្របសម្រួលបញ្ហាតំបន់ក្នុងនាមជាប្រធានអាស៊ានប្តូរវេន។",
            "expected_errors": []
        },
        {
            "id": 23, "type": "Correct", "topic": "ASEAN",
            "text": "សមាហរណកម្មសេដ្ឋកិច្ចអាស៊ានផ្តល់ឱកាសដល់កម្ពុជាក្នុងការទាក់ទាញវិនិយោគិននិងពង្រីកទីផ្សារ។",
            "expected_errors": []
        },
        {
            "id": 24, "type": "Correct", "topic": "ASEAN",
            "text": "កិច្ចសហប្រតិបត្តិការរវាងប្រទេសសមាជិកអាស៊ានគឺចាំបាច់ដើម្បីដោះស្រាយបញ្ហាប្រឈមរួមដូចជាឧក្រិដ្ឋកម្មឆ្លងដែន។",
            "expected_errors": []
        },

        # --- Youth ---
        {
            "id": 25, "type": "Correct", "topic": "Youth",
            "text": "យុវជនគឺជាទំពាំងស្នងឫស្សីដែលត្រូវតែទទួលបានការអប់រំនិងការបណ្តុះបណ្តាលជំនាញឱ្យបានច្បាស់លាស់។",
            "expected_errors": []
        },
        {
            "id": 26, "type": "Correct", "topic": "Youth",
            "text": "ការចូលរួមរបស់យុវជននៅក្នុងកិច្ចការសង្គមជួយពង្រឹងលទ្ធិប្រជាធិបតេយ្យនិងការអភិវឌ្ឍសហគមន៍។",
            "expected_errors": []
        },
        {
            "id": 27, "type": "Correct", "topic": "Youth",
            "text": "កម្មវិធីបណ្តុះបណ្តាលភាពជាអ្នកដឹកនាំជួយឱ្យយុវជនមានទំនុកចិត្តនិងសមត្ថភាពក្នុងការដោះស្រាយបញ្ហា។",
            "expected_errors": []
        },

        # --- Medicine ---
        {
            "id": 28, "type": "Correct", "topic": "Medicine",
            "text": "ការប្រើប្រាស់ឱសថបុរាណខ្មែរនៅតែមានប្រជាប្រិយភាពទន្ទឹមនឹងការរីកចម្រើននៃវេជ្ជសាស្ត្រសម័យថ្មី។",
            "expected_errors": []
        },
        {
            "id": 29, "type": "Correct", "topic": "Medicine",
            "text": "ការស្រាវជ្រាវវិទ្យាសាស្ត្រលើរុក្ខជាតិឱសថអាចនាំឱ្យមានការរកឃើញថ្នាំព្យាបាលជំងឺថ្មីៗដែលមានប្រសិទ្ធភាព។",
            "expected_errors": []
        },
        {
            "id": 30, "type": "Correct", "topic": "Medicine",
            "text": "ក្រមសីលធម៌វិជ្ជាជីវៈគ្រូពេទ្យតម្រូវឱ្យមានការយកចិត្តទុកដាក់ខ្ពស់ចំពោះសុខុមាលភាពរបស់អ្នកជំងឺ។",
            "expected_errors": []
        }
    ]

    print(f"\nRunning {len(test_cases)} Complex Sentence Tests (Set 3)...")
    
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
    run_complex_sentences_test_v3()
