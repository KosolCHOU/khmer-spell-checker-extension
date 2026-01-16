import sys
import os
import time
from typing import List, Dict

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'keyez')))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'keyez_site.settings')
import django
django.setup()

from landing.spell_checker_advanced import (
    SpellCheckerData, 
    segment_text, 
    pos_tag_tokens, 
    detect_grammar_errors, 
    detect_error_slots,
    detect_semantic_suspicion,
    COMMON_TYPOS
)

def run_test():
    print("Initializing Spell Checker Data...")
    start_load = time.time()
    # Initialize data
    word_set, word_to_pos, word_freq, _ = SpellCheckerData.build_tables()
    word_list = SpellCheckerData.get_word_list()
    bigrams = SpellCheckerData.load_bigrams()
    trigrams = SpellCheckerData.load_trigrams()
    print(f"Data loaded in {time.time() - start_load:.2f}s")
    
    # Test Set 8: Other Contextual Rules (Nov/Nov, Ney/Ney, Som/Som, etc.)
    test_cases = [
        # 1. នៅ (At/In/Still) vs នូវ (Object Marker)
        {
            "text": "ខ្ញុំកំពុងរស់នៅទីក្រុងភ្នំពេញជាមួយគ្រួសារ។",
            "expected_valid": True,
            "category": "Nov (At) - Live at"
        },
        {
            "text": "គាត់បានផ្តល់នូវជំនួយជាច្រើនដល់ជនរងគ្រោះ។",
            "expected_valid": True,
            "category": "Nov (Obj Marker) - Give [obj]"
        },
        {
            "text": "តើអ្នកនៅចាំរឿងនោះទេ?",
            "expected_valid": True,
            "category": "Nov (Still) - Still remember"
        },
        {
            "text": "ការនាំមកនូវសន្តិភាពគឺជាបំណងប្រាថ្នារបស់យើង។",
            "expected_valid": True,
            "category": "Nov (Obj Marker) - Bring [obj]"
        },
        {
            "text": "សៀវភៅនេះនៅលើតុ។",
            "expected_valid": True,
            "category": "Nov (At) - At on table"
        },
        {
            "text": "សូមទទួលនូវការគោរពរាប់អានពីខ្ញុំ។",
            "expected_valid": True,
            "category": "Nov (Obj Marker) - Receive [obj]"
        },
        
        # 2. នៃ (Of) vs ន័យ (Meaning)
        {
            "text": "នេះគឺជាអត្ថន័យនៃជីវិត។",
            "expected_valid": True,
            "category": "Ney (Of) - Meaning of Life"
        },
        {
            "text": "ពាក្យនេះមានន័យថាម៉េច?",
            "expected_valid": True,
            "category": "Ney (Meaning) - Has meaning that"
        },
        {
            "text": "ការរីកចម្រើននៃបច្ចេកវិទ្យាគឺលឿនណាស់។",
            "expected_valid": True,
            "category": "Ney (Of) - Growth of Tech"
        },
        {
            "text": "គាត់មិនយល់ពីន័យធៀបនៃពាក្យនេះទេ។",
            "expected_valid": True,
            "category": "Ney (Meaning) - Metaphorical meaning"
        },
        
        # 3. សុំ (Ask) vs សម (Suitable) vs សំ (Noise/Park)
        {
            "text": "ខ្ញុំសុំច្បាប់ឈប់សម្រាកមួយថ្ងៃ។",
            "expected_valid": True,
            "category": "Som (Ask) - Ask permission"
        },
        {
            "text": "អាវនេះពាក់ទៅសមនឹងអ្នកណាស់។",
            "expected_valid": True,
            "category": "Som (Suitable) - Fit well"
        },
        {
            "text": "សូមកុំធ្វើសំឡេងរំខានដល់អ្នកដទៃ។",
            "expected_valid": True,
            "category": "Som (Sound) - Noise"
        },
        {
            "text": "គាត់គឺជាមនុស្សសមរម្យនិងថ្លៃថ្នូរ។",
            "expected_valid": True,
            "category": "Som (Suitable) - Decent"
        },
        {
            "text": "សុំទោសតើអ្នកឈ្មោះអ្វី?",
            "expected_valid": True,
            "category": "Som (Ask) - Excuse me"
        },

        # 4. គ្រូ (Teacher) vs គូ (Pair/Draw)
        {
            "text": "លោកគ្រូកំពុងបង្រៀនសិស្សនៅក្នុងថ្នាក់។",
            "expected_valid": True,
            "category": "Kru (Teacher)"
        },
        {
            "text": "ពួកគេគឺជាគូស្នេហ៍ដ៏សាកសមបំផុត។",
            "expected_valid": True,
            "category": "Ku (Pair) - Couple"
        },
        {
            "text": "កុំគូសវាសនៅលើជញ្ជាំងសាលារៀន។",
            "expected_valid": True,
            "category": "Ku (Draw) - Scribble"
        },
        {
            "text": "គ្រូពេទ្យបានព្យាបាលអ្នកជំងឺដោយយកចិត្តទុកដាក់។",
            "expected_valid": True,
            "category": "Kru (Teacher/Expert) - Doctor"
        },

        # 5. បាទ (Yes - Male) vs បាត (Bottom/Palm)
        {
            "text": "បាទខ្ញុំយល់ព្រមតាមសំណើរបស់អ្នក។",
            "expected_valid": True,
            "category": "Bat (Yes)"
        },
        {
            "text": "កង្កែបនៅក្នុងបាតអណ្តូងមើលឃើញមេឃប៉ុនគម្របឆ្នាំង។",
            "expected_valid": True,
            "category": "Bat (Bottom) - Bottom of well"
        },
        {
            "text": "បាតដៃរបស់គាត់មានស្នាមរបួស។",
            "expected_valid": True,
            "category": "Bat (Palm) - Palm of hand"
        },

        # 6. Mixed / Tricky
        {
            "text": "នៅពេលដែលគាត់មកដល់ខ្ញុំនឹងផ្តល់នូវកាដូមួយ។",
            "expected_valid": True,
            "category": "Mixed - Nov (At), Nov (Obj)"
        },
        {
            "text": "អត្ថន័យនៃពាក្យសុំទោសគឺមានតម្លៃណាស់។",
            "expected_valid": True,
            "category": "Mixed - Ney (Meaning), Ney (Of), Som (Ask)"
        },
        {
            "text": "គ្រូបានប្រាប់ថាគូរបស់ឯងគឺសមគ្នាណាស់។",
            "expected_valid": True,
            "category": "Mixed - Kru, Ku, Som"
        },
        {
            "text": "បាទខ្ញុំនៅចាំពាក្យសម្តីរបស់គាត់។",
            "expected_valid": True,
            "category": "Mixed - Bat, Nov"
        }
    ]

    print(f"Running 30 Complex Test Cases (Set 8 - Other Contextual)...")
    print("=" * 60)
    
    passed_count = 0
    failed_cases = []

    for i, case in enumerate(test_cases):
        text = case["text"]
        expected = case["expected_valid"]
        category = case["category"]
        
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
        is_valid = len(errors) == 0
        
        # Determine pass/fail
        if is_valid == expected:
            status = "PASS"
            passed_count += 1
            print(f"ID {i+1} [{category}]: {status}")
            print(f"Text: {text}")
            print("-" * 60)
        else:
            status = "FAIL"
            failed_cases.append({
                "id": i+1,
                "text": text,
                "category": category,
                "errors": errors
            })
            print(f"ID {i+1} [{category}]: {status}")
            print(f"Text: {text}")
            print(f"Expected Valid: {expected}, Got: {is_valid}")
            if not is_valid:
                print("Errors found:")
                for idx, err in errors.items():
                    print(f"  - {err.get('type', 'Unknown')}: {err.get('original', '')} -> {err.get('suggestions', [])} ({err.get('message', '')})")
            print("-" * 60)

    print(f"\nTest Summary: {passed_count}/{len(test_cases)} Passed")
    accuracy = (passed_count / len(test_cases)) * 100
    print(f"Accuracy: {accuracy:.2f}%")
    
    if accuracy >= 90:
        print("SUCCESS: Accuracy is >= 90%")
    else:
        print("WARNING: Accuracy is < 90%")

if __name__ == "__main__":
    run_test()
