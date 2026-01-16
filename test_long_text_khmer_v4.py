
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

def run_long_text_test_v4():
    print("=" * 100)
    print("RUNNING KHMER SPELL CHECKER LONG TEXT STRESS TEST (PHASE 5 - WAR & PEACE)")
    print("=" * 100)
    
    print("Initializing Spell Checker Data...")
    start_load = time.time()
    word_set, word_to_pos, word_freq, _ = SpellCheckerData.build_tables()
    word_list = SpellCheckerData.get_word_list()
    bigrams = SpellCheckerData.load_bigrams()
    print(f"Data loaded in {time.time() - start_load:.2f}s")
    
    paragraphs = [
        # P1: History and Conflict
        "សង្គ្រាមមបាននាំមកនូវការបំផ្លិចបំផ្លាញយ៉ាងខ្លាំងដល់ហេដ្ឋារចនាសម្ព័ន្ធនិងជីវិតមនុស្ស។ "
        "ប្រវត្តិសាស្ត្ររខ្មែរបានឆ្លងកាត់ដំណាក់កាលលដ៏លំបាកជាច្រើននៃជម្លោះផ្ទៃក្នុង។ "
        "យើងត្រូវចងចាំមនូវមេរៀននទាំងនេះដើម្បីកុំអោយសោកនាដកម្មមដដែលៗកើតឡើងវិញ។",
        
        # P2: Peace and Stability
        "សុខសន្តិភាគឺជាមូលដ្ឋានគ្រឹះដ៏សំខាន់សំរាប់ការអភិវឌ្ឍន៍សេដ្ឋកិច្ចនិងសង្គម។ "
        "កំលាំងប្រដាប់អាវុធត្រូវពង្រឹងសមត្ថភាពពដើម្បីការពាររអធិបតេយ្យភាពនិងបូរណភាពពទឹកដី។ "
        "យើងត្រូវរួមគ្នាថែរក្សាសន្តិសុនៅក្នុងតំបន់ឱ្យបានល្អប្រសើររជានិច្ច។",
        
        # P3: International Relations and Peacekeeping
        "កងទ័ពមួកខៀវកម្ពុជាបានចូលរួមក្នុងបេសកកម្មមរក្សាសន្តិភាពរបស់អង្គការសហប្រជាជាតិ។ "
        "នេះគឺជាមោទនភាពពជាតិដែលបង្ហាញពីមនសិការរនិងការទទួលខុសត្រូវខ្ពស់។ "
        "យើងទទួលបាននូវការកោតសរសើររពីសំណាក់សហគមន៍អន្តរជាតិជានិច្ច។",
        
        # P4: Conclusion and Future
        "ជាចុងក្រោយ យើងត្រូវរួមគ្នាការពាររសន្តិភាពអោយបានគង់វង្សសំរាប់កូនចៅជំនាន់ក្រោយយ។ "
        "សុខសន្តិភាមិនអាចកាត់ថ្លៃបានឡើយក្នុងដំណើររឆ្ពោះទៅរកភាពរុងរឿង។ "
        "អគុណដល់កងកំលាំងទាំងអស់ដែលបានលះបង់ដើម្បីសេចក្តីសុខរបស់ប្រជាជន។"
    ]
    
    long_text = "\n\n".join(paragraphs)
    
    expected_errors = [
        # P1
        "សង្គ្រាមម", "ប្រវត្តិសាស្ត្ររ", "ដំណាក់កាលល", "ចងចាំម", "មេរៀនន", "អោយ", "សោកនាដកម្មម",
        # P2
        "សុខសន្តិភា", "សំរាប់", "កំលាំង", "សមត្ថភាពព", "ការពាររ", "បូរណភាពព", "សន្តិសុ", "ប្រសើររ",
        # P3
        "បេសកកម្មម", "មោទនភាពព", "មនសិការរ", "កោតសរសើររ",
        # P4
        "ការពាររ", "អោយ", "សំរាប់", "ក្រោយយ", "សុខសន្តិភា", "ដំណើររ", "អគុណ", "កំលាំង"
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
        is_found = False
        if e in detected_set:
            is_found = True
        else:
            for d in detected_set:
                if e in d or d in e:
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
            
    # Remove duplicates
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
    run_long_text_test_v4()
