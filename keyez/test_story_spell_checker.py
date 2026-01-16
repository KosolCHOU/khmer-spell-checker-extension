
import sys
import os
import json

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

def calculate_metrics(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    accuracy = tp / (tp + fp + fn) if (tp + fp + fn) > 0 else 0
    return precision, recall, f1, accuracy

def test_complex_story():
    print("=" * 100)
    print(f"{'KHMER COMPLEX STORY SPELL CHECKER TEST & ACCURACY MATRIX':^100}")
    print("=" * 100)

    # Metrics counters
    tp = 0
    fp = 0
    fn = 0

    # 1. Clean Version (Advanced Vocabulary)
    clean_story = (
        "ក្នុងយុគសម័យឌីជីថលនេះ ការអភិវឌ្ឍបច្ចេកវិទ្យាមានសក្ដានុពលយ៉ាងខ្លាំង។ "
        "យើងត្រូវប្រើប្រាស់វាដើម្បីការពារបរិស្ថាន។ យុវជនគឺជាកម្លាំងចលករដ៏មានសារៈសំខាន់ក្នុងការថែរក្សាភពផែនដីឱ្យនៅបៃតងជានិច្ច។ "
        "ការចូលរួមពីមនុស្សគ្រប់រូបនឹងនាំមកនូវភាពរីកចម្រើនប្រកបដោយចីរភាព។"
    )
    
    print("\n--- 1. TESTING CLEAN COMPLEX STORY (Target: 0 errors) ---")
    result_clean = check_spelling(clean_story)
    errors_clean = result_clean.get("errors", {})
    token_offsets_clean = result_clean.get("token_offsets", [])
    
    if not errors_clean:
        print("✅ SUCCESS: No false positives detected in complex vocabulary.")
    else:
        print(f"❌ FALSE POSITIVES DETECTED ({len(errors_clean)}):")
        for idx_str, err in errors_clean.items():
            idx = int(idx_str)
            offset = token_offsets_clean[idx] if idx < len(token_offsets_clean) else "Unknown"
            print(f"   - Word: '{err['original']}' at {offset} | Type: {err['error_type']}")
            fp += 1

    # 2. Test Version (Subtle & Complex Errors)
    # Expected errors:
    # 1. យុគមន័យ (instead of យុគសម័យ - Wrong diacritic)
    # 2. បច្ចេកវិទ្យ (instead of បច្ចេកវិទ្យា - Missing final vowel)
    # 3. សកានុពល (Missing subscript 'ដ' -> should be សក្ដានុពល)
    # 4. គឺជារ (Extra 'រ' -> should be គឺជា)
    # 5. សារះសំខាន់ (Wrong 'ah' diacritic 'ះ' instead of 'ៈ')
    # 6. ជីរភាព (Wrong consonant 'ជ' instead of 'ច')
    expected_errors = ["យុគមន័យ", "បច្ចេកវិទ្យ", "សកានុពល", "គឺជារ", "សារះសំខាន់", "ជីរភាព"]
    
    error_story = (
        "ក្នុងយុគមន័យឌីជីថលនេះ ការអភិវឌ្ឍបច្ចេកវិទ្យមានសកានុពលយ៉ាងខ្លាំង។ "
        "យើងត្រូវប្រើប្រាស់វាដើម្បីការពារបរិស្ថាន។ យុវជនគឺជារកម្លាំងចលករដ៏មានសារះសំខាន់ក្នុងការថែរក្សាភពផែនដីឱ្យនៅបៃតងជានិច្ច។ "
        "ការចូលរួមពីមនុស្សគ្រប់រូបនឹងនាំមកនូវភាពរីកចម្រើនប្រកបដោយជីរភាព។"
    )
    
    print("\n--- 2. TESTING COMPLEX ERROR STORY ---")
    result_error = check_spelling(error_story)
    errors_detected = result_error.get("errors", {})
    token_offsets = result_error.get("token_offsets", [])
    
    detected_list = []
    for idx_str, err in errors_detected.items():
        detected_list.append(err['original'])

    print(f"Expected Errors: {expected_errors}")
    print(f"Detected Errors: {detected_list}\n")
    
    temp_expected = expected_errors.copy()
    
    # Detailed Detection Analysis
    for original in detected_list:
        found_in_expected = False
        for i, exp in enumerate(temp_expected):
            if exp == original or exp in original or original in exp:
                tp += 1
                print(f"   ✅ [TP] Detected: '{original}' (matched target '{exp}')")
                temp_expected.pop(i)
                found_in_expected = True
                break
        if not found_in_expected:
            fp += 1
            print(f"   ⚠️ [FP] Unexpected Detection: '{original}'")

    for missed in temp_expected:
        fn += 1
        print(f"   ❌ [FN] Missed Error: '{missed}'")

    # 3. Final Matrix
    precision, recall, f1, accuracy = calculate_metrics(tp, fp, fn)

    print("\n" + "=" * 100)
    print(f"{'ACCURACY MATRIX (COMPLEX STORY)':^100}")
    print("=" * 100)
    print(f"{'Metric':<20} | {'Count/Value':<20}")
    print("-" * 100)
    print(f"{'True Positives':<20} | {tp:<20}")
    print(f"{'False Positives':<20} | {fp:<20}")
    print(f"{'False Negatives':<20} | {fn:<20}")
    print("-" * 100)
    print(f"{'Precision':<20} | {precision:.2%}")
    print(f"{'Recall':<20} | {recall:.2%}")
    print(f"{'F1-Score':<20} | {f1:.2%}")
    print(f"{'Overall Accuracy':<20} | {accuracy:.2%}")
    print("=" * 100)

if __name__ == "__main__":
    test_complex_story()
