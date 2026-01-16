
import sys
import os
import json
from typing import List, Dict

# Add parent directory to path to import spell_checker_advanced
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))

try:
    from landing.spell_checker_advanced import check_spelling
except ImportError:
    print("Error: Could not import spell_checker_advanced. Make sure you are running this from the correct directory.")
    sys.exit(1)

TEST_CASES = [
    # === CATEGORY 1: CONTEXTUAL ERRORS (និង vs នឹង) ===
    {
        "description": "Rule A: Incorrect 'និង' (and) instead of 'នឹង' (will)",
        "text": "ខ្ញុំនិងទៅសាលារៀននៅថ្ងៃស្អែក។",
        "expected_error": "និង",
        "suggestion": "នឹង"
    },
    {
        "description": "Rule A: Correct 'នឹង' (will)",
        "text": "ស្អែកនេះខ្ញុំនឹងទៅលេងស្រុកកំណើត។",
        "is_correct": True
    },
    {
        "description": "Rule B: Incorrect 'នឹង' (will) instead of 'និង' (and) between nouns",
        "text": "ខ្ញុំទិញសៀវភៅនឹងប៊ិចនៅបណ្ណាគារ។",
        "expected_error": "នឹង",
        "suggestion": "និង"
    },
    {
        "description": "Rule B: Correct 'និង' (and) between nouns",
        "text": "ប៉ានិងម៉ាក់ទៅផ្សារជាមួយគ្នា។",
        "is_correct": True
    },

    # === CATEGORY 2: CONTEXTUAL ERRORS (នៅ vs នូវ) ===
    {
        "description": "Rule D: Incorrect 'នូវ' instead of 'នៅ' (location)",
        "text": "គាត់កំពុងទទួលទានអាហារនូវផ្ទះ។",
        "expected_error": "នូវ",
        "suggestion": "នៅ"
    },
    {
        "description": "Rule D: Correct 'នៅ' (location)",
        "text": "សៀវភៅនៅលើយន្តហោះ។",
        "is_correct": True
    },
    {
        "description": "Rule D: Incorrect 'នៅ' instead of 'នូវ' (object marker)",
        "text": "យើងត្រូវថែរក្សានៅបរិស្ថាន។",
        "expected_error": "នៅ",
        "suggestion": "នូវ"
    },
    {
        "description": "Rule D: Correct 'នូវ' (object marker)",
        "text": "រដ្ឋាភិបាលបានដាក់ចេញនូវគោលនយោបាយថ្មី។",
        "is_correct": True
    },

    # === CATEGORY 3: CONTEXTUAL ERRORS (ពី vs ពីរ) ===
    {
        "description": "Rule E: Incorrect 'ពីរ' (two) instead of 'ពី' (from)",
        "text": "គាត់ទើបតែមកពីរភ្នំពេញ។",
        "expected_error": "ពីរ",
        "suggestion": "ពី"
    },
    {
        "description": "Rule E: Correct 'ពី' (from)",
        "text": "ខ្ញុំទទួលបានដំណឹងនេះពីមិត្តភក្តិ។",
        "is_correct": True
    },
    {
        "description": "Rule E: Incorrect 'ពី' (from) instead of 'ពីរ' (number two)",
        "text": "ខ្ញុំមានបងប្អូនចំនួនពីនាក់។",
        "expected_error": "ពី",
        "suggestion": "ពីរ"
    },

    # === CATEGORY 4: CONTEXTUAL ERRORS (ដែល vs ដែរ) ===
    {
        "description": "Rule 7: Incorrect 'ដែរ' instead of 'ដែល' (relative pronoun)",
        "text": "នេះគឺជាផ្ទះដែរខ្ញុំធ្លាប់រស់នៅ។",
        "expected_error": "ដែរ",
        "suggestion": "ដែល"
    },
    {
        "description": "Rule 7: Correct 'ដែល' (relative pronoun)",
        "text": "មនុស្សដែលខិតខំនឹងជោគជ័យ។",
        "is_correct": True
    },
    {
        "description": "Rule 7: Incorrect 'ដែល' instead of 'ដែរ' (also)",
        "text": "ខ្ញុំចង់ទៅលេងកំពតដែល។",
        "expected_error": "ដែល",
        "suggestion": "ដែរ"
    },
    {
        "description": "Rule 7: Correct 'ដែរ' (also)",
        "text": "គាត់ញ៉ាំបាយហើយ ខ្ញុំក៏ញ៉ាំដែរ។",
        "is_correct": True
    },

    # === CATEGORY 5: CLASSIFIERS (អ្នក vs នាក់) ===
    {
        "description": "Rule 2: Incorrect 'អ្នក' instead of 'នាក់' (classifier)",
        "text": "មានសិស្សចំនួនដប់អ្នកនៅក្នុងថ្នាក់។",
        "expected_error": "អ្នក",
        "suggestion": "នាក់"
    },
    {
        "description": "Rule 2: Correct 'នាក់' (classifier)",
        "text": "យើងមានគ្នាប្រាំនាក់។",
        "is_correct": True
    },
    {
        "description": "Rule 2: Incorrect 'នាក់' instead of 'អ្នក' (title)",
        "text": "នាក់គ្រូកំពុងបង្រៀនសិស្ស។",
        "expected_error": "នាក់",
        "suggestion": "អ្នក"
    },

    # === CATEGORY 6: ADJECTIVE MARKERS (ដ៏ vs ដល់) ===
    {
        "description": "Rule 8: Incorrect 'ដល់' instead of 'ដ៏' (adjective marker)",
        "text": "នេះគឺជាសមិទ្ធផលដល់ត្រចះត្រចង់។",
        "expected_error": "ដល់",
        "suggestion": "ដ៏"
    },
    {
        "description": "Rule 8: Correct 'ដ៏' (adjective marker)",
        "text": "កម្ពុជាមានវប្បធម៌ដ៏សម្បូរបែប។",
        "is_correct": True
    },
    {
        "description": "Rule 8 reverse: Incorrect 'ដ៏' instead of 'ដល់' (to/reach)",
        "text": "ខ្ញុំធ្វើដំណើរដ៏សាលារៀន។",
        "expected_error": "ដ៏",
        "suggestion": "ដល់"
    },

    # === CATEGORY 7: MEANING vs OF (នៃ vs ន័យ) ===
    {
        "description": "Rule 9: Incorrect 'ន័យ' instead of 'នៃ' (of)",
        "text": "នេះគឺជាបញ្ហាន័យសង្គម។",
        "expected_error": "ន័យ",
        "suggestion": "នៃ"
    },
    {
        "description": "Rule 9: Correct 'នៃ' (of)",
        "text": "ពណ៌នៃផ្កាឈូកស្អាតណាស់។",
        "is_correct": True
    },
    {
        "description": "Rule 9 reverse: Incorrect 'នៃ' instead of 'ន័យ' (meaning)",
        "text": "តើពាក្យនេះមាននៃយ៉ាងដូចម្តេច?",
        "expected_error": "នៃ",
        "suggestion": "ន័យ"
    },

    # === CATEGORY 8: COMMON SPELLING TYPOS ===
    {
        "description": "Spelling typo: សួសី្ដ -> សួស្ដី",
        "text": "សួសី្ដ តើអ្នកសុខសប្បាយទេ?",
        "expected_error": "សួសី្ដ",
        "suggestion": "សួស្ដី"
    },
    {
        "description": "Spelling typo: សុវត្តភាព -> សុវត្ថិភាព",
        "text": "យើងត្រូវគិតពីសុវត្តភាពជាចម្បង។",
        "expected_error": "សុវត្តភាព",
        "suggestion": "សុវត្ថិភាព"
    },
    {
        "description": "Spelling typo: កម្ពុជារ -> កម្ពុជា",
        "text": "ប្រទេសកម្ពុជារមានសន្តិភាព។",
        "expected_error": "កម្ពុជារ",
        "suggestion": "កម្ពុជា"
    },
    {
        "description": "Spelling typo: បច្ចេកវិទ្យា (missing subscript ជ)",
        "text": "បច្ចេកវិទ្យាកំពុងរីកចម្រើន។", # Correct
        "is_correct": True
    },
    {
        "description": "Spelling typo: បច្ចេកវិទ្យា -> បច្ឆេកវិទ្យា",
        "text": "បច្ឆេកវិទ្យាថ្មីៗមានច្រើនណាស់។",
        "expected_error": "បច្ឆេកវិទ្យា",
        "suggestion": "បច្ចេកវិទ្យា"
    },

    # === CATEGORY 9: DIACRITIC ERRORS (Bantak logic) ===
    {
        "description": "Rule 8: Incorrect Bantak placement",
        "text": "កា់រងារនេះពិបាកណាស់។", # Bantak on Ko
        "expected_error": "កា់រងារ",
        "suggestion": "ការងារ"
    },
    {
        "description": "Missing ending consonant/vowel",
        "text": "ខ្ញុំចូលចិត្តញ៉ាំបា។", # Should be បាយ
        "expected_error": "បា",
        "suggestion": "បាយ"
    },

    # === CATEGORY 10: COMPLEX COMPOUND WORDS & FALSE POSITIVES ===
    {
        "description": "Valid long compound word",
        "text": "ព្រះរាជាណាចក្រកម្ពុជាគឺជាប្រទេសអច្ឆរិយៈ។",
        "is_correct": True
    },
    {
        "description": "Valid word with diverse characters",
        "text": "ឡានក្រុងសាធារណៈជួយកាត់បន្ថយស្ទះចរាចរណ៍។",
        "is_correct": True
    },
    {
        "description": "Technical term: Blockchain (Transliterated)",
        "text": "បច្ចេកវិទ្យា ប្លុកឆេន កំពុងពេញនិយម។",
        "is_correct": True
    },
    {
        "description": "Technical term: AI (Transliterated) - may need whitelist",
        "text": "បញ្ញាសិប្បនិម្មិត ជួយសម្រួលការងារមនុស្ស។",
        "is_correct": True
    },

    # === CATEGORY 11: HISTORICAL NAMES (False Positives) ===
    {
        "description": "Historical name: Jayavarman VII",
        "text": "ព្រះបាទជ័យវរ្ម័នទី៧ សាងសង់ប្រាសាទបាយ័ន។",
        "is_correct": True
    },
    {
        "description": "Historical name: Suryavarman II",
        "text": "ប្រាសាទអង្គរវត្តសាងសង់ដោយព្រះបាទសូរ្យវរ្ម័នទី២។",
        "is_correct": True
    },

    # === CATEGORY 12: PUNCTUATION SPACING ===
    {
        "description": "Rule 10: Missing space before colon",
        "text": "បញ្ជីរួមមាន៖សៀវភៅ ប៊ិច និងបន្ទាត់។", # Missing space after colon is common
        "expected_error": "រួមមាន៖សៀវភៅ", # Might be treated as one token if not handled
        "suggestion": "រួមមាន៖ សៀវភៅ"
    },
    {
        "description": "Rule 10: Double punctuation",
        "text": "តើអ្នកទៅណា??",
        "expected_error": "??",
        "suggestion": "?"
    },

    # === CATEGORY 13: HONORIFICS (Rule 5) ===
    {
        "description": "Rule 5: Status Mismatch - Common word with Royal status",
        "text": "ខ្ញុំសោយបាយល្ងាច។", # 'សោយ' is for Royals, used with 'ខ្ញុំ' (I)
        "expected_error": "សោយ",
        "suggestion": "ញ៉ាំ"
    },
    {
        "description": "Rule 5: Status Mismatch - King with common word",
        "text": "ព្រះមហាក្សត្រញ៉ាំបាយ។", # Should be 'សោយ'
        "expected_error": "ញ៉ាំ",
        "suggestion": "សោយ"
    },

    # === CATEGORY 14: MODERN SLANG / LOAN WORDS (Potential False Positives) ===
    {
        "description": "Slang/Loan: 'ហ្វ្រី' (Free)",
        "text": "សេវាកម្មនេះគឺ ហ្វ្រី សម្រាប់សមាជិក។",
        "is_correct": True # Should be whitelisted or accepted
    },
    {
        "description": "Loan: 'អាយធី' (IT)",
        "text": "ប្អូនប្រុសខ្ញុំរៀនផ្នែក អាយធី។",
        "is_correct": True
    },
    # === CATEGORY 15: ADDITIONAL CONTEXTUAL & GRAMMAR ===
    {
        "description": "Rule 6: Verb vs Noun suffix (ការងារ vs ការងា)",
        "text": "គាត់កំពុងធ្វើការងាជាអ្នកគិតលុយ។",
        "expected_error": "ការងា",
        "suggestion": "ការងារ"
    },
    {
        "description": "Rule: 'សស្រាក់សស្រាំ' (Diligently) misspelling",
        "text": "ពួកគេធ្វើការសស្រាក់សស់្រាំ។",
        "expected_error": "សស្រាក់សស់្រាំ",
        "suggestion": "សស្រាក់សស្រាំ"
    },
    {
        "description": "Rule: 'គម្រោង' (Project) vs 'គំរោង' (Old spelling)",
        "text": "គំរោងនេះនឹងចាប់ផ្តើមឆាប់ៗ។",
        "expected_error": "គំរោង", # Standard is often គម្រោង
        "suggestion": "គម្រោង"
    },
    {
        "description": "Rule: 'ពិសោធន៍' (Experience/Test) vs 'ពិសោធ' (Incomplete)",
        "text": "ការពិសោធនេះទទួលបានជោគជ័យ។",
        "is_correct": True
    },
    {
        "description": "Rule: 'អាសយដ្ឋាន' (Address) commonly misspelled",
        "text": "សូមបំពេញអាស័យដ្ឋានរបស់អ្នក។",
        "expected_error": "អាស័យដ្ឋាន",
        "suggestion": "អាសយដ្ឋាន"
    },
    {
        "description": "Rule: 'សកម្មភាព' (Activity) misspelling",
        "text": "យើងមានសកម្មភាជាច្រើន។",
        "expected_error": "សកម្មភា",
        "suggestion": "សកម្មភាព"
    },
    {
        "description": "Rule: 'ជោគជ័យ' (Success) typo",
        "text": "សូមជូនពរឱ្យទទួលបានជោគជយ។",
        "expected_error": "ជោគជយ",
        "suggestion": "ជោគជ័យ"
    },
    {
        "description": "Rule: 'អរគុណ' (Thank you) typo",
        "text": "អគុណច្រើនសម្រាប់ជំនួយ។",
        "expected_error": "អគុណ",
        "suggestion": "អរគុណ"
    },
    {
        "description": "Rule: 'អនាគត' (Future) typo",
        "text": "ដើម្បីអនាគរដ៏ល្អរបស់កូន។",
        "expected_error": "អនាគរ",
        "suggestion": "អនាគត"
    },
    {
        "description": "Rule: 'សហគមន៍' (Community) typo",
        "text": "ការអភិវឌ្ឍសហគមន៏មូលដ្ឋាន។",
        "expected_error": "សហគមន៏",
        "suggestion": "សហគមន៍"
    },
    {
        "description": "Rule: 'ទំនួលខុសត្រូវ' (Responsibility) typo",
        "text": "មន្ត្រីមានទំនួលខុសត្រួវខ្ពស់។",
        "expected_error": "ទំនួលខុសត្រួវ",
        "suggestion": "ទំនួលខុសត្រូវ"
    },
    {
        "description": "Rule: 'សីលធម៌' (Morality) vs 'សីលធម៏' (Incorrect diacritic)",
        "text": "យុវជនត្រូវមានសីលធម៏ល្អ។",
        "expected_error": "សីលធម៏",
        "suggestion": "សីលធម៌"
    },
    {
        "description": "Rule: 'សហគ្រាស' (Enterprise) typo",
        "text": "សហគ្រាធុនតូចនិងមធ្យម។",
        "expected_error": "សហគ្រា",
        "suggestion": "សហគ្រាស"
    },
    {
        "description": "Rule: 'ផលិតផល' (Product) typo",
        "text": "ផលិតផល់ក្នុងស្រុកមានគុណភាព។",
        "expected_error": "ផលិតផល់",
        "suggestion": "ផលិតផល"
    },
    {
        "description": "Rule: 'បរិស្ថាន' (Environment) typo",
        "text": "ការពារបរិស្ថាគឺការពារជីវិត។",
        "expected_error": "បរិស្ថា",
        "suggestion": "បរិស្ថាន"
    },
    {
        "description": "Rule: 'សុខុមាលភាព' (Well-being) typo",
        "text": "ដើម្បីសុខុមាលភាសង្គម។",
        "expected_error": "សុខុមាលភា",
        "suggestion": "សុខុមាលភាព"
    },
    {
        "description": "Rule: 'ជីវភាព' (Livelihood) typo",
        "text": "លើកកម្ពស់ជីវភាប្រជាជន។",
        "expected_error": "ជីវភា",
        "suggestion": "ជីវភាព"
    },
    {
        "description": "Rule: 'រដ្ឋាភិបាល' (Government) typo",
        "text": "គោលនយោបាយរបស់រដ្ឋាភិបារ។",
        "expected_error": "រដ្ឋាភិបារ",
        "suggestion": "រដ្ឋាភិបាល"
    },
    {
        "description": "Rule: 'មោទនភាព' (Pride) typo",
        "text": "ខ្ញុំមានមោទនភាចំពោះជាតិ។",
        "expected_error": "មោទនភា",
        "suggestion": "មោទនភាព"
    },
    {
        "description": "Rule: 'សញ្ញាបត្រ' (Diploma) typo",
        "text": "គាត់ទទួលបានសញ្ញាប័ត្រ។", # Both common, but standard differs
        "is_correct": True
    },
    {
        "description": "Rule: 'កិច្ចសហប្រតិបត្តិការ' (Cooperation) complex word",
        "text": "ពង្រឹងកិច្ចសហប្រតិបត្តិការអន្តរជាតិ។",
        "is_correct": True
    },
    {
        "description": "Rule: 'ទស្សនវិជ្ជា' (Philosophy) typo",
        "text": "ការសិក្សាផ្នែកទស្សនវិជ្ចា។",
        "expected_error": "ទស្សនវិជ្ចា",
        "suggestion": "ទស្សនវិជ្ជា"
    },
    {
        "description": "Rule: 'វិទ្យាសាស្ត្រ' (Science) typo",
        "text": "វិទ្យាសាស្ត្រនិងបច្ចេកវិទ្យា។",
        "is_correct": True
    },
    {
        "description": "Rule: 'ឧស្សាហកម្ម' (Industry) typo",
        "text": "បដិវត្តន៍ឧស្សាហកម្មទី៤។",
        "is_correct": True
    },
    {
        "description": "Rule: 'សេដ្ឋកិច្ច' (Economy) typo",
        "text": "កំណើនសេដ្ឋកិច្ចមានស្ថិរភាព។",
        "is_correct": True
    },
    {
        "description": "Rule: 'វប្បធម៌' (Culture) typo",
        "text": "ថែរក្សាវប្បធម៏ខ្មែរ។",
        "expected_error": "វប្បធម៏",
        "suggestion": "វប្បធម៌"
    },
    {
        "description": "Rule: 'ប្រពៃណី' (Tradition) typo",
        "text": "ទំនៀមទម្លាប់ប្រពៃណ៏។",
        "expected_error": "ប្រពៃណ៏",
        "suggestion": "ប្រពៃណី"
    },
    {
        "description": "Rule: 'ទេសចរណ៍' (Tourism) typo",
        "text": "វិស័យទេសចរណ៏រីកចម្រើន។",
        "expected_error": "ទេសចរណ៏",
        "suggestion": "ទេសចរណ៍"
    },
    {
        "description": "Rule: 'សន្តិសុខ' (Security) typo",
        "text": "រក្សាសន្តិសុខសណ្តាប់ធ្នាប់។",
        "is_correct": True
    },
    {
        "description": "Rule: 'ជនពិការ' (Person with disability) typo",
        "text": "ជួយដល់ជនពិកា។",
        "expected_error": "ជនពិកា",
        "suggestion": "ជនពិការ"
    },
    {
        "description": "Rule: 'មនុស្សធម៌' (Humanitarian) typo",
        "text": "ការងារមនុស្សធម៏ជាប្រពៃណី។",
        "expected_error": "មនុស្សធម៏",
        "suggestion": "មនុស្សធម៌"
    },
    {
        "description": "Rule: 'មហាសន្និបាត' (General Assembly) complex word",
        "text": "មហាសន្និបាតអង្គការសហប្រជាជាតិ។",
        "is_correct": True
    },
    {
        "description": "Rule: 'យុត្តិធម៌' (Justice) typo",
        "text": "ប្រព័ន្ធយុត្តិធម៏មានតម្លាភាព។",
        "expected_error": "យុត្តិធម៏",
        "suggestion": "យុត្តិធម៌"
    },
    {
        "description": "Rule: 'ស្ថិរភាព' (Stability) typo",
        "text": "រក្សាស្ថិរភាសន្តិសុខជាតិ។",
        "expected_error": "ស្ថិរភា",
        "suggestion": "ស្ថិរភាព"
    },
    {
        "description": "Rule: 'អធិបតេយ្យភាព' (Sovereignty) complex word",
        "text": "ការពារអធិបតេយ្យភាពជាតិ។",
        "is_correct": True
    },
    {
        "description": "Rule: 'ឯករាជ្យភាព' (Independence) typo",
        "text": "បុណ្យឯករាជ្យភាជាតិ។",
        "expected_error": "ឯករាជ្យភា",
        "suggestion": "ឯករាជ្យភាព"
    },
    {
        "description": "Rule: 'ប្រជាធិបតេយ្យ' (Democracy) typo",
        "text": "ការអនុវត្តប្រជាធិបតេយ្យ។",
        "is_correct": True
    },
    {
        "description": "Rule: 'សេរីភាព' (Freedom) typo",
        "text": "សេរីភាបញ្ចេញមតិ។",
        "expected_error": "សេរីភា",
        "suggestion": "សេរីភាព"
    },
    {
        "description": "Rule: 'សមភាព' (Equality) typo",
        "text": "សមភាយេនឌ័រ។",
        "expected_error": "សមភា",
        "suggestion": "សមភាព"
    },
    {
        "description": "Rule: 'តម្លាភាព' (Transparency) typo",
        "text": "អភិបាលកិច្ចល្អមានតម្លាភា។",
        "expected_error": "តម្លាភា",
        "suggestion": "តម្លាភាព"
    },
    {
        "description": "Rule: 'គណនេយ្យភាព' (Accountability) typo",
        "text": "ពង្រឹងគណនេយ្យភា។",
        "expected_error": "គណនេយ្យភា",
        "suggestion": "គណនេយ្យភាព"
    },
    {
        "description": "Rule: 'សកលភាវូបនីយកម្ម' (Globalization) complex word",
        "text": "ឥទ្ធិពលនៃសកលភាវូបនីយកម្ម។",
        "is_correct": True
    },
    {
        "description": "Rule: 'មនោគមវិជ្ជា' (Ideology) typo",
        "text": "មនោគមវិជ្ចាខុសគ្នា។",
        "expected_error": "មនោគមវិជ្ចា",
        "suggestion": "មនោគមវិជ្ជា"
    },
    {
        "description": "Rule: 'បេតិកភណ្ឌ' (Heritage) complex word",
        "text": "បេតិកភណ្ឌពិភពលោក។",
        "is_correct": True
    },
    {
        "description": "Rule: 'សប្បុរសធម៌' (Charity) typo",
        "text": "សកម្មភាពសប្បុរសធម៏។",
        "expected_error": "សប្បុរសធម៏",
        "suggestion": "សប្បុរសធម៌"
    },
    {
        "description": "Rule: 'វិបុលភាព' (Prosperity) typo",
        "text": "នាំមកនូវវិបុលភាជាតិ។",
        "expected_error": "វិបុលភា",
        "suggestion": "វិបុលភាព"
    },
    {
        "description": "Rule: 'កិច្ចសន្យា' (Contract) typo",
        "text": "ចុះហត្ថលេខាលើកិច្ចសន្យ។",
        "expected_error": "កិច្ចសន្យ",
        "suggestion": "កិច្ចសន្យា"
    },
    {
        "description": "Rule: 'សក្ខីកម្ម' (Testimony) typo",
        "text": "ផ្តល់សក្ខីកមនៅតុលាការ។",
        "expected_error": "សក្ខីកម",
        "suggestion": "សក្ខីកម្ម"
    },
    {
        "description": "Rule: 'នីតិវិធី' (Procedure) typo",
        "text": "អនុលោមតាមនីតិវិធុ។",
        "expected_error": "នីតិវិធុ",
        "suggestion": "នីតិវិធី"
    },
    {
        "description": "Rule: 'បទបញ្ញត្តិ' (Regulation) typo",
        "text": "ច្បាប់និងបទបញ្ញត្ដិ។", # Note character variation
        "is_correct": True
    },
    {
        "description": "Rule: 'អាជ្ញាប័ណ្ណ' (License) typo",
        "text": "មានអាជ្ញាប័ណ្ណត្រឹមត្រូវ។",
        "is_correct": True
    },
    {
        "description": "Rule: 'វិញ្ញាបនបត្រ' (Certificate) complex word",
        "text": "ទទួលបានវិញ្ញាបនបត្របញ្ជាក់ការសិក្សា។",
        "is_correct": True
    },
    # === CATEGORY 16: SEGMENTATION STRESS TEST (No spaces) ===
    {
        "description": "Long sentence without spaces (Valid)",
        "text": "ខ្ញុំទៅសាលារៀនជារៀងរាល់ថ្ងៃដើម្បីទទួលបានចំណេះដឹង។",
        "is_correct": True
    },
    {
        "description": "Long sentence without spaces (with typo: សាឡារៀន instead of សាលារៀន)",
        "text": "ខ្ញុំទៅសាឡារៀនជារៀងរាល់ថ្ងៃដើម្បីទទួលបានចំណេះដឹង។",
        "expected_error": "សាឡារៀន",
        "suggestion": "សាលារៀន"
    },
    {
        "description": "Complex joining: ប្រជាជនកម្ពុជាស្រលាញ់សន្តិភាព។",
        "is_correct": True,
        "text": "ប្រជាជនកម្ពុជាស្រលាញ់សន្តិភាព។"
    },
    {
        "description": "Complex joining with typo: បច្ចេកវិទ្យាថ្មីៗជួយកែលម្អជីវភា។",
        "text": "បច្ចេកវិទ្យាថ្មីៗជួយកែលម្អជីវភា។",
        "expected_error": "ជីវភា",
        "suggestion": "ជីវភាព"
    },
    {
        "description": "Religious text segment: ព្រះតេជគុណយាងទៅបិណ្ឌបាត។",
        "is_correct": True,
        "text": "ព្រះតេជគុណយាងទៅបិណ្ឌបាត។"
    },
    {
        "description": "Legal text segment: យោងតាមមាត្រាទី១នៃរដ្ឋធម្មនុញ្ញ។",
        "is_correct": True,
        "text": "យោងតាមមាត្រាទី១នៃរដ្ឋធម្មនុញ្ញ។"
    },
    {
        "description": "Economic text segment: ការនាំចេញអង្ករមានការកើនឡើងយ៉ាងខ្លាំងក្នុងឆ្នាំនេះ។",
        "is_correct": True,
        "text": "ការនាំចេញអង្ករមានការកើនឡើងយ៉ាងខ្លាំងក្នុងឆ្នាំនេះ។"
    },
    {
        "description": "Environment segment: ការប្រែប្រួលអាកាសធាតុជាបញ្ហាប្រឈមជាសកល។",
        "is_correct": True,
        "text": "ការប្រែប្រួលអាកាសធាតុជាបញ្ហាប្រឈមជាសកល។"
    },
    {
        "description": "Education segment: ការបណ្តុះបណ្តាលធនធានមនុស្សជាកត្តាសំខាន់សម្រាប់អភិវឌ្ឍន៍ជាតិ។",
        "is_correct": True,
        "text": "ការបណ្តុះបណ្តាលធនធានមនុស្សជាកត្តាសំខាន់សម្រាប់អភិវឌ្ឍន៍ជាតិ។"
    },
    {
        "description": "Technology stress: ការអភិវឌ្ឍកម្មវិធីទូរស័ព្ទដៃត្រូវការជំនាញខ្ពស់។",
        "is_correct": True,
        "text": "ការអភិវឌ្ឍកម្មវិធីទូរស័ព្ទដៃត្រូវការជំនាញខ្ពស់។"
    },
    {
        "description": "Medical stress: ការពិនិត្យសុខភាពជាទៀងទាត់ជួយបង្ការជំងឺ។",
        "is_correct": True,
        "text": "ការពិនិត្យសុខភាពជាទៀងទាត់ជួយបង្ការជំងឺ។"
    },
    {
        "description": "Agriculture stress: កសិករកំពុងប្រមូលផលស្រូវវស្សា។",
        "is_correct": True,
        "text": "កសិករកំពុងប្រមូលផលស្រូវវស្សា។"
    },
    {
        "description": "Tourism stress: ប្រាសាទអង្គរវត្តជាបេតិកភណ្ឌពិភពលោកដ៏អស្ចារ្យ។",
        "is_correct": True,
        "text": "ប្រាសាទអង្គរវត្តជាបេតិកភណ្ឌពិភពលោកដ៏អស្ចារ្យ។"
    },
    {
        "description": "Society stress: សមភាពសង្គមចាប់ផ្តើមពីការយល់ដឹងរបស់បុគ្គលម្នាក់ៗ។",
        "is_correct": True,
        "text": "សមភាពសង្គមចាប់ផ្តើមពីការយល់ដឹងរបស់បុគ្គលម្នាក់ៗ។"
    },
    {
        "description": "Sports stress: ការប្រកួតកីឡាស៊ីហ្គេមនៅកម្ពុជាទទួលបានជោគជ័យ។",
        "is_correct": True,
        "text": "ការប្រកួតកីឡាស៊ីហ្គេមនៅកម្ពុជាទទួលបានជោគជ័យ។"
    },
    {
        "description": "History stress: ប្រវត្តិសាស្ត្រខ្មែរមានភាពរុងរឿងក្នុងសម័យអង្គរ។",
        "is_correct": True,
        "text": "ប្រវត្តិសាស្ត្រខ្មែរមានភាពរុងរឿងក្នុងសម័យអង្គរ។"
    },
    {
        "description": "Literature stress: អក្សរសាស្ត្រខ្មែរឆ្លុះបញ្ចាំងពីព្រលឹងជាតិ។",
        "is_correct": True,
        "text": "អក្សរសាស្ត្រខ្មែរឆ្លុះបញ្ចាំងពីព្រលឹងជាតិ។"
    },
    {
        "description": "Art stress: របាំអប្សរាជាសិល្បៈវប្បធម៌ដ៏វិសេសវិសាល។",
        "is_correct": True,
        "text": "របាំអប្សរាជាសិល្បៈវប្បធម៌ដ៏វិសេសវិសាល។"
    },
    {
        "description": "Security stress: ស្ថាប័នមានសមត្ថកិច្ចកំពុងពង្រឹងសន្តិសុខ។",
        "is_correct": True,
        "text": "ស្ថាប័នមានសមត្ថកិច្ចកំពុងពង្រឹងសន្តិសុខ។"
    }
]

def run_test_suite():
    print("=" * 100)
    print(f"{'KHNER SPELL CHECKER COMPREHENSIVE TEST SUITE':^100}")
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
                        suggested = err_info['suggestions'][0] if err_info['suggestions'] else "None"
                        if case["suggestion"] == suggested:
                            details = f"Correctly suggested: {suggested}"
                        else:
                            details = f"Wrong suggestion: {suggested} (Exp: {case['suggestion']})"
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
    print(f"- Correct Detections: {passed}")
    print(f"- False Positives:    {false_positives}")
    print(f"- False Negatives:    {false_negatives}")
    print("=" * 100)

if __name__ == "__main__":
    run_test_suite()
