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
    
    # Test Set 7: Contextual Homophones (Ning, Del, Der, etc.)
    test_cases = [
        # 1. និង (And) vs នឹង (Will/With)
        {
            "text": "ខ្ញុំនិងមិត្តភក្តិបានទៅលេងសមុទ្រកាលពីចុងសប្តាហ៍មុន។",
            "expected_valid": True,
            "category": "Ning (And) - Noun + And + Noun"
        },
        {
            "text": "គាត់នឹងត្រឡប់មកវិញនៅថ្ងៃស្អែកវេលាម៉ោងប្រាំល្ងាច។",
            "expected_valid": True,
            "category": "Ning (Will) - Subject + Will + Verb"
        },
        {
            "text": "សៀវភៅនិងប៊ិចត្រូវបានដាក់នៅលើតុយ៉ាងមានរបៀបរៀបរយ។",
            "expected_valid": True,
            "category": "Ning (And) - Noun + And + Noun"
        },
        {
            "text": "យើងសង្ឃឹមថានឹងទទួលបានលទ្ធផលល្អក្នុងការប្រឡងនេះ។",
            "expected_valid": True,
            "category": "Ning (Will) - That + Will + Verb"
        },
        {
            "text": "ការអភិវឌ្ឍនិងការអភិរក្សត្រូវតែដើរទន្ទឹមគ្នាដើម្បីនិរន្តរភាព។",
            "expected_valid": True,
            "category": "Ning (And) - Noun + And + Noun"
        },
        
        # 2. នឹង (Preposition: With/To/As)
        {
            "text": "ប្រទេសកម្ពុជាកំពុងប្រឈមមុខនឹងបញ្ហាប្រែប្រួលអាកាសធាតុ។",
            "expected_valid": True,
            "category": "Ning (Preposition) - Face + With"
        },
        {
            "text": "តម្លៃទំនិញនេះគឺស្មើនឹងប្រាក់ខែរបស់ខ្ញុំមួយខែពេញ។",
            "expected_valid": True,
            "category": "Ning (Preposition) - Equal + To"
        },
        {
            "text": "គាត់មានទំនាក់ទំនងល្អជាមួយនឹងអ្នកជិតខាងទាំងអស់។",
            "expected_valid": True,
            "category": "Ning (Preposition) - With + Ning"
        },
        {
            "text": "គំនិតរបស់អ្នកគឺស្រដៀងគ្នានឹងគំនិតរបស់ខ្ញុំដែរ។",
            "expected_valid": True,
            "category": "Ning (Preposition) - Similar + To"
        },
        
        # 3. ហ្នឹង (That/There - Demonstrative/Emphasis)
        {
            "text": "សៀវភៅមួយក្បាលហ្នឹងគឺជាសៀវភៅដែលខ្ញុំចូលចិត្តបំផុត។",
            "expected_valid": True,
            "category": "Hnung (That) - Noun + That"
        },
        {
            "text": "រឿងហ្នឹងមិនមែនជាការពិតទេសូមកុំជឿពាក្យចចាមអារ៉ាម។",
            "expected_valid": True,
            "category": "Hnung (That) - Noun + That"
        },
        {
            "text": "តើអ្នកកំពុងធ្វើអ្វីហ្នឹង?",
            "expected_valid": True,
            "category": "Hnung (Emphasis) - Question"
        },
        {
            "text": "ខ្ញុំមិនដែលទៅកន្លែងហ្នឹងទេតាំងពីខ្ញុំកើតមក។",
            "expected_valid": True,
            "category": "Hnung (That Place)"
        },
        {
            "text": "អីហ្នឹង? ម៉េចក៏ថ្លៃម្ល៉េះ?",
            "expected_valid": True,
            "category": "Hnung (What is that)"
        },

        # 4. ដែល (Which/That/Who - Relative Pronoun) vs ដែរ (Also/Too)
        {
            "text": "នេះគឺជាផ្ទះដែលខ្ញុំបានទិញកាលពីឆ្នាំមុន។",
            "expected_valid": True,
            "category": "Del (Relative) - Noun + Del + Verb"
        },
        {
            "text": "មនុស្សដែលខិតខំប្រឹងប្រែងតែងតែទទួលបានជោគជ័យ។",
            "expected_valid": True,
            "category": "Del (Relative) - Noun + Del + Verb"
        },
        {
            "text": "ខ្ញុំក៏ចង់ទៅលេងអង្គរវត្តដែរនៅពេលទំនេរ។",
            "expected_valid": True,
            "category": "Der (Also) - End of clause"
        },
        {
            "text": "តើអ្នកឈ្មោះអ្វីដែរ?",
            "expected_valid": True,
            "category": "Der (Polite particle)"
        },
        {
            "text": "គាត់មិនដែលទៅបរទេសទេក្នុងមួយជីវិតរបស់គាត់។",
            "expected_valid": True,
            "category": "Del (Never - Min Del)"
        },
        {
            "text": "អ្នកណាក៏អាចធ្វើបានដែរប្រសិនបើមានការតាំងចិត្ត។",
            "expected_valid": True,
            "category": "Der (Also/Either)"
        },
        {
            "text": "អ្វីដែលសំខាន់បំផុតគឺសុខភាពនិងសុភមង្គលក្នុងគ្រួសារ។",
            "expected_valid": True,
            "category": "Del (What is...)"
        },

        # 5. Mixed Contexts
        {
            "text": "ខ្ញុំនឹងទៅជួបគាត់ហើយនឹងប្រាប់គាត់អំពីបញ្ហាហ្នឹង។",
            "expected_valid": True,
            "category": "Mixed - Will, And Will (Wait, And Will?)"
        },
        # Note: "ហើយនឹង" (And will) -> "ហើយ" (And/Then) + "នឹង" (Will). Correct.
        # Or "ហើយនិង" (And with)? "ហើយនិង" is often used as "And".
        # "A, B, C ហើយនិង D".
        # "I will go and tell" -> "ខ្ញុំនឹងទៅ ហើយ(នឹង)ប្រាប់".
        # Let's test "ហើយនិង" (And) too.
        {
            "text": "ឪពុកម្តាយហើយនិងកូនៗកំពុងញ៉ាំបាយជុំគ្នា។",
            "expected_valid": True,
            "category": "Hery Ning (And)"
        },
        {
            "text": "តើអ្នកនឹងធ្វើអ្វីនៅថ្ងៃស្អែកហ្នឹង?",
            "expected_valid": True,
            "category": "Mixed - Will, Hnung"
        },
        {
            "text": "សៀវភៅដែលនៅលើតុហ្នឹងជារបស់អ្នកណាដែរ?",
            "expected_valid": True,
            "category": "Mixed - Del, Hnung, Der"
        },
        {
            "text": "ខ្ញុំមិនដឹងថាគាត់នឹងមកឬមិនមកទេ។",
            "expected_valid": True,
            "category": "Mixed - Will, Te (Negative)"
        },
        {
            "text": "ការសិក្សានិងការងារគឺជារឿងពីរដែលមិនអាចខ្វះបាន។",
            "expected_valid": True,
            "category": "Mixed - Ning (And), Del"
        },
        {
            "text": "គាត់និយាយថាគាត់នឹងមិនធ្វើបែបហ្នឹងទៀតទេ។",
            "expected_valid": True,
            "category": "Mixed - Will, Hnung, Te"
        }
    ]

    print(f"Running 30 Complex Test Cases (Set 7 - Contextual)...")
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
