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
    
    # Test Set 9: Punctuation (Question Mark ? and Khan ។)
    test_cases = [
        # 1. Standard Questions with ?
        {
            "text": "តើអ្នកឈ្មោះអ្វី?",
            "expected_valid": True,
            "category": "Question - Ter... Avey?"
        },
        {
            "text": "អ្នកចង់ទៅណា?",
            "expected_valid": True,
            "category": "Question - Na?"
        },
        {
            "text": "ហេតុអ្វីបានជាអ្នកយំ?",
            "expected_valid": True,
            "category": "Question - Het Avey?"
        },
        {
            "text": "តើនេះជាសៀវភៅរបស់អ្នកមែនឬទេ?",
            "expected_valid": True,
            "category": "Question - Men Reu Te?"
        },
        {
            "text": "តើអ្នកសុខសប្បាយជាទេ?",
            "expected_valid": True,
            "category": "Question - Sok Sabay?"
        },

        # 2. Statements with Khan ។
        {
            "text": "ខ្ញុំឈ្មោះសុខ។",
            "expected_valid": True,
            "category": "Statement - Khan"
        },
        {
            "text": "ថ្ងៃនេះមេឃស្រឡះល្អណាស់។",
            "expected_valid": True,
            "category": "Statement - Khan"
        },
        {
            "text": "គាត់កំពុងធ្វើការនៅការិយាល័យ។",
            "expected_valid": True,
            "category": "Statement - Khan"
        },
        {
            "text": "កម្ពុជាគឺជាប្រទេសមួយដែលមានវប្បធម៌ចំណាស់។",
            "expected_valid": True,
            "category": "Statement - Khan"
        },
        {
            "text": "សូមរក្សាភាពស្ងៀមស្ងាត់។",
            "expected_valid": True,
            "category": "Statement - Khan"
        },

        # 3. Etc. (។ល។)
        {
            "text": "ផ្លែឈើមានដូចជា៖ ស្វាយ ចេក ក្រូច ។ល។",
            "expected_valid": True,
            "category": "Etc - Khan L Khan"
        },
        {
            "text": "សម្ភារៈសិក្សារួមមាន សៀវភៅ ប៊ិច ខ្មៅដៃ ។ល។",
            "expected_valid": True,
            "category": "Etc - Khan L Khan"
        },

        # 4. Complex Sentences with Punctuation
        {
            "text": "តើអ្នកដឹងទេថាគាត់នៅឯណា?",
            "expected_valid": True,
            "category": "Complex Question"
        },
        {
            "text": "ខ្ញុំមិនដឹងថាគាត់ទៅណាទេ ប៉ុន្តែខ្ញុំគិតថាគាត់នឹងត្រឡប់មកវិញ។",
            "expected_valid": True,
            "category": "Complex Statement with Khan"
        },
        {
            "text": "តើអ្នកអាចជួយខ្ញុំបានទេ? ខ្ញុំត្រូវការជំនួយជាបន្ទាន់។",
            "expected_valid": True,
            "category": "Question + Statement"
        },
        {
            "text": "ប្រសិនបើអ្នកខិតខំរៀនសូត្រ អ្នកនឹងទទួលបានជោគជ័យ។",
            "expected_valid": True,
            "category": "Conditional Statement with Khan"
        },
        {
            "text": "តើអ្នកយល់ព្រមឬទេ?",
            "expected_valid": True,
            "category": "Question - Reu Te?"
        },

        # 5. Informal/Colloquial Questions
        {
            "text": "ទៅណាហ្នឹង?",
            "expected_valid": True,
            "category": "Informal Question - Hnung?"
        },
        {
            "text": "អីគេហ្នឹង?",
            "expected_valid": True,
            "category": "Informal Question - Ei Ke Hnung?"
        },
        {
            "text": "ម៉េចក៏អញ្ចឹង?",
            "expected_valid": True,
            "category": "Informal Question - Mech Anchung?"
        },
        {
            "text": "ញ៉ាំបាយនៅ?",
            "expected_valid": True,
            "category": "Informal Question - Nov?"
        },
        {
            "text": "រួចរាល់ហើយឬនៅ?",
            "expected_valid": True,
            "category": "Informal Question - Reu Nov?"
        },

        # 6. Tricky Punctuation Contexts
        {
            "text": "គាត់សួរថា \"តើអ្នកសុខសប្បាយទេ?\"",
            "expected_valid": True,
            "category": "Quote Question"
        },
        {
            "text": "ខ្ញុំឆ្លើយថា \"ខ្ញុំសុខសប្បាយជាធម្មតា។\"",
            "expected_valid": True,
            "category": "Quote Statement"
        },
        {
            "text": "តើអ្នកចូលចិត្តពណ៌អ្វី? ក្រហម ឬ ខៀវ?",
            "expected_valid": True,
            "category": "Multiple Questions"
        },
        {
            "text": "សូមអរគុណ។",
            "expected_valid": True,
            "category": "Short Statement"
        },
        {
            "text": "តើមានបញ្ហាអ្វីដែរឬទេ?",
            "expected_valid": True,
            "category": "Question - Der Reu Te?"
        }
    ]

    print(f"Running 30 Complex Test Cases (Set 9 - Punctuation ? and Khan)...")
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
