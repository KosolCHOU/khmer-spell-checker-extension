
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

def run_complex_sentences_test_v4():
    print("Initializing Spell Checker Data...")
    start_load = time.time()
    # Initialize data
    word_set, word_to_pos, word_freq, _ = SpellCheckerData.build_tables()
    word_list = SpellCheckerData.get_word_list()
    bigrams = SpellCheckerData.load_bigrams()
    trigrams = SpellCheckerData.load_trigrams()
    print(f"Data loaded in {time.time() - start_load:.2f}s")
    
    # 30 New Complex Sentences (Set 4 - History, Law, Culture)
    test_cases = [
        # --- History & Archaeology ---
        {
            "id": 1, "type": "Correct", "topic": "History",
            "text": "ប្រាសាទអង្គរវត្តគឺជាស្នាដៃស្ថាបត្យកម្មដ៏អស្ចារ្យដែលបង្ហាញពីភាពរុងរឿងនៃអាណាចក្រខ្មែរ។",
            "expected_errors": []
        },
        {
            "id": 2, "type": "Correct", "topic": "History",
            "text": "ការសិក្សាអំពីប្រវត្តិសាស្ត្រជួយឱ្យយើងយល់ដឹងអំពីឫសគល់និងអត្តសញ្ញាណជាតិរបស់យើង។",
            "expected_errors": []
        },
        {
            "id": 3, "type": "Correct", "topic": "History",
            "text": "បុព្វបុរសខ្មែរបានបន្សល់ទុកនូវកេរដំណែលវប្បធម៌ដែលមិនអាចកាត់ថ្លៃបានសម្រាប់កូនចៅជំនាន់ក្រោយ។",
            "expected_errors": []
        },
        {
            "id": 4, "type": "Correct", "topic": "History",
            "text": "សិលាចារឹកបុរាណបានផ្តល់នូវភស្តុតាងយ៉ាងច្បាស់លាស់អំពីការរៀបចំរចនាសម្ព័ន្ធសង្គមនៅសម័យនោះ។",
            "expected_errors": []
        },
        {
            "id": 5, "type": "Correct", "topic": "History",
            "text": "ការអភិរក្សបេតិកភណ្ឌជាតិគឺជាកាតព្វកិច្ចរបស់ប្រជាពលរដ្ឋខ្មែរគ្រប់រូបដើម្បីរក្សាបាននូវតម្លៃដើម។",
            "expected_errors": []
        },

        # --- Law & Justice ---
        {
            "id": 6, "type": "Correct", "topic": "Law",
            "text": "រដ្ឋធម្មនុញ្ញនៃព្រះរាជាណាចក្រកម្ពុជាគឺជាច្បាប់កំពូលដែលធានានូវសិទ្ធិនិងសេរីភាពរបស់ពលរដ្ឋ។",
            "expected_errors": []
        },
        {
            "id": 7, "type": "Correct", "topic": "Law",
            "text": "តុលាការមានតួនាទីឯករាជ្យក្នុងការកាត់ក្តីដើម្បីស្វែងរកយុត្តិធម៌ជូនជនរងគ្រោះដោយគ្មានការរើសអើង។",
            "expected_errors": []
        },
        {
            "id": 8, "type": "Correct", "topic": "Law",
            "text": "ការគោរពច្បាប់ចរាចរណ៍គឺជាការចូលរួមចំណែកយ៉ាងសំខាន់ក្នុងការកាត់បន្ថយគ្រោះថ្នាក់នៅលើដងផ្លូវ។",
            "expected_errors": []
        },
        {
            "id": 9, "type": "Correct", "topic": "Law",
            "text": "នីតិរដ្ឋតម្រូវឱ្យមានការអនុវត្តច្បាប់ដោយស្មើភាពគ្នាចំពោះមុខច្បាប់មិនថាអ្នកមានឬអ្នកក្រឡើយ។",
            "expected_errors": []
        },
        {
            "id": 10, "type": "Correct", "topic": "Law",
            "text": "មេធាវីមានសិទ្ធិការពារកូនក្តីរបស់ខ្លួនស្របតាមនីតិវិធីច្បាប់ដែលបានកំណត់នៅក្នុងក្រមព្រហ្មទណ្ឌ។",
            "expected_errors": []
        },

        # --- Philosophy & Culture ---
        {
            "id": 11, "type": "Correct", "topic": "Culture",
            "text": "ព្រះពុទ្ធសាសនាបានដើរតួនាទីយ៉ាងសំខាន់ក្នុងការអប់រំចិត្តនិងសីលធម៌របស់ប្រជាជនខ្មែរតាំងពីបុរាណកាល។",
            "expected_errors": []
        },
        {
            "id": 12, "type": "Correct", "topic": "Culture",
            "text": "ការធ្វើបុណ្យទានគឺជាប្រពៃណីដ៏ល្អงามដែលបង្ហាញពីទឹកចិត្តសប្បុរសនិងការចែករំលែកនៅក្នុងសង្គម។",
            "expected_errors": []
        },
        {
            "id": 13, "type": "Correct", "topic": "Culture",
            "text": "សុជីវធម៌ក្នុងការនិយាយស្តីនិងការប្រាស្រ័យទាក់ទងគឺជាគុណតម្លៃដែលគួរឱ្យគោរពនៅក្នុងវប្បធម៌ខ្មែរ។",
            "expected_errors": []
        },
        {
            "id": 14, "type": "Correct", "topic": "Culture",
            "text": "ពិធីបុណ្យចូលឆ្នាំថ្មីប្រពៃណីជាតិគឺជាឱកាសដ៏សប្បាយរីករាយសម្រាប់ការជួបជុំក្រុមគ្រួសារនិងញាតិមិត្ត។",
            "expected_errors": []
        },
        {
            "id": 15, "type": "Correct", "topic": "Culture",
            "text": "ការស្លៀកពាក់តាមបែបប្រពៃណីក្នុងពិធីមង្គលការបង្ហាញពីការរក្សាបាននូវអត្តសញ្ញាណវប្បធម៌ដ៏ផូរផង់។",
            "expected_errors": []
        },

        # --- Education & Youth ---
        {
            "id": 16, "type": "Correct", "topic": "Education",
            "text": "ការអប់រំគឺជាគន្លឹះដ៏សំខាន់បំផុតសម្រាប់ការអភិវឌ្ឍធនធានមនុស្សនិងការរីកចម្រើននៃប្រទេសជាតិ។",
            "expected_errors": []
        },
        {
            "id": 17, "type": "Correct", "topic": "Education",
            "text": "យុវជនគឺជាទំពាំងស្នងឫស្សីដែលនឹងបន្តវេនដឹកនាំប្រទេសជាតិឆ្ពោះទៅរកភាពរុងរឿងនាពេលអនាគត។",
            "expected_errors": []
        },
        {
            "id": 18, "type": "Correct", "topic": "Education",
            "text": "ការសិក្សាស្រាវជ្រាវនៅកម្រិតឧត្តមសិក្សាតម្រូវឱ្យមានការគិតស៊ីជម្រៅនិងការវិភាគប្រកបដោយហេតុផល។",
            "expected_errors": []
        },
        {
            "id": 19, "type": "Correct", "topic": "Education",
            "text": "បណ្ណាល័យគឺជាឃ្លាំងនៃចំណេះដឹងដែលបើកចំហសម្រាប់សិស្សនិស្សិតនិងសាធារណជនទូទៅចូលសិក្សា។",
            "expected_errors": []
        },
        {
            "id": 20, "type": "Correct", "topic": "Education",
            "text": "ការបណ្តុះបណ្តាលជំនាញបច្ចេកទេសនិងវិជ្ជាជីវៈកំពុងទទួលបានការយកចិត្តទុកដាក់យ៉ាងខ្លាំងពីរាជរដ្ឋាភិបាល។",
            "expected_errors": []
        },

        # --- Health & Well-being ---
        {
            "id": 21, "type": "Correct", "topic": "Health",
            "text": "ការហាត់ប្រាណជាប្រចាំជួយឱ្យរាងកាយរឹងមាំនិងកាត់បន្ថយហានិភ័យនៃជំងឺផ្សេងៗដូចជាជំងឺបេះដូង។",
            "expected_errors": []
        },
        {
            "id": 22, "type": "Correct", "topic": "Health",
            "text": "ការបរិភោគអាហារដែលមានសុវត្ថិភាពនិងមានជីវជាតិគឺជាកត្តាចាំបាច់សម្រាប់សុខភាពល្អនិងការលូតលាស់។",
            "expected_errors": []
        },
        {
            "id": 23, "type": "Correct", "topic": "Health",
            "text": "សុខភាពផ្លូវចិត្តក៏មានសារៈសំខាន់ដូចសុខភាពផ្លូវកាយដែរហើយមិនគួរត្រូវបានមើលរំលងឡើយ។",
            "expected_errors": []
        },
        {
            "id": 24, "type": "Correct", "topic": "Health",
            "text": "មន្ទីរពេទ្យគន្ធបុប្ផាបានជួយសង្គ្រោះជីវិតកុមារកម្ពុជារាប់លាននាក់ដោយឥតគិតថ្លៃនិងប្រកបដោយគុណធម៌។",
            "expected_errors": []
        },
        {
            "id": 25, "type": "Correct", "topic": "Health",
            "text": "ការចាក់វ៉ាក់សាំងគឺជាវិធីសាស្ត្រដ៏មានប្រសិទ្ធភាពបំផុតក្នុងការការពារជំងឺឆ្លងរាតត្បាតនៅក្នុងសហគមន៍។",
            "expected_errors": []
        },

        # --- Agriculture & Rural Development ---
        {
            "id": 26, "type": "Correct", "topic": "Agriculture",
            "text": "វិស័យកសិកម្មនៅតែជាឆ្អឹងខ្នងនៃសេដ្ឋកិច្ចជាតិដែលផ្តល់ការងារដល់ប្រជាពលរដ្ឋភាគច្រើននៅជនបទ។",
            "expected_errors": []
        },
        {
            "id": 27, "type": "Correct", "topic": "Agriculture",
            "text": "ការប្រើប្រាស់ជីធម្មជាតិជួយកាត់បន្ថយការចំណាយនិងការពារដីកសិកម្មពីការខូចខាតដោយសារសារធាតុគីមី។",
            "expected_errors": []
        },
        {
            "id": 28, "type": "Correct", "topic": "Agriculture",
            "text": "ប្រព័ន្ធធារាសាស្ត្រទំនើបត្រូវបានសាងសង់ឡើងដើម្បីធានាការផ្គត់ផ្គង់ទឹកគ្រប់គ្រាន់សម្រាប់ការធ្វើស្រែប្រាំង។",
            "expected_errors": []
        },
        {
            "id": 29, "type": "Correct", "topic": "Agriculture",
            "text": "កសិករគំរូបានទទួលជោគជ័យក្នុងការដាំដំណាំបន្លែសុវត្ថិភាពដែលកំពុងមានតម្រូវការខ្ពស់នៅលើទីផ្សារ។",
            "expected_errors": []
        },
        {
            "id": 30, "type": "Correct", "topic": "Agriculture",
            "text": "ការអភិវឌ្ឍជនបទមានគោលបំណងកាត់បន្ថយភាពក្រីក្រនិងលើកកម្ពស់ជីវភាពរស់នៅរបស់ប្រជាជននៅតាមមូលដ្ឋាន។",
            "expected_errors": []
        }
    ]

    passed_count = 0
    total_count = len(test_cases)
    
    print(f"\nRunning {total_count} Complex Test Cases (Set 4)...")
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
            # print(f"  Found:    {[e['word'] + ' (' + e['type'] + ')' for e in all_errors]}")
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
    run_complex_sentences_test_v4()
