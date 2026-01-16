
from keyez.landing.spell_checker_advanced import SpellCheckerData, segment_text, pos_tag_tokens, detect_semantic_suspicion, is_known
import json

def run_stress_test():
    # Load data
    word_set, word_to_pos, word_freq, _ = SpellCheckerData.build_tables()
    bigrams = SpellCheckerData.load_bigrams()
    word_list = SpellCheckerData.get_word_list()
    words_by_start = SpellCheckerData.get_words_by_start()

    test_cases = [
        {
            "id": 1,
            "category": "Technical & Spelling",
            "text": "បច្ចេកវិជ្ជាខ្មែរនាពេលបច្ចុប្បន្នកំពុងមានការរីកចម្រើនយ៉ាងខ្លាំងក្លាបផុតក្នុងតំបន់អាស៊ាន តែយើងនៅមានបញ្ហាខ្លះៗជាមួយនិងការប្រើប្រាស់អក្សរខ្មែរលើប្រព័ន្ធឌីជីថល។",
            "expected_errors": ["ខ្លាំងក្លាបផុត", "ជាមួយនិង"],
            "description": "Typos in complex words and 'ជាមួយនិង' (should be ជាមួយនឹង)."
        },
        {
            "id": 2,
            "category": "Political/Legal & Vowel Confusion",
            "text": "រដ្ឋាភិបាលបានដាក់ចេញនូវវិធានការណ៍ជាច្រើនដើម្បីពង្រឹងសន្តិសុខជាតិ និងលើកកពស់ជីវៈភាពប្រជាជន។",
            "expected_errors": ["វិធានការណ៍", "លើកកពស់", "ជីវៈភាព"],
            "description": "Extra marks in 'វិធានការណ៍', missing subscript in 'លើកកពស់', and extra vowel in 'ជីវៈភាព'."
        },
        {
            "id": 3,
            "category": "Semantic (Nov vs Nov)",
            "text": "យើងត្រូវតែរួមគ្នាថែរក្សានៅសម្បត្តិវប្បធម៌ជាតិឱ្យបានគង់វង្សសម្រាប់កូនចៅជំនាន់ក្រោយ។",
            "expected_errors": ["នៅ"],
            "description": "Contextual error: 'នៅ' (at) used instead of 'នូវ' (object marker) after transitive verb 'ថែរក្សា'."
        },
        {
            "id": 4,
            "category": "Historical/Literary",
            "text": "ប្រាសាទអង្គរវត្តគឺជាស្នាដៃដ៍អស្ចារ្យនៃស្ថាបត្យកម្មខ្មែរដែលបានកសាងឡើយក្នុងសតវត្សរ៍ទី១២។",
            "expected_errors": ["ដ៍", "កសាងឡើយ"],
            "description": "Wrong diacritic on 'ដ៏' and wrong word usage 'កសាងឡើយ' (built until) vs 'កសាងឡើង' (built up)."
        },
        {
            "id": 5,
            "category": "Social & Loanwords",
            "text": "ខ្ញុំចូលចិត្តប្រើប្រាស់អ៊ីនធើណែតសម្រាប់ស្វែងរកពត៌មានថ្មីៗជារៀងរាល់ថ្ងៃ។",
            "expected_errors": ["អ៊ីនធើណែត", "ពត៌មាន"],
            "description": "Common misspellings of loanwords and Sanskrit-derived words."
        },
        {
            "id": 6,
            "category": "Compound Splitting",
            "text": "សិស្ស នុសិស្ស ត្រូវ តែ ខិត ខំ រៀន សូត្រ ដើម្បី អនា គត ភ្លឺ ស្វាង ។",
            "expected_errors": ["សិស្ស នុសិស្ស", "អនា គត"],
            "description": "Tests if the spell checker can identify that these should be merged tokens: សិស្សានុសិស្ស, អនាគត."
        }
    ]

    print(f"{'ID':<4} | {'Category':<30} | {'Status':<10}")
    print("-" * 50)

    for case in test_cases:
        text = case["text"]
        tokens = segment_text(text, word_set, word_freq, words_by_start, is_known)
        tagged = pos_tag_tokens(tuple(tokens), word_to_pos, word_set)
        
        # Detect spelling errors (not in dict)
        spelling_errors = [t["token"] for t in tagged if not t["in_dict"] and t["type"] == "WORD"]
        
        # Detect semantic/contextual errors
        semantic_errors_dict = detect_semantic_suspicion(tagged, bigrams, {}, word_list)
        
        # Detect grammar errors
        grammar_errors_dict = {}
        # Import detects_grammar_errors dynamically or ensure it is available
        from keyez.landing.spell_checker_advanced import detect_grammar_errors
        detect_grammar_errors(tagged, grammar_errors_dict)
        
        semantic_errors = [tagged[idx]["token"] for idx in semantic_errors_dict]
        grammar_errors = [tagged[idx]["token"] for idx in grammar_errors_dict]
        
        all_detected = set(spelling_errors + semantic_errors + grammar_errors)

        
        # Simple check: are at least some expected errors found?
        found_count = 0
        for expected in case["expected_errors"]:
            if any(expected in detected for detected in all_detected):
                found_count += 1
        
        status = "PASS" if found_count > 0 else "FAIL"
        print(f"{case['id']:<4} | {case['category']:<30} | {status}")
        
        if status == "FAIL" or True: # Always show for debug/stress test output
            print(f"   Text: {text}")
            print(f"   Detected: {list(all_detected)}")
            print(f"   Expected: {case['expected_errors']}")
            print("-" * 50)

if __name__ == "__main__":
    run_stress_test()
