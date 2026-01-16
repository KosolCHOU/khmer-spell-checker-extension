
import sys
import time
from typing import List, Dict

# Import the spell checker module
from keyez.landing.spell_checker_advanced import (
    SpellCheckerData, 
    segment_text, 
    pos_tag_tokens, 
    detect_grammar_errors, 
    detect_error_slots
)

def run_long_text_test_v3():
    print("=" * 100)
    print("RUNNING KHMER SPELL CHECKER LONG TEXT STRESS TEST (PHASE 4 - HERITAGE & PROGRESS)")
    print("=" * 100)
    
    print("Initializing Spell Checker Data...")
    start_load = time.time()
    word_set, word_to_pos, word_freq, _ = SpellCheckerData.build_tables()
    word_list = SpellCheckerData.get_word_list()
    bigrams = SpellCheckerData.load_bigrams()
    print(f"Data loaded in {time.time() - start_load:.2f}s")
    
    paragraphs = [
        # P1: Khmer Heritage and Dance
        "របាំព្រះរាជទ្រព្យគឺជាបេតិកភណ្ឌអរូបីនៃមនុស្សជាតិដែលយើងត្រូវថែរក្សាសំរាប់កូនចៅជំនាន់ក្រោយយ។ "
        "សម្លៀកបំពាក់និងក្បាច់រាំមានភាពវិចិត្ររនិងទន់ភ្លន់ខ្លាំងណាស់សំរាប់អ្នកទស្សនា។ "
        "យើងត្រូវរួមគ្នាការពាររនូវកេរ្តិ៍តំណែលបូរាណណនេះអោយបានគង់វង្សជានិច្ច។",
        
        # P2: Digital Era and Connectivity
        "បច្ចុប្បន្នភាពពនៃបច្ចេកវិទ្យាឌីជីថលបានធ្វើឱ្យការរស់នៅមានភាពងាយស្រួលលជាងមុន។ "
        "មនុស្សម្នាក់ៗមានទូរស័ព្ទដៃដែលភ្ជាប់ទៅកាន់ពិភពលោកតាមរយៈអិនធឺណិត។ "
        "ទោះជាយ៉ាងណា យើងត្រូវចេះប្រើប្រាស់បច្ចេកវិជ្ជាអោយបានត្រឹមត្រូវនិងមានសុវត្ថិភាពភាជានិច្ច។",
        
        # P3: Education, STEM, and Morality
        "ការអប់រំនៅតាមសាលារៀននមិនត្រឹមតែផ្តល់នូវចំណេះដឺងបច្ចេកទេសសប៉ុណ្ណោះទេ។ "
        "គ្រូបង្រៀនត្រូវពង្រឹងសីលធម៏និងសុជីវធម៏ដល់សិស្សានុសិស្សគ្រប់រូប។ "
        "សិស្សម្នាក់ៗត្រូវមានភាពកតញ្ញនិងគោរពចាស់ទុំមដើម្បីក្លាយជាទំពាំងស្នងឫស្សីដ៏ល្អ។",
        
        # P4: Conclusion and National Pride
        "សរុបមក ការរួមបញ្ចូលគ្នារវាងប្រពៃណនិងការអភិវឌ្ឍន៏សម័យទំនើបនឹងនាំមកនូវជោគជយដល់ជាតិ។ "
        "យើងមានមោទនភាពពចំពោះស្នាដៃអក្សរសិល្ប៍ដែលបុព្វបុរសបានបន្សល់ទុកមក។ "
        "អគុណដល់គ្រប់គ្នាដែលបានខិតខំប្រឹងប្រែងដើម្បីមាតុភូមិដ៏រុងរឿងរបស់យើង។"
    ]
    
    long_text = "\n\n".join(paragraphs)
    
    expected_errors = [
        # P1
        "សំរាប់", "ក្រោយយ", "វិចិត្ររ", "សំរាប់", "ការពាររ", "បូរាណណ", "អោយ",
        # P2
        "បច្ចុប្បន្នភាពព", "ស្រួលល", "អិនធឺណិត", "បច្ចេកវិជ្ជា", "អោយ", "សុវត្ថិភាពភា",
        # P3
        "សាលារៀនន", "ចំណេះដឺង", "បច្ចេកទេសស", "សីលធម៏", "សុជីវធម៏", "កតញ្ញ", "ចាស់ទុំម",
        # P4
        "ប្រពៃណ", "អភិវឌ្ឍន៏", "ជោគជយ", "មោទនភាពព", "អគុណ"
    ]
    
    print(f"\nTesting Long Text (Length: {len(long_text)} characters, {len(paragraphs)} paragraphs):")
    print("-" * 100)
    print(long_text)
    print("-" * 100)
    
    start_check = time.time()
    
    # 1. Segment
    tokens = segment_text(long_text)
    
    # 2. Tag
    tagged = pos_tag_tokens(tuple(tokens), word_to_pos, word_set)
    
    # 3. Detect
    errors = {}
    error_indices = detect_error_slots(tagged, word_set, word_list, bigrams, {}, errors, word_freq)
    detect_grammar_errors(tagged, errors)
    
    check_duration = time.time() - start_check
    
    detected_tokens = []
    for idx in errors:
        detected_tokens.append(errors[idx]['original'])
    for idx in error_indices:
        token_text = tagged[idx]['token']
        if token_text not in detected_tokens:
            detected_tokens.append(token_text)
            
    detected_set = set(detected_tokens)
    
    print(f"\nCheck completed in {check_duration:.3f}s")
    print("-" * 100)
    
    found_expected = []
    missed_expected = []
    
    for e in expected_errors:
        # Check for exact, or partial match logic consistent with v2
        is_found = False
        if e in detected_set:
            is_found = True
        else:
            for d in detected_set:
                if e in d or d in e:
                    # Heuristic: if d is just a single character like 'រ' or 'ន', 
                    # check if the expected error 'e' ends with it.
                    if len(d) <= 2 and e.endswith(d):
                        is_found = True
                        break
                    if e in d:
                        is_found = True
                        break
        
        if is_found:
            found_expected.append(e)
        else:
            missed_expected.append(e)
            
    # Remove duplicates from lists for clean reporting
    found_expected_unique = sorted(list(set(found_expected)))
    missed_expected_unique = sorted(list(set(missed_expected)))
    
    print(f"Results:")
    print(f"Expected Unique Error Tokens: {len(set(expected_errors))}")
    print(f"Total Detected Unique Tokens: {len(detected_set)}")
    print(f"Successfully Found: {len(found_expected_unique)}/{len(set(expected_errors))} ({len(found_expected_unique)/len(set(expected_errors))*100:.1f}%)")
    
    if missed_expected_unique:
        print(f"\nMissed Errors: {missed_expected_unique}")
        
    print("\nSample of Detected Tokens:")
    print(sorted(list(detected_set))[:20], "...")
    
    print("-" * 100)
    print("=" * 100)

if __name__ == "__main__":
    run_long_text_test_v3()
