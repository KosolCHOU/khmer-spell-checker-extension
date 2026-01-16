
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

def run_long_text_test_v2():
    print("=" * 100)
    print("RUNNING KHMER SPELL CHECKER LONG TEXT STRESS TEST (PHASE 3 - NEW TOPICS)")
    print("=" * 100)
    
    print("Initializing Spell Checker Data...")
    start_load = time.time()
    word_set, word_to_pos, word_freq, _ = SpellCheckerData.build_tables()
    word_list = SpellCheckerData.get_word_list()
    bigrams = SpellCheckerData.load_bigrams()
    print(f"Data loaded in {time.time() - start_load:.2f}s")
    
    paragraphs = [
        # P1: Tourism and Landmarks
        "វិស័យទេសចរណ៏គឺជាសសរស្តម្ភដ៏សំខាន់នៃសេដ្ឋកិច្ចកម្ពុជា។ ប្រាសាទអង្គរវត្តនិងប្រាសាទព្រះវិហាររគឺជាអត្តសញ្ញាណជាតិដែលទាក់ទាញភ្ញៀវមកពីគ្រប់ទិសទី។ "
        "យើងត្រូវរួមគ្នាថែរក្សាសោភ័ណភាពពនិងបរិស្ថានននៃតំបន់បេតិកភណ្ឌទាំងនេះ។ ការអភិវឌ្ឍន៏សក្តានុពលលទេសចរណ៍នឹងនាំមកនូវប្រាក់ចំណូលលដ៏ច្រើនសម្រាប់ជាតិ។",
        
        # P2: Agriculture and Environment
        "កសិកម្មមគឺជាឆ្អឹងខ្នងនៃសេដ្ឋកិច្ចដែលផ្គត់ផ្គង់ជីវភាពពប្រជាជនភាគច្រើន។ ទោះបីជាមានការផ្លាស់ប្តូររអាកាសធាតុយ៉ាងខ្លាំងក៏ដោយ "
        "កសិករយើងនៅតែខិតខំបង្កបង្កើនផលជានិច្ច។ ការប្រើប្រាស់បច្ចេកទេសថ្មីៗនិងជីធម្មជាតិជួយបង្កើនទិន្នផលលនិងការពារបរិស្ថានន។ "
        "យើងត្រូវរួមគ្នាដាំដើមឈើដើម្បីកាត់បន្ថយការភាយយនៃឧស្ម័នផ្ទះកញ្ចក់។",
        
        # P3: Education and STEM
        "ការវិនិយោគលើវិស័យអប់រំគឺជារឿងចាំបាច់សំរាប់ការអភិវឌ្ឍន៍ធនធានមនុស្ស។ សាលារៀននត្រូវពង្រឹងការបង្រៀនវិទ្យាសាស្ត្រនិងបច្ចេកវិទ្យាដល់សិស្សានុសិស្ស។ "
        "សិស្សត្រូវមានចំណេះដឺងនិងសមត្ថភាពពគ្រប់គ្រាន់ក្នុងសម័យឌីជីថល។ អាហារូបករណ៍គឺជាកាលានុវត្តភាពពដ៏សំខាន់សំរាប់យុវជនដែលខិតខំរៀនសូត្រត្រ។",
        
        # P4: Health and Wellbeing
        "សុខភាពពគឺជាទ្រព្យសម្បត្តិដ៏មានតំលៃបំផុតរបស់មនុស្សម្នាក់ៗ។ ក្នុងសម័យកាលមមាញឹកកនេះ យើងត្រូវចេះបែងចែកពេលវេលាសំរាប់ការហាត់ប្រាណនិងការសំរាកក។ "
        "ការរស់នៅស្អាតនិងការបរិភោគអាហារមានជីវជាតិជួយអោយរាងកាយរឹងមាំ។ សូមអោយកម្ពុជាក្លាយជាប្រទេសដែលមានសុខុមាលភាពពខ្ពស់សម្រាប់មនុស្សគ្រប់រូប។"
    ]
    
    long_text = "\n\n".join(paragraphs)
    
    expected_errors = [
        # P1
        "ទេសចរណ៏", "ព្រះវិហាររ", "សោភ័ណភាពព", "បរិស្ថានន", "អភិវឌ្ឍន៏", "សក្តានុពលល", "ចំណូលល",
        # P2
        "កសិកម្មម", "ជីវភាពព", "ផ្លាស់ប្តូររ", "ទិន្នផលល", "ភាយយ",
        # P3
        "សំរាប់", "សាលារៀនន", "ចំណេះដឺង", "សមត្ថភាពព", "កាលានុវត្តភាពព", "សូត្រត្រ",
        # P4
        "សុខភាពព", "តំលៃ", "មមាញឹកក", "សំរាកក", "អោយ", "សុខុមាលភាពព"
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
        # Check for exact, or if e is a substring of detected, or if detected contains the "meat" of the error
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
    found_expected = sorted(list(set(found_expected)))
    missed_expected = sorted(list(set(missed_expected)))
    
    print(f"Results:")
    print(f"Expected Unique Error Tokens: {len(set(expected_errors))}")
    print(f"Total Detected Unique Tokens: {len(detected_set)}")
    print(f"Successfully Found: {len(found_expected)}/{len(set(expected_errors))} ({len(found_expected)/len(set(expected_errors))*100:.1f}%)")
    
    if missed_expected:
        print(f"\nMissed Errors: {missed_expected}")
        
    print("\nSample of Detected Tokens:")
    print(sorted(list(detected_set))[:20], "...")
    
    print("-" * 100)
    print("=" * 100)

if __name__ == "__main__":
    run_long_text_test_v2()
