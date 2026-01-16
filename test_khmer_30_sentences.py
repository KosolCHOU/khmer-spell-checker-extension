
import sys
import time
from typing import List, Dict

# Import the spell checker module
from keyez.landing.spell_checker_advanced import (
    SpellCheckerData, 
    segment_text, 
    pos_tag_tokens, 
    detect_grammar_errors, 
    detect_error_slots,
    detect_semantic_suspicion,
    COMMON_TYPOS
)

def run_30_sentences_test():
    print("Initializing Spell Checker Data...")
    start_load = time.time()
    word_set, word_to_pos, word_freq, _ = SpellCheckerData.build_tables()
    word_list = SpellCheckerData.get_word_list()
    bigrams = SpellCheckerData.load_bigrams()
    print(f"Data loaded in {time.time() - start_load:.2f}s")
    
    from keyez.landing.spell_checker_advanced import WHITELIST_WORDS, COMMON_TYPOS
    print(f"DEBUG: 'ទូរស័ព្ទដៃ' in WHITELIST: {'ទូរស័ព្ទដៃ' in WHITELIST_WORDS}")
    print(f"DEBUG: 'ផ្ញើឯកសារ' in WHITELIST: {'ផ្ញើឯកសារ' in WHITELIST_WORDS}")
    print(f"DEBUG: 'ប្រកួតប្រជែ' in COMMON_TYPOS: {'ប្រកួតប្រជែ' in COMMON_TYPOS}")
    
    test_cases = [

        # --- FALSE POSITIVE CHECKS (Should pass with NO errors) ---
        {
            "id": 1, "type": "Correct", "topic": "Politics",
            "text": "រាជរដ្ឋាភិបាលកម្ពុជាបានដាក់ចេញនូវយុទ្ធសាស្ត្របញ្ចកោណដើម្បីជំរុញកំណើនសេដ្ឋកិច្ច។",
            "expected_errors": []
        },
        {
            "id": 2, "type": "Correct", "topic": "Technology",
            "text": "ការអភិវឌ្ឍវិស័យបច្ចេកវិទ្យាព័ត៌មាននិងទូរគមនាគមន៍គឺជាអាទិភាពមួយសម្រាប់ប្រទេស។",
            "expected_errors": []
        },
        {
            "id": 3, "type": "Correct", "topic": "Formal",
            "text": "លោកនាយករដ្ឋមន្ត្រីបានអញ្ជើញទៅចូលរួមក្នុងពិធីសម្ពោធដាក់ឱ្យប្រើប្រាស់ផ្លូវជាតិលេខ៥។",
            "expected_errors": []
        },
        {
            "id": 4, "type": "Correct", "topic": "Education",
            "text": "សិស្សានុសិស្សកំពុងសិក្សាអំពីប្រវត្តិសាស្ត្រនៃប្រាសាទព្រះវិហារដោយយកចិត្តទុកដាក់។",
            "expected_errors": []
        },
        {
            "id": 5, "type": "Correct", "topic": "Environment",
            "text": "យើងគួរតែការពារបរិស្ថានដោយកាត់បន្ថយការប្រើប្រាស់ថង់ប្លាស្ទិកនិងដាំដើមឈើ។",
            "expected_errors": []
        },
        {
            "id": 6, "type": "Correct", "topic": "Economy",
            "text": "សេដ្ឋកិច្ចឌីជីថលកំពុងដើរតួនាទីយ៉ាងសំខាន់ក្នុងការផ្លាស់ប្តូររបៀបរស់នៅរបស់ប្រជាជន។",
            "expected_errors": []
        },
        {
            "id": 7, "type": "Correct", "topic": "General",
            "text": "កសិករនៅខេត្តបាត់ដំបងសប្បាយចិត្តនឹងទិន្នផលស្រូវដែលកើនឡើងនៅឆ្នាំនេះ។",
            "expected_errors": []
        },
        {
            "id": 8, "type": "Correct", "topic": "Mobile",
            "text": "កម្មវិធីទូរស័ព្ទដៃនេះមានមុខងារទំនើបៗជាច្រើនដែលជួយសម្រួលដល់ការងារប្រចាំថ្ងៃ។",
            "expected_errors": []
        },
        {
            "id": 9, "type": "Correct", "topic": "Literature",
            "text": "អក្សរសិល្ប៍ខ្មែរមានតម្លៃមិនអាចកាត់ថ្លៃបានសម្រាប់អត្តសញ្ញាណជាតិនិងការសិក្សា។",
            "expected_errors": []
        },
        {
            "id": 10, "type": "Correct", "topic": "Casual",
            "text": "សូមផ្ញើឯកសារដែលបានកែតម្រូវមកខ្ញុំតាមរយៈតេឡេក្រាមនៅរសៀលនេះផង។",
            "expected_errors": []
        },
        {
            "id": 11, "type": "Correct", "topic": "Complex",
            "text": "សន្តិភាពគឺជាមូលដ្ឋានគ្រឹះនៃការអភិវឌ្ឍលើគ្រប់វិស័យទាំងវិស័យសាធារណៈនិងឯកជន។",
            "expected_errors": []
        },
         {
            "id": 12, "type": "Correct", "topic": "Health",
            "text": "ការហាត់ប្រាណទៀងទាត់ជួយឱ្យសុខភាពរឹងមាំនិងជៀសផុតពីជំងឺផ្សេងៗ។",
            "expected_errors": []
        },
        {
            "id": 13, "type": "Correct", "topic": "Culture",
            "text": "របាំអប្សរាគឺជាសម្បត្តិវប្បធម៌អរូបីនៃមនុស្សជាតិដែលត្រូវបានទទួលស្គាល់ដោយអង្គការយូណេស្កូ។",
            "expected_errors": []
        },
        {
            "id": 14, "type": "Correct", "topic": "Science",
            "text": "អ្នកវិទ្យាសាស្ត្រកំពុងសិក្សាអំពីបម្រែបម្រួលអាកាសធាតុនិងផលប៉ះពាល់របស់វា។",
            "expected_errors": []
        },
        {
            "id": 15, "type": "Correct", "topic": "Finance",
            "text": "ធនាគារជាតិបានដាក់ចេញនូវគោលនយោបាយថ្មីដើម្បីពង្រឹងវិស័យហិរញ្ញវត្ថុ។",
            "expected_errors": []
        },

        # --- ERROR CHECKS (Should FAIL and detect errors) ---
        {
            "id": 16, "type": "Error", "topic": "Spelling",
            "text": "បច្ចេកវិជ្ជាពត៌មានមានសារៈសំខាន់ណាស់នៅពេលបច្ចុប្បន្ន។",
            "expected_errors": ["ពត៌មាន"] # Should be ព័ត៌មាន
        },
        {
            "id": 17, "type": "Error", "topic": "Spelling",
            "text": "ខ្ញុំចង់ទៅលេងប្រទសថៃនៅខែក្រោយជាមួយគ្រួសារ។",
            "expected_errors": ["ប្រទស"] # Should be ប្រទេស
        },
        {
            "id": 18, "type": "Error", "topic": "Spelling",
            "text": "យើងត្រូវកាពារព្រៃឈើដើម្បីរក្សាតុល្យភាពបរិស្ថាន។",
            "expected_errors": ["កាពារ"] # Should be ការពារ
        },
        {
            "id": 19, "type": "Error", "topic": "Spelling",
            "text": "សូមមេត្តាជួយសំរួលចរាចរណ៍នៅផ្លូវបំបែកនេះផង។",
            "expected_errors": ["សំរួល"] # Should be សម្រួល
        },
        {
            "id": 20, "type": "Error", "topic": "Spelling",
            "text": "ផ្ទះថ្មីនេះស្អាណាស់ខ្ញុំពិតជាពេញចិត្ត។",
            "expected_errors": ["ស្អា"] # Should be ស្អាត
        },
        {
            "id": 21, "type": "Error", "topic": "Grammar",
            "text": "រដ្ឋាភិបាលបានដាក់ចេញនៅវិធានការថ្មីជាច្រើន។",
            "expected_errors": ["នៅ"] # Should be នូវ
        },
         {
            "id": 22, "type": "Error", "topic": "Grammar",
            "text": "យើងត្រូវរួមគ្នាការពារនៅធនធានធម្មជាតិ។",
            "expected_errors": ["នៅ"] # Should be នូវ
        },
        {
            "id": 23, "type": "Error", "topic": "Spelling",
            "text": "ការប្រកួតប្រជែនេះមានភាពតានតឹងនិងស្វិតស្វាញ។",
            "expected_errors": ["ប្រកួតប្រជែ"] # Should be ប្រកួតប្រជែង
        },
        {
            "id": 24, "type": "Error", "topic": "Spelling",
            "text": "សិស្សនុសិស្សទាំងអស់ត្រូវគោរពវិន័យសាលា។",
            "expected_errors": ["សិស្សនុសិស្ស", "សិស្ស", "នុសិស្ស"] # Split error or spelling
        },
        {
            "id": 25, "type": "Error", "topic": "Loanword",
            "text": "ខ្ញុំប្រើអិនធឺណិតរាល់ថ្ងៃដើម្បីធ្វើការ។",
            "expected_errors": ["អិនធឺណិត"] # Should be អ៊ីនធឺណិត
        },
        {
            "id": 26, "type": "Error", "topic": "Spelling",
            "text": "គាត់សរសេលិខិតមួយច្បាប់ជូននាយក។",
            "expected_errors": ["សរសេ"] # Should be សរសេរ
        },
        {
            "id": 27, "type": "Error", "topic": "Spelling",
            "text": "កំលាំងពលកម្មគឺជាកត្តាសំខាន់ក្នុងការផលិត។",
            "expected_errors": ["កំលាំង"] # Should be កម្លាំង
        },
        {
            "id": 28, "type": "Error", "topic": "Spelling",
            "text": "តំលៃទំនិញនៅលើទីផ្សារមានការប្រែប្រួល។",
            "expected_errors": ["តំលៃ"] # Should be តម្លៃ
        },
        {
            "id": 29, "type": "Error", "topic": "Spelling",
            "text": "បញ្ហាចរាចរណ៏គឺជាបញ្ហាប្រឈមក្នុងទីក្រុង។",
            "expected_errors": ["ចរាចរណ៏"] # Should be ចរាចរណ៍
        },
        {
            "id": 30, "type": "Error", "topic": "Spelling",
            "text": "សូមអោយលោកអ្នកជួបតែសំណាងល្អ។",
            "expected_errors": ["អោយ"] # Should be ឱ្យ
        },
    ]

    print(f"\nRunning {len(test_cases)} Tests...\n")
    print(f"{'ID':<4} | {'Type':<8} | {'Topic':<12} | {'Status':<10} | {'Details'}")
    print("-" * 100)

    score = 0
    passed = 0
    
    for case in test_cases:
        text = case["text"]
        
        # 1. Segment
        tokens = segment_text(text)
        
        if case['id'] in {8, 10, 15}:
             print(f"DEBUG CASE {case['id']} TOKENS: {tokens}")
        
        # 2. Tag
        tagged = pos_tag_tokens(tuple(tokens), word_to_pos, word_set)
        
        # 3. Detect
        errors = {}
        detect_error_slots(tagged, word_set, word_list, bigrams, {}, errors, word_freq)
        detect_grammar_errors(tagged, errors)
        
        # Collect detected tokens
        detected_tokens = []
        for idx in errors:
            detected_tokens.append(errors[idx]['original'])
            
        detected_set = set(detected_tokens)
        
        is_pass = False
        
        if case['type'] == 'Correct':
            # Pass if NO errors detected
            if not detected_set:
                is_pass = True
            else:
                # If detected errors are actually acceptable variants, maybe soft fail?
                # But for strict check, we want empty.
                is_pass = False
        else:
            # Pass if EXPECTED errors detected
            # Check overlap
            found_expected = [e for e in case['expected_errors'] if e in detected_set or any(e in d for d in detected_set)]
            if found_expected:
                is_pass = True
            else:
                is_pass = False
        
        status_str = "PASS" if is_pass else "FAIL"
        if is_pass:
            passed += 1
            
        # Format output
        detected_str = f"Found: {list(detected_set)}" if detected_set else "Found: None"
        if case['type'] == 'Error' and not is_pass:
            expected_str = f"Expected: {case['expected_errors']}"
            detail = f"{detected_str} | {expected_str}"
        elif case['type'] == 'Correct' and not is_pass:
             detail = f"FALSE POSITIVE: {detected_str}"
        else:
             detail = ""

        print(f"{case['id']:<4} | {case['type']:<8} | {case['topic']:<12} | {status_str:<10} | {detail}")

    print("-" * 100)
    print(f"Final Score: {passed}/{len(test_cases)} ({passed/len(test_cases)*100:.1f}%)")

if __name__ == "__main__":
    run_30_sentences_test()
