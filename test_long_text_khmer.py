
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

def run_long_text_test():
    print("=" * 100)
    print("RUNNING KHMER SPELL CHECKER LONG TEXT STRESS TEST (PHASE 2)")
    print("=" * 100)
    
    print("Initializing Spell Checker Data...")
    start_load = time.time()
    word_set, word_to_pos, word_freq, _ = SpellCheckerData.build_tables()
    word_list = SpellCheckerData.get_word_list()
    bigrams = SpellCheckerData.load_bigrams()
    print(f"Data loaded in {time.time() - start_load:.2f}s")
    
    paragraphs = [
        # P1: Culture and History
        "វប្បធម៏ខ្មែរគឺជាមរតដ៏អស្ចារ្យដែលបុព្វបុរសយើងបានបន្សល់ទុកអោយ។ យើងត្រូវចេះថែរក្សាប្រពៃណនិងសុជីវធម៏ខ្មែរជានិច្ច។ "
        "ទោះបីជាពិភពលោកមានការផ្លាស់ប្តូរយ៉ាងមោះមុតតក៏ដោយ ក៏យើងមិនត្រូវភ្លេចនូវឫសគល់បូរាណណរបស់យើងដែរ។ "
        "សិល្បៈនិងអក្សរសិល្ប៍ខ្មែរផ្តល់នូវចំណេះដឺងនិងបញ្ញារយ៉ាងជ្រាលជ្រៅសំរាប់យុវជនជំនាន់ក្រោយ។",
        
        # P2: Technology and Internet
        "សព្វថ្ងែនេះ ការសិក្សារតាមអិនធឺណិតបានក្លាយជាផ្នែកមួយមិនអាចខ្វះបាន។ សិស្សនុសិស្សប្រើបច្ចេកវិជ្ជាដើម្បីស្រាវជ្រាវពត៌មានផ្សេងៗ។ "
        "ទោះជាយ៉ាងណា តំលៃនៃឧបករណ៍បច្ចេកវិទ្យានៅមានកំរិតខ្ពស់សំរាប់គ្រួសារក្រីគ្រមួយចំនួន។ "
        "យើងសង្ឃឹមថាការអភិវឌ្ឍន៍នាពេលអនាគតតនឹងជួយកាត់បន្ថយគម្លាតឌីជីថលនេះបានសព្វគ្រប។",
        
        # P3: Economy and Workforce
        "កំលាំងពលកម្មគឺជាកត្តាកំណត់ក្នុងការសំរេចជោគជ័យនៃសេដ្ឋកិច្ចជាតិ។ ការប្រកួតប្រជែនៅក្នុងទីផ្សារការងារសកលវិទ្យាល័យ "
        "តម្រូវឱ្យបុគ្គលម្នាក់ៗមានសមត្ថភាពនិងសីលធម៏ខ្ពស់។ បញ្ហាចរាចរណ៏ក៏ជាបញ្ហាប្រឈមដែលប៉ះពាល់ដល់ប្រសិទ្ធភាពការងាររាល់ថ្ងែ។ "
        "យើងត្រូវរួមគ្នាដោះស្រាយបញ្ហានេះដើម្បីរក្សាតុល្យភាសង្គម។",
        
        # P4: Conclusion and Future
        "ជាចុងក្រោយ សូមអោយលោកអ្នកជួបតែសំណាងល្អនឹងសុភមង្គលលក្នុងជីវិត។ សូមផ្ញើរនូវក្តីស្រឡាញ់ចេញពីបេះដូពិតៗ "
        "ដល់ប្រជាជនកម្ពុជាគ្រប់រូប។ ប្រសិនបើយើងម្នាក់ៗខិតខំប្រឹងប្រែង នោះជោគជយនឹងនៅមិនឆ្ងាយពីយើងឡើយ។ "
        "អគុណច្រើនសម្រាប់កិច្ចសហការដែលបានផ្តល់អោយកន្លងមក។"
    ]
    
    long_text = "\n\n".join(paragraphs)
    
    expected_errors = [
        # P1
        "វប្បធម៏", "អោយ", "ប្រពៃណ", "សុជីវធម៏", "មោះមុតត", "បូរាណណ", "ចំណេះដឺង", "បញ្ញារ", "សំរាប់",
        # P2
        "សព្វថ្ងែ", "សិក្សារ", "អិនធឺណិត", "សិស្សនុសិស្ស", "បច្ចេកវិជ្ជា", "ពត៌មាន", "តំលៃ", "សំរាប់", "ក្រីគ្រ", "អនាគតត", "សព្វគ្រប",
        # P3
        "កំលាំង", "សំរេច", "ប្រកួតប្រជែ", "សីលធម៏", "ចរាចរណ៏", "រាល់ថ្ងែ", "តុល្យភា",
        # P4
        "អោយ", "សុភមង្គលល", "ផ្ញើរ", "បេះដូ", "ជោគជយ", "អគុណ", "អោយ"
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
        if e in detected_set or any(e in d for d in detected_set):
            found_expected.append(e)
        else:
            missed_expected.append(e)
            
    # Remove duplicates from lists for clean reporting
    found_expected = sorted(list(set(found_expected)))
    missed_expected = sorted(list(set(missed_expected)))
    
    print(f"Results:")
    print(f"Expected Unique Error Tokens: {len(set(expected_errors))}")
    print(f"Total Detected Tokens: {len(detected_set)}")
    print(f"Successfully Found: {len(found_expected)}/{len(set(expected_errors))} ({len(found_expected)/len(set(expected_errors))*100:.1f}%)")
    
    if missed_expected:
        print(f"\nMissed Errors: {missed_expected}")
        
    print("\nSample of Detected Tokens:")
    print(sorted(list(detected_set))[:20], "...")
    
    print("-" * 100)
    print("=" * 100)

if __name__ == "__main__":
    run_long_text_test()
