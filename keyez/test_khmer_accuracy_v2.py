
import sys
import os
import json
from typing import List, Dict

# Add landing directory to path to import spell_checker_advanced
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'landing')))

try:
    from spell_checker_advanced import check_spelling
except ImportError:
    try:
        from landing.spell_checker_advanced import check_spelling
    except ImportError:
        print("Error: Could not import spell_checker_advanced.")
        sys.exit(1)

TEST_CASES = [
    # === CATEGORY 1: NEW CONTEXTUAL & GRAMMAR (10 cases) ===
    {
        "description": "Rule: 'សកម្ម' (Active) vs 'សាកម្ម' (Typo)",
        "text": "យុវជនត្រូវមានស្មារតីសាកម្មក្នុងការងារ។",
        "expected_error": "សាកម្ម",
        "suggestion": "សកម្ម"
    },
    {
        "description": "Rule: 'បន្ត' (Continue) vs 'បន្ន' (Typo)",
        "text": "យើងត្រូវបន្នការខិតខំប្រឹងប្រែងទៀត។",
        "expected_error": "បន្ន",
        "suggestion": "បន្ត"
    },
    {
        "description": "Rule: 'គំនិត' (Idea) vs 'កំនិត' (Typo)",
        "text": "គាត់មានកំនិតច្នៃប្រឌិតខ្ពស់។",
        "expected_error": "កំនិត",
        "suggestion": "គំនិត"
    },
    {
        "description": "Rule: 'សហការ' (Cooperate) vs 'សាកហការ' (Typo)",
        "text": "សូមសាកហការជាមួយអាជ្ញាធរមូលដ្ឋាន។",
        "expected_error": "សាកហការ",
        "suggestion": "សហការ"
    },
    {
        "description": "Rule: 'រៀបចំ' (Prepare) vs 'រៀបចម' (Typo)",
        "text": "រៀបចមឯកសារឱ្យបានត្រឹមត្រូវ។",
        "expected_error": "រៀបចម",
        "suggestion": "រៀបចំ"
    },
    {
        "description": "Correct sentence: 'តស៊ូ' (Struggle)",
        "text": "យើងត្រូវតស៊ូដើម្បីអនាគតដ៏ភ្លឺស្វាង។",
        "is_correct": True
    },
    {
        "description": "Correct sentence: 'ផ្ដល់' (Provide)",
        "text": "រដ្ឋាភិបាលផ្ដល់អាហារូបករណ៍ដល់សិស្សក្រីក្រ។",
        "is_correct": True
    },
    {
        "description": "Rule: 'ជោគជ័យ' (Success) vs 'ជោគជយ' (Typo)",
        "text": "សូមជូនពរឱ្យទទួលបានជោគជយគ្រប់ភារកិច្ច។",
        "expected_error": "ជោគជយ",
        "suggestion": "ជោគជ័យ"
    },
    {
        "description": "Rule: 'សរសើរ' (Praise) vs 'សសើរ' (Typo)",
        "text": "គ្រូសសើរសិស្សដែលរៀនពូកែ។",
        "expected_error": "សសើរ",
        "suggestion": "សរសើរ"
    },
    {
        "description": "Rule: 'ប្រយ័ត្ន' (Careful) vs 'ប្រយត្ន' (Typo)",
        "text": "បើកបរត្រូវប្រយត្នគ្រោះថ្នាក់។",
        "expected_error": "ប្រយត្ន",
        "suggestion": "ប្រយ័ត្ន"
    },

    # === CATEGORY 2: COMPOUND WORDS & TECHNICAL (10 cases) ===
    {
        "description": "Rule: 'វិវឌ្ឍ' (Evolve) vs 'វិវត្តន៍' (Incorrect choice)",
        "text": "បច្ចេកវិទ្យាកំពុងវិវឌ្ឍយ៉ាងលឿន។",
        "is_correct": True
    },
    {
        "description": "Rule: 'អភិវឌ្ឍ' (Develop) vs 'អភិវឌ្ឈ' (Incorrect subscript)",
        "text": "ការអភិវឌ្ឈសេដ្ឋកិច្ចឆ្លងកាត់ច្រើនដំណាក់កាល។",
        "expected_error": "អភិវឌ្ឈ",
        "suggestion": "អភិវឌ្ឍ"
    },
    {
        "description": "Rule: 'ព័ត៌មាន' (Information) vs 'ពត៌មាន' (Typo)",
        "text": "ពត៌មាននេះពិតជាមានសារៈសំខាន់ណាស់។",
        "expected_error": "ពត៌មាន",
        "suggestion": "ព័ត៌មាន"
    },
    {
        "description": "Rule: 'សកល' (Global) vs 'សាកល' (Commonly mixed)",
        "text": "បញ្ហាកំដៅសកលប៉ះពាល់ដល់មនុស្សគ្រប់រូប។",
        "is_correct": True
    },
    {
        "description": "Rule: 'ប្រជាជន' (People) vs 'ប្រជាជន្ន' (Typo)",
        "text": "ប្រជាជន្នខ្មែរមានចិត្តសប្បុរស។",
        "expected_error": "ប្រជាជន្ន",
        "suggestion": "ប្រជាជន"
    },
    {
        "description": "Rule: 'វិញ្ញាបនបត្រ' (Certificate) vs 'វិញ្ញាបនប័ត្រ' (Typo)",
        "text": "គាត់ទទួលបានវិញ្ញាបនប័ត្របញ្ជាក់ការសិក្សា។",
        "expected_error": "វិញ្ញាបនប័ត្រ",
        "suggestion": "វិញ្ញាបនបត្រ"
    },
    {
        "description": "Technical: 'អុីនធឺណិត' (Internet) correctly spelled",
        "text": "ការប្រើប្រាស់អុីនធឺណិតមានការកើនឡើង។",
        "is_correct": True
    },
    {
        "description": "Technical: 'ស្មាតហ្វូន' (Smartphone) correctly spelled",
        "text": "ស្មាតហ្វូនជួយឱ្យការទំនាក់ទំនងងាយស្រួល។",
        "is_correct": True
    },
    {
        "description": "Technical: 'ឌីជីថល' (Digital) correctly spelled",
        "text": "យើងកំពុងរស់នៅក្នុងយុគសម័យឌីជីថល។",
        "is_correct": True
    },
    {
        "description": "Technical: 'កុំព្យូទ័រ' (Computer) vs 'កុំពុទ័រ' (Typo)",
        "text": "កុំពុទ័រនេះមានល្បឿនលឿនណាស់។",
        "expected_error": "កុំពុទ័រ",
        "suggestion": "កុំព្យូទ័រ"
    },

    # === CATEGORY 3: COMPLEX SENTENCES & SLANG (10 cases) ===
    {
        "description": "Slang/Loan: 'ស៊ែរ' (Share) from English",
        "text": "កុំភ្លេចស៊ែរវីដេអូនេះទៅមិត្តភក្តិផង។",
        "is_correct": True
    },
    {
        "description": "Slang/Loan: 'ឡាយ' (Live) from English",
        "text": "គាត់កំពុងឡាយលក់ផលិតផលនៅលើហ្វេសប៊ុក។",
        "is_correct": True
    },
    {
        "description": "Complex: No space sentence with typo",
        "text": "ការអប់រំគឺជាគ្រឹះនៃកាអភិវឌ្ឍន៍ធនធានមនុស្ស។", # Wrong: កាអភិវឌ្ឍន៍
        "expected_error": "កាអភិវឌ្ឍន៍",
        "suggestion": "ការអភិវឌ្ឍន៍"
    },
    {
        "description": "Complex: Historical Context",
        "text": "ព្រះមហាក្សត្រខ្មែរតែងតែយកព្រះទ័យទុកដាក់ចំពោះរាស្ត្រ។",
        "is_correct": True
    },
    {
        "description": "Rule: 'សន្យា' (Promise) vs 'សន្យ' (Typo)",
        "text": "យើងត្រូវរក្សាសន្យដែលបានផ្តល់ឱ្យ។",
        "expected_error": "សន្យ",
        "suggestion": "សន្យា"
    },
    {
        "description": "Rule: 'សប្បាយ' (Happy) vs 'សប្បាយយ' (Extra char)",
        "text": "ខ្ញុំមានអារម្មណ៍សប្បាយយណាស់ថ្ងៃនេះ។",
        "expected_error": "សប្បាយយ",
        "suggestion": "សប្បាយ"
    },
    {
        "description": "Rule: 'មិត្តភក្តិ' (Friend) vs 'មិត្តភក្ដិ' (Variant subscript - check support)",
        "text": "មិត្តភក្ដិជួយគ្នាក្នុងគ្រាក្រ។",
        "is_correct": True
    },
    {
        "description": "Rule: 'ស្រុកកំណើត' (Hometown) vs 'ស្រុកកំនើត' (Typo)",
        "text": "ខ្ញុំនឹករលឹកស្រុកកំនើតខ្លាំងណាស់។",
        "expected_error": "ស្រុកកំនើត",
        "suggestion": "ស្រុកកំណើត"
    },
    {
        "description": "Rule: 'អរគុណ' (Thank you) vs 'អគុណ' (Typo)",
        "text": "អគុណបងសម្រាប់ដំបូន្មានល្អៗ។",
        "expected_error": "អគុណ",
        "suggestion": "អរគុណ"
    },
    {
        "description": "Rule: 'ខ្មែរ' (Khmer) vs 'ខ្មែ' (Missing char)",
        "text": "ភាសាខ្មែមានប្រវត្តិយូរលង់ណាស់មកហើយ។",
        "expected_error": "ខ្មែ",
        "suggestion": "ខ្មែរ"
    }
]

def run_test_suite():
    print("=" * 100)
    print(f"{'KHMER SPELL CHECKER ACCURACY TEST V2':^100}")
    print("=" * 100)
    print(f"{'Category/Description':<60} | {'Status':<10} | {'Details'}")
    print("-" * 100)

    total = len(TEST_CASES)
    passed = 0
    false_positives = 0
    false_negatives = 0
    
    for i, case in enumerate(TEST_CASES, 1):
        text = case["text"]
        is_correct_sentence = case.get("is_correct", False)
        
        result = check_spelling(text)
        detected_errors = result.get("errors", {})
        
        status = "FAIL"
        details = ""
        
        if is_correct_sentence:
            if not detected_errors:
                status = "PASS"
                passed += 1
            else:
                status = "FAIL (FP)"
                false_positives += 1
                details = f"Detected {len(detected_errors)} false errors: " + ", ".join([e['original'] for e in detected_errors.values()])
        else:
            expected_word = case.get("expected_error")
            found = False
            for err_idx, err_info in detected_errors.items():
                if expected_word in err_info['original'] or err_info['original'] in expected_word:
                    found = True
                    # Check suggestion if provided
                    if "suggestion" in case:
                        # Check multiple suggestions if available
                        suggestions = err_info.get('suggestions', [])
                        if case["suggestion"] in suggestions:
                            details = f"Correctly suggested: {case['suggestion']}"
                        else:
                            top_suggestion = suggestions[0] if suggestions else "None"
                            details = f"Wrong suggestion: {top_suggestion} (Exp: {case['suggestion']})"
                    break
            
            if found:
                status = "PASS"
                passed += 1
            else:
                status = "FAIL (FN)"
                false_negatives += 1
                details = f"Expected error '{expected_word}' not detected"

        print(f"{case['description'][:58]:<60} | {status:<10} | {details}")

    print("=" * 100)
    print(f"SUMMARY: {passed}/{total} Passed")
    print(f"- Correct Detections/Passes: {passed}")
    print(f"- False Positives:           {false_positives}")
    print(f"- False Negatives:           {false_negatives}")
    print(f"Accuracy Rate:                {(passed/total)*100:.2f}%")
    print("=" * 100)

if __name__ == "__main__":
    run_test_suite()
