
import sys
import time
from typing import List, Dict

# Import the spell checker module
# Ensure the project root is in sys.path if running directly
import os
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

def run_complex_sentences_test():
    print("Initializing Spell Checker Data...")
    start_load = time.time()
    # Initialize data
    word_set, word_to_pos, word_freq, _ = SpellCheckerData.build_tables()
    word_list = SpellCheckerData.get_word_list()
    bigrams = SpellCheckerData.load_bigrams()
    trigrams = SpellCheckerData.load_trigrams()
    print(f"Data loaded in {time.time() - start_load:.2f}s")
    
    print(f"DEBUG: 'បរទេស' in word_set: {'បរទេស' in word_set}")
    print(f"DEBUG: 'ភព' in word_set: {'ភព' in word_set}")
    
    # 30 Complex Sentences from various topics
    # These are all expected to be CORRECT (False Positive Checks)
    test_cases = [
        # --- Politics/Government ---
        {
            "id": 1, "type": "Correct", "topic": "Politics",
            "text": "គណៈរដ្ឋមន្ត្រីបានអនុម័តសេចក្តីព្រាងច្បាប់ស្តីពីការគ្រប់គ្រងទឹកកខ្វក់ដើម្បីធានានិរន្តរភាពបរិស្ថាន។",
            "expected_errors": []
        },
        {
            "id": 2, "type": "Correct", "topic": "Politics",
            "text": "កិច្ចសហប្រតិបត្តិការអន្តរជាតិរវាងកម្ពុជានិងបណ្ដាប្រទេសក្នុងតំបន់អាស៊ានត្រូវបានពង្រឹងយ៉ាងរឹងមាំ។",
            "expected_errors": []
        },
        {
            "id": 3, "type": "Correct", "topic": "Politics",
            "text": "ការបោះឆ្នោតជ្រើសតាំងតំណាងរាស្ត្រនីតិកាលទី៧បានប្រព្រឹត្តទៅដោយរលូននិងមានតម្លាភាព។",
            "expected_errors": []
        },

        # --- Economy/Finance ---
        {
            "id": 4, "type": "Correct", "topic": "Economy",
            "text": "ធនាគារជាតិនៃកម្ពុជាបានដាក់ចេញនូវគោលនយោបាយរូបិយវត្ថុដើម្បីរក្សាស្ថិរភាពថ្លៃនិងអត្រាប្តូរប្រាក់។",
            "expected_errors": []
        },
        {
            "id": 5, "type": "Correct", "topic": "Economy",
            "text": "វិស័យសហគ្រាសធុនតូចនិងមធ្យមដើរតួនាទីយ៉ាងសំខាន់ក្នុងការបង្កើតការងារនិងបង្កើនប្រាក់ចំណូលជូនប្រជាពលរដ្ឋ។",
            "expected_errors": []
        },
        {
            "id": 6, "type": "Correct", "topic": "Economy",
            "text": "ការវិនិយោគផ្ទាល់ពីបរទេសបានកើនឡើងគួរឱ្យកត់សម្គាល់នៅក្នុងតំបន់សេដ្ឋកិច្ចពិសេសក្រុងព្រះសីហនុ។",
            "expected_errors": []
        },

        # --- Education ---
        {
            "id": 7, "type": "Correct", "topic": "Education",
            "text": "ក្រសួងអប់រំយុវជននិងកីឡាកំពុងអនុវត្តកំណែទម្រង់ស៊ីជម្រៅដើម្បីលើកកម្ពស់គុណភាពនៃការបណ្តុះបណ្តាល។",
            "expected_errors": []
        },
        {
            "id": 8, "type": "Correct", "topic": "Education",
            "text": "ការសិក្សាតាមប្រព័ន្ធអេឡិចត្រូនិកបានក្លាយជាផ្នែកមួយដ៏សំខាន់នៃប្រព័ន្ធអប់រំក្នុងបរិបទនៃបដិវត្តន៍ឧស្សាហកម្ម៤.០។",
            "expected_errors": []
        },
        {
            "id": 9, "type": "Correct", "topic": "Education",
            "text": "សាកលវិទ្យាល័យនានាត្រូវបានលើកទឹកចិត្តឱ្យបង្កើនការស្រាវជ្រាវវិទ្យាសាស្ត្រដើម្បីបម្រើដល់ការអភិវឌ្ឍសង្គម។",
            "expected_errors": []
        },

        # --- Health/Medicine ---
        {
            "id": 10, "type": "Correct", "topic": "Health",
            "text": "ការផ្ដល់សេវាសុខាភិបាលសាធារណៈត្រូវបានពង្រីកដល់តំបន់ដាច់ស្រយាលដើម្បីធានាសមធម៌សុខភាព។",
            "expected_errors": []
        },
        {
            "id": 11, "type": "Correct", "topic": "Health",
            "text": "យុទ្ធនាការចាក់វ៉ាក់សាំងបង្ការជំងឺឆ្លងនានាទទួលបានជោគជ័យយ៉ាងធំធេងដោយមានការចូលរួមពីប្រជាពលរដ្ឋ។",
            "expected_errors": []
        },
        {
            "id": 12, "type": "Correct", "topic": "Health",
            "text": "មន្ទីរពេទ្យគន្ធបុប្ផានៅតែបន្តផ្ដល់ការព្យាបាលដោយឥតគិតថ្លៃដល់កុមារកម្ពុជារាប់លាននាក់ជារៀងរាល់ឆ្នាំ។",
            "expected_errors": []
        },

        # --- Technology ---
        {
            "id": 13, "type": "Correct", "topic": "Technology",
            "text": "បញ្ញាសិប្បនិម្មិតកំពុងត្រូវបានយកមកប្រើប្រាស់ដើម្បីវិភាគទិន្នន័យធំៗនិងជួយក្នុងការសម្រេចចិត្ត។",
            "expected_errors": []
        },
        {
            "id": 14, "type": "Correct", "topic": "Technology",
            "text": "ការបង្កើតថ្នាលបច្ចេកវិទ្យាហិរញ្ញវត្ថុបានជួយសម្រួលដល់ការទូទាត់ប្រាក់និងការធ្វើពាណិជ្ជកម្មតាមប្រព័ន្ធឌីជីថល។",
            "expected_errors": []
        },
        {
            "id": 15, "type": "Correct", "topic": "Technology",
            "text": "សន្តិសុខសាយប័រគឺជាបញ្ហាប្រឈមមួយដែលទាមទារឱ្យមានការយកចិត្តទុកដាក់ខ្ពស់ពីគ្រប់ស្ថាប័នពាក់ព័ន្ធ។",
            "expected_errors": []
        },

        # --- Culture/Arts ---
        {
            "id": 16, "type": "Correct", "topic": "Culture",
            "text": "របាំព្រះរាជទ្រព្យត្រូវបានចុះបញ្ជីជាសម្បត្តិបេតិកភណ្ឌវប្បធម៌អរូបីនៃមនុស្សជាតិដោយអង្គការយូណេស្កូ។",
            "expected_errors": []
        },
        {
            "id": 17, "type": "Correct", "topic": "Culture",
            "text": "ពិធីបុណ្យអុំទូកបណ្តែតប្រទីបនិងសំពះព្រះខែគឺជាប្រពៃណីជាតិដ៏រុងរឿងដែលត្រូវបានប្រារព្ធឡើងជារៀងរាល់ឆ្នាំ។",
            "expected_errors": []
        },
        {
            "id": 18, "type": "Correct", "topic": "Culture",
            "text": "ការអភិរក្សប្រាសាទបុរាណទាមទារឱ្យមានបច្ចេកទេសខ្ពស់និងកិច្ចសហការពីអ្នកជំនាញជាតិនិងអន្តរជាតិ។",
            "expected_errors": []
        },

        # --- Environment/Agriculture ---
        {
            "id": 19, "type": "Correct", "topic": "Environment",
            "text": "ការប្រែប្រួលអាកាសធាតុបានបង្កផលប៉ះពាល់យ៉ាងធ្ងន់ធ្ងរដល់ទិន្នផលកសិកម្មនិងជីវភាពរស់នៅរបស់កសិករ។",
            "expected_errors": []
        },
        {
            "id": 20, "type": "Correct", "topic": "Environment",
            "text": "ក្រសួងបរិស្ថានបាននិងកំពុងជំរុញការដាំដើមឈើឡើងវិញដើម្បីបង្កើនគម្របព្រៃឈើនិងកាត់បន្ថយឧស្ម័នផ្ទះកញ្ចក់។",
            "expected_errors": []
        },
        {
            "id": 21, "type": "Correct", "topic": "Environment",
            "text": "ការធ្វើកសិកម្មតាមបែបទំនើបនិងការប្រើប្រាស់ជីធម្មជាតិជួយបង្កើនផលិតភាពនិងធានាសុវត្ថិភាពចំណីអាហារ។",
            "expected_errors": []
        },

        # --- Law/Justice ---
        {
            "id": 22, "type": "Correct", "topic": "Law",
            "text": "តុលាការកំពូលបានសម្រេចតម្កល់សាលដីការបស់សាលាឧទ្ធរណ៍ទុកជាបានការនៅក្នុងសំណុំរឿងព្រហ្មទណ្ឌនេះ។",
            "expected_errors": []
        },
        {
            "id": 23, "type": "Correct", "topic": "Law",
            "text": "ការគោរពសិទ្ធិមនុស្សនិងនីតិរដ្ឋគឺជាមូលដ្ឋានគ្រឹះនៃការកសាងសង្គមប្រជាធិបតេយ្យនិងយុត្តិធម៌។",
            "expected_errors": []
        },
        {
            "id": 24, "type": "Correct", "topic": "Law",
            "text": "គណៈមេធាវីនៃព្រះរាជាណាចក្រកម្ពុជាមានតួនាទីការពារក្តីនិងផ្ដល់ប្រឹក្សាច្បាប់ជូនប្រជាពលរដ្ឋដោយវិជ្ជាជីវៈ។",
            "expected_errors": []
        },

        # --- History ---
        {
            "id": 25, "type": "Correct", "topic": "History",
            "text": "អាណាចក្រអង្គរគឺជាសម័យកាលដ៏រុងរឿងបំផុតមួយនៅក្នុងប្រវត្តិសាស្ត្រនៃតំបន់អាស៊ីអាគ្នេយ៍។",
            "expected_errors": []
        },
        {
            "id": 26, "type": "Correct", "topic": "History",
            "text": "ការតស៊ូរំដោះជាតិពីរបបប្រល័យពូជសាសន៍បាននាំមកនូវសន្តិភាពនិងការឯកភាពជាតិពេញលេញ។",
            "expected_errors": []
        },
        {
            "id": 27, "type": "Correct", "topic": "History",
            "text": "ឯកសារប្រវត្តិសាស្ត្រជាច្រើនត្រូវបានរក្សាទុកនៅបណ្ណាល័យជាតិដើម្បីទុកជាប្រយោជន៍ដល់អ្នកស្រាវជ្រាវជំនាន់ក្រោយ។",
            "expected_errors": []
        },

        # --- Social Issues ---
        {
            "id": 28, "type": "Correct", "topic": "Social",
            "text": "ការលើកកម្ពស់សមភាពយេនឌ័រនិងការផ្តល់ឱកាសដល់ស្ត្រីគឺជាកត្តាគន្លឹះក្នុងការអភិវឌ្ឍសេដ្ឋកិច្ចសង្គម។",
            "expected_errors": []
        },
        {
            "id": 29, "type": "Correct", "topic": "Social",
            "text": "បញ្ហាគ្រឿងញៀនត្រូវបានរាជរដ្ឋាភិបាលចាត់ទុកជាអាទិភាពដែលត្រូវប្រយុទ្ធប្រឆាំងយ៉ាងម៉ឺងម៉ាត់និងតឹងរ៉ឹង។",
            "expected_errors": []
        },
        {
            "id": 30, "type": "Correct", "topic": "Social",
            "text": "សាមគ្គីភាពក្នុងចំណោមប្រជាពលរដ្ឋគឺជាកម្លាំងចលករដែលមិនអាចខ្វះបានក្នុងការកសាងនិងការពារមាតុភូមិ។",
            "expected_errors": []
        }
    ]

    print(f"\nRunning {len(test_cases)} Complex Sentence Tests...")
    
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
        
        real_errors = []
        for idx, err in errors.items():
            original = err.get('original', '')
            suggestions = err.get('suggestions', [])
            # Ignore if suggestion is identical to original (False alarm)
            if suggestions and original == suggestions[0]:
                continue
            real_errors.append(err)

        if len(real_errors) == 0:
            passed_count += 1
            # print(f"✅ Case {case['id']} Passed")
        else:
            failed_count += 1
            print(f"❌ Case {case['id']} Failed: {text}")
            print(f"   Found {len(real_errors)} errors, expected 0.")
            for err in real_errors:
                print(f"   - {err.get('type', 'Unknown')}: {err.get('original', '')} -> {err.get('suggestions', [])} ({err.get('message', '')})")
    
    print("\n" + "="*40)
    print(f"Test Summary: {passed_count}/{len(test_cases)} Passed")
    print("="*40)

if __name__ == "__main__":
    run_complex_sentences_test()
