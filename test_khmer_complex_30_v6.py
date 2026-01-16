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
    
    # Test Set 6: Honorifics (Royal & Monk Language - Raja Sap)
    test_cases = [
        # Royal Titles & General
        {
            "text": "ព្រះករុណាព្រះបាទសម្តេចព្រះបរមនាថនរោត្តមសីហមុនីគឺជាព្រះមហាក្សត្រនៃព្រះរាជាណាចក្រកម្ពុជា។",
            "expected_valid": True,
            "category": "Royal Titles"
        },
        {
            "text": "ព្រះអង្គទ្រង់សព្វព្រះរាជហឫទ័យប្រោសព្រះរាជទានព្រះរាជទ្រព្យដល់ប្រជារាស្ត្រក្រីក្រ។",
            "expected_valid": True,
            "category": "Royal Action"
        },
        {
            "text": "សម្តេចព្រះមហាក្សត្រីនរោត្តមមុនិនាថសីហនុព្រះវររាជមាតាជាតិខ្មែរ។",
            "expected_valid": True,
            "category": "Royal Titles"
        },
        {
            "text": "ព្រះរាជពិធីបុណ្យអុំទូកបណ្តែតប្រទីបនិងសំពះព្រះខែត្រូវបានប្រារព្ធឡើងយ៉ាងអធិកអធម។",
            "expected_valid": True,
            "category": "Royal Ceremony"
        },
        {
            "text": "ព្រះរាជក្រឹត្យតែងតាំងមន្ត្រីរាជការជាន់ខ្ពស់ត្រូវបានចុះព្រះហត្ថលេខាដោយព្រះមហាក្សត្រ។",
            "expected_valid": True,
            "category": "Royal Decree"
        },
        
        # Royal Actions (Verbs)
        {
            "text": "ព្រះអង្គទ្រង់យាងទៅបំពេញព្រះរាជកិច្ចនៅតាមបណ្តាខេត្តនានាដើម្បីសួរសុខទុក្ខប្រជាពលរដ្ឋ។",
            "expected_valid": True,
            "category": "Royal Action"
        },
        {
            "text": "ព្រះមហាក្សត្រទ្រង់សោយព្រះស្ងោយនៅព្រះបរមរាជវាំងជាមួយភ្ញៀវកិត្តិយសអន្តរជាតិ។",
            "expected_valid": True,
            "category": "Royal Action"
        },
        {
            "text": "ព្រះអង្គទ្រង់ផ្ទុំនៅវេលាយប់ជ្រៅបន្ទាប់ពីបំពេញព្រះរាជកិច្ចដ៏មមាញឹក។",
            "expected_valid": True,
            "category": "Royal Action"
        },
        {
            "text": "ព្រះរាជសុខភាពរបស់ព្រះអង្គមានភាពល្អប្រសើរជាធម្មតាដោយមានការថែទាំពីក្រុមគ្រូពេទ្យ។",
            "expected_valid": True,
            "category": "Royal Health"
        },
        {
            "text": "ព្រះអង្គទ្រង់មានព្រះរាជបន្ទូលសំណេះសំណាលជាមួយសិស្សនិស្សិតដែលបានទទួលអាហារូបករណ៍។",
            "expected_valid": True,
            "category": "Royal Speech"
        },

        # Monk Language (Sangha)
        {
            "text": "សម្តេចព្រះសង្ឃរាជបាននិមន្តទៅចូលរួមពិធីបុណ្យវិសាខបូជានៅបរិវេណព្រះមហាស្តូប។",
            "expected_valid": True,
            "category": "Monk Action"
        },
        {
            "text": "ព្រះសង្ឃកំពុងឆាន់ចង្ហាន់ពេលព្រឹកដែលពុទ្ធបរិស័ទបានយកមកប្រគេនដោយសទ្ធាជ្រះថ្លា។",
            "expected_valid": True,
            "category": "Monk Action"
        },
        {
            "text": "ព្រះតេជគុណបានសម្តែងធម៌ទេសនាអំពីអានិសង្សនៃការធ្វើបុណ្យនិងការរក្សាសីល។",
            "expected_valid": True,
            "category": "Monk Action"
        },
        {
            "text": "ព្រះសង្ឃដែលអាពាធត្រូវបានបញ្ជូនទៅព្យាបាលនៅមន្ទីរពេទ្យដោយមានការយកចិត្តទុកដាក់។",
            "expected_valid": True,
            "category": "Monk Health"
        },
        {
            "text": "ការប្រគេនចង្ហាន់និងបច្ច័យដល់ព្រះសង្ឃគឺជាការសន្សំបុណ្យកុសលសម្រាប់ជាតិមុខ។",
            "expected_valid": True,
            "category": "Monk Offering"
        },

        # Royal Objects & Places
        {
            "text": "ព្រះបរមរាជវាំងគឺជាកន្លែងគង់ប្រថាប់របស់ព្រះមហាក្សត្រនិងជាតំបន់ទេសចរណ៍ដ៏សំខាន់។",
            "expected_valid": True,
            "category": "Royal Place"
        },
        {
            "text": "ព្រះទីនាំងទេវាវិនិច្ឆ័យត្រូវបានប្រើប្រាស់សម្រាប់ពិធីរាជាភិសេកនិងពិធីបុណ្យជាតិធំៗ។",
            "expected_valid": True,
            "category": "Royal Place"
        },
        {
            "text": "ព្រះរាជបល្ល័ង្កត្រូវបានរចនាឡើងយ៉ាងវិចិត្រដោយជាងចម្លាក់ដ៏ជំនាញបំផុតនៃព្រះរាជាណាចក្រ។",
            "expected_valid": True,
            "category": "Royal Object"
        },
        {
            "text": "ព្រះខ័នរាជគឺជាគ្រឿងកកុធភណ្ឌមួយក្នុងចំណោមគ្រឿងកកុធភណ្ឌទាំងប្រាំសម្រាប់ព្រះមហាក្សត្រ។",
            "expected_valid": True,
            "category": "Royal Object"
        },
        {
            "text": "ព្រះរាជរថត្រូវបានតុបតែងលម្អដោយក្បាច់ក្បូររចនាខ្មែរយ៉ាងស្រស់ស្អាតសម្រាប់ពិធីដង្ហែ។",
            "expected_valid": True,
            "category": "Royal Object"
        },

        # Formal/Royal Vocabulary Mix
        {
            "text": "ព្រះរាជសាររបស់ព្រះមហាក្សត្របានអំពាវនាវឱ្យជនរួមជាតិរួបរួមសាមគ្គីគ្នាដើម្បីជាតិ។",
            "expected_valid": True,
            "category": "Royal Message"
        },
        {
            "text": "ព្រះរាជអំណោយរាប់ពាន់កញ្ចប់ត្រូវបានចែកជូនដល់ប្រជាពលរដ្ឋដែលរងគ្រោះដោយទឹកជំនន់។",
            "expected_valid": True,
            "category": "Royal Gift"
        },
        {
            "text": "ព្រះរាជតំណាងព្រះមហាក្សត្របានអញ្ជើញចូលរួមក្នុងពិធីសម្ពោធដាក់ឱ្យប្រើប្រាស់សាលារៀន។",
            "expected_valid": True,
            "category": "Royal Representative"
        },
        {
            "text": "ព្រះរាជពិធីច្រត់ព្រះនង្គ័លត្រូវបានប្រារព្ធឡើងដើម្បីផ្សងប្រផ្នូលអំពីទិន្នផលកសិកម្ម។",
            "expected_valid": True,
            "category": "Royal Ceremony"
        },
        {
            "text": "ព្រះបរមសពរបស់អតីតព្រះមហាក្សត្រត្រូវបានតម្កល់ទុកក្នុងព្រះបរមកោដ្ឋដើម្បីធ្វើបុណ្យ។",
            "expected_valid": True,
            "category": "Royal Funeral"
        },

        # Complex Honorific Sentences
        {
            "text": "សូមព្រះអង្គទ្រង់ព្រះរាជទានព្រះរាជអនុញ្ញាតឱ្យទូលព្រះបង្គំបានចូលគាល់ដើម្បីថ្វាយរបាយការណ៍។",
            "expected_valid": True,
            "category": "Royal Request"
        },
        {
            "text": "ទូលព្រះបង្គំជាខ្ញុំសូមព្រះបរមរាជានុញ្ញាតសម្តែងនូវកតញ្ញូតាធម៌ដ៏ជ្រាលជ្រៅបំផុត។",
            "expected_valid": True,
            "category": "Royal Formal"
        },
        {
            "text": "ព្រះករុណាជាអម្ចាស់ជីវិតលើត្បូងទ្រង់ប្រកបដោយទសពិធរាជធម៌ក្នុងការដឹកនាំប្រទេសជាតិ។",
            "expected_valid": True,
            "category": "Royal Virtue"
        },
        {
            "text": "ព្រះសង្ឃរាជទ្រង់មានព្រះបន្ទូលដាស់តឿនពុទ្ធបរិស័ទឱ្យប្រកាន់ខ្ជាប់នូវអំពើល្អនិងសីលធម៌។",
            "expected_valid": True,
            "category": "Monk Speech"
        },
        {
            "text": "ការយាងសោយទិវង្គតរបស់ព្រះមហាវីរក្សត្រគឺជាការបាត់បង់ដ៏ធំធេងសម្រាប់ប្រជាជាតិខ្មែរទាំងមូល។",
            "expected_valid": True,
            "category": "Royal Death"
        }
    ]

    print(f"Running 30 Complex Test Cases (Set 6 - Honorifics)...")
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
