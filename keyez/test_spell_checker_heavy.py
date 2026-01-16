
import sys
import os
import json
from typing import List, Dict

# Add parent directory to path to import spell_checker_advanced
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))

try:
    from landing.spell_checker_advanced import check_spelling
except ImportError:
    # Try local import if running from the landing directory or similar
    try:
        from spell_checker_advanced import check_spelling
    except ImportError:
        print("Error: Could not import spell_checker_advanced. Make sure you are running this from the correct directory.")
        sys.exit(1)

TEST_CASES = [
    # === CATEGORY 1: ROYAL LANGUAGE & HONORIFICS (Correct) ===
    {
        "description": "Royal Language: King's full title",
        "text": "ព្រះករុណាព្រះបាទសម្តេចព្រះបរមនាថ នរោត្តម សីហមុនី ព្រះមហាក្សត្រនៃព្រះរាជាណាចក្រកម្ពុជា។",
        "is_correct": True
    },
    {
        "description": "Royal Language: Queen Mother",
        "text": "សម្តេចព្រះមហាក្សត្រី នរោត្តម មុនិនាថ សីហនុ ព្រះវររាជមាតាជាតិខ្មែរ។",
        "is_correct": True
    },
    {
        "description": "Honorifics: HE and Lady",
        "text": "ឯកឧត្តមនិងលោកជំទាវបានអញ្ជើញជាអធិបតីក្នុងពិធីសព្វថ្ងៃ។",
        "is_correct": True
    },

    # === CATEGORY 2: COMMON TYPOS (Spelling) ===
    {
        "description": "Typo: ពត៌មាន -> ព័ត៌មាន",
        "text": "ខ្ញុំបានទទួលពត៌មាននេះពីមិត្តភក្តិ។",
        "expected_error": "ពត៌មាន",
        "suggestion": "ព័ត៌មាន"
    },
    {
        "description": "Typo: សួរស្តី -> សួស្ដី",
        "text": "សួរស្តី តើអ្នកសុខសប្បាយជាទេ?",
        "expected_error": "សួរស្តី",
        "suggestion": "សួស្ដី"
    },
    {
        "description": "Typo: អោយ -> ឱ្យ",
        "text": "សូមអោយគាត់មកជួបខ្ញុំផង។",
        "expected_error": "អោយ",
        "suggestion": "ឱ្យ"
    },
    {
        "description": "Typo: សំរាប់ -> សម្រាប់",
        "text": "សៀវភៅនេះគឺសំរាប់អ្នកសិក្សាគ្រប់គ្នា។",
        "expected_error": "សំរាប់",
        "suggestion": "សម្រាប់"
    },
    {
        "description": "Typo: តំលៃ -> តម្លៃ",
        "text": "ទំនិញមានតំលៃសមរម្យ។",
        "expected_error": "តំលៃ",
        "suggestion": "តម្លៃ"
    },
    {
        "description": "Typo: ជំរាប -> ជម្រាប",
        "text": "សូមជំរាបសួរលោកគ្រូអ្នកគ្រូ។",
        "expected_error": "ជំរាប",
        "suggestion": "ជម្រាប"
    },

    # === CATEGORY 3: CONTEXTUAL ERRORS (និង/នឹង, នៅ/នូវ, ពី/ពីរ) ===
    {
        "description": "Context: និង (and) vs នឹង (will)",
        "text": "បងប្រុសខ្ញុំនិងទៅធ្វើការនៅភ្នំពេញ។",
        "expected_error": "និង",
        "suggestion": "នឹង"
    },
    {
        "description": "Context: នឹង (will) vs និង (and)",
        "text": "ខ្ញុំទិញផ្លែឈើនឹងបន្លែពីផ្សារ។",
        "expected_error": "នឹង",
        "suggestion": "និង"
    },
    {
        "description": "Context: នៅ (location) vs នូវ (object marker)",
        "text": "គាត់ស្នាក់នូវសណ្ឋាគារលំដាប់ផ្កាយប្រាំ។",
        "expected_error": "នូវ",
        "suggestion": "នៅ"
    },
    {
        "description": "Context: នូវ (object marker) vs នៅ (location)",
        "text": "យើងត្រូវតែគោរពនៅច្បាប់ចរាចរណ៍។",
        "expected_error": "នៅ",
        "suggestion": "នូវ"
    },
    {
        "description": "Context: ពី (from) vs ពីរ (number 2)",
        "text": "ខ្ញុំមានបងប្អូនស្រីពីរនាក់។", # Correct
        "is_correct": True
    },
    {
        "description": "Context: ពី (from) vs ពីរ (number 2) error",
        "text": "មិត្តភក្តិខ្ញុំមកពីរខេត្តសៀមរាប។",
        "expected_error": "ពីរ",
        "suggestion": "ពី"
    },

    # === CATEGORY 4: TECHNICAL & LOAN WORDS (Transliteration) ===
    {
        "description": "Loan: អ៊ីនធឺណែត -> អ៊ីនធឺណិត",
        "text": "ការប្រើប្រាស់អ៊ីនធឺណែតមានភាពងាយស្រួល។",
        "expected_error": "អ៊ីនធឺណែត",
        "suggestion": "អ៊ីនធឺណិត"
    },
    {
        "description": "Loan: កុំព្យូទ័រ vs កុងព្យូទ័រ",
        "text": "ម៉ាក់ទិញកុកព្យូទ័រថ្មីមួយសម្រាប់ប្អូន។", # Intentional typo 'កុកព្យូទ័រ'
        "expected_error": "កុកព្យូទ័រ",
        "suggestion": "កុំព្យូទ័រ"
    },
    {
        "description": "Loan: ហ្វេសប៊ុក (Correct)",
        "text": "ហ្វេសប៊ុកជាបណ្តាញសង្គមដ៏ពេញនិយម។",
        "is_correct": True
    },
    {
        "description": "Loan: ស្មាតហ្វូន (Correct)",
        "text": "ស្មាតហ្វូនជំនាន់ថ្មីជួយការងារច្រើនយ៉ាង។",
        "is_correct": True
    },

    # === CATEGORY 5: CONSONANT & VOWEL CONFUSIONS ===
    {
        "description": "Confusion: ជីរភាព -> ចីរភាព",
        "text": "ការអភិវឌ្ឍប្រកបដោយជីរភាពជាគោលដៅសំខាន់។",
        "expected_error": "ជីរភាព",
        "suggestion": "ចីរភាព"
    },
    {
        "description": "Confusion: គឺជារ -> គឺជា",
        "text": "ប្រទេសកម្ពុជាគឺជារព្រះរាជាណាចក្រអច្ឆរិយៈ។",
        "expected_error": "គឺជារ",
        "suggestion": "គឺជា"
    },
    {
        "description": "Confusion: សិក្សារ -> សិក្សា",
        "text": "ការសិក្សារគឺជាមូលដ្ឋាននៃចំណេះដឹង។",
        "expected_error": "សិក្សារ",
        "suggestion": "សិក្សា"
    },
    {
        "description": "Diacritic: ចរាចរណ៏ -> ចរាចរណ៍",
        "text": "សូមគោរពច្បាប់ចរាចរណ៏ទាំងអស់គ្នា។",
        "expected_error": "ចរាចរណ៏",
        "suggestion": "ចរាចរណ៍"
    },

    # === CATEGORY 6: SEGMENTATION STRESS TEST (Long Sentences, Double Errors) ===
    {
        "description": "Long sentence, no spaces, correct",
        "text": "យើងទាំងអស់គ្នាត្រូវរួមគ្នាថែរក្សាបរិស្ថានដើម្បីអនាគតដ៏ភ្លឺស្វាងនៃកូនចៅជំនាន់ក្រោយ។",
        "is_correct": True
    },
    {
        "description": "Double errors in long sentence",
        "text": "បញ្ញាសិប្បនិម្មិតកំនំពុងផ្លាស់ប្តូរការរស់នៅនិងការងាជារៀងរាល់ថ្ងៃរបស់មនុស្ស។", # typos: កំនំពុង, ការងា
        "expected_error": "កំនំពុង",
        "suggestion": "កំពុង"
    },
    {
        "description": "Missing subscript logic: បច្ឆេកវិទ្យា -> បច្ចេកវិទ្យា",
        "text": "បច្ឆេកវិទ្យាថ្មីៗជាច្រើនកំពុងជួយដល់ការសិក្សា។",
        "expected_error": "បច្ឆេកវិទ្យា",
        "suggestion": "បច្ចេកវិទ្យា"
    },

    # === CATEGORY 7: MODERN PHRASES & COMPOUNDS (Whitelist/Names) ===
    {
        "description": "Modern: ឃ្យូអរកូដ (Correct)",
        "text": "យើងអាចបង់ប្រាក់តាមរយៈឃ្យូអរកូដបានយ៉ាងងាយ។",
        "is_correct": True
    },
    {
        "description": "Names: លោក ដារ៉ា (Correct)",
        "text": "លោក ដារ៉ា កំពុងអានសៀវភៅនៅបណ្ណាល័យ។",
        "is_correct": True
    },
    {
        "description": "Names: កញ្ញា សោភា (Correct)",
        "text": "កញ្ញា សោភា គឺជាគ្រូបង្រៀនដ៏ឆ្នើម។",
        "is_correct": True
    },

    # === CATEGORY 8: FORMAL & LEGAL TERMS ===
    {
        "description": "Legal: រដ្ឋធម្មនុញ្ញ (Correct)",
        "text": "រដ្ឋធម្មនុញ្ញគឺជាច្បាប់កំពូលនៃប្រទេសកម្ពុជា។",
        "is_correct": True
    },
    {
        "description": "Formal: សហប្រតិបត្តិការ (Correct)",
        "text": "ការពង្រឹងសហប្រតិបត្តិការអន្តរជាតិមានសារៈសំខាន់ខ្លាំង។",
        "is_correct": True
    },
    {
        "description": "Formal: បដិវត្តន៍ឧស្សាហកម្មទី៤ (Correct)",
        "text": "យើងកំពុងស្ថិតក្នុងយុគសម័យនៃបដិវត្តន៍ឧស្សាហកម្មទី៤។",
        "is_correct": True
    },

    # === CATEGORY 9: SLANG & INFORMAL (Potential False Positives) ===
    {
        "description": "Informal: អីុ (Typo for អ្វី or Whitelisted variation)",
        "text": "កុំគិតច្រើនអីវាជារឿងធម្មតាទេ។",
        "is_correct": True
    },
    {
        "description": "Slang: ឡូយ (Cool - Correct)",
        "text": "ឡានថ្មីរបស់គាត់មើលទៅពិតជាឡូយណាស់។",
        "is_correct": True
    },

    # === CATEGORY 10: RARE WORD CONFUSION ===
    {
        "description": "Rare: រេន -> រៀន (Rare word confusion test)",
        "text": "កូនសិស្សត្រូវខិតខំរេនសូត្រ។", # 'រេន' might be in dict but rare
        "expected_error": "រេន",
        "suggestion": "រៀន"
    },
    {
        "description": "Rare: បាយណាស -> បាយណាស់",
        "text": "ម្ហូបនេះឆ្ងាញ់បាយណាស។",
        "expected_error": "បាយណាស",
        "suggestion": "បាយណាស់"
    },

    # === CATEGORY 11: PUNCTUATION & SYMBOLS ===
    {
        "description": "Punctuation: Space before colon",
        "text": "ទំនិញរួមមាន៖ អាហារ ភេសជ្ជៈ និងសម្លៀកបំពាក់។",
        "is_correct": True
    },
    {
        "description": "Symbols: Currency ៛ (Riel)",
        "text": "តម្លៃគឺ ១០០០០៛ ក្នុងមួយគីឡូក្រាម។",
        "is_correct": True
    },
    {
        "description": "Symbols: Percent %",
        "text": "កំណើនសេដ្ឋកិច្ចមានអត្រា ៧% ក្នុងមួយឆ្នាំ។",
        "is_correct": True
    },

    # === CATEGORY 12: COMPLEX COMPOUNDS (Stress tests) ===
    {
        "description": "Complex: សាកលវិទ្យាល័យភូមិន្ទភ្នំពេញ",
        "text": "គាត់រៀននៅសាកលវិទ្យាល័យភូមិន្ទភ្នំពេញ។",
        "is_correct": True
    },
    {
        "description": "Complex: វិទ្យាស្ថានបច្ចេកវិទ្យាកម្ពុជា",
        "text": "ប្អូនប្រុសខ្ញុំសិក្សានៅវិទ្យាស្ថានបច្ចេកវិទ្យាកម្ពុជា។",
        "is_correct": True
    },
    {
        "description": "Complex: កំពង់ផែស្វយ័តក្រុងព្រះសីហនុ",
        "text": "កំពង់ផែស្វយ័តក្រុងព្រះសីហនុជាច្រកសេដ្ឋកិច្ចសំខាន់។",
        "is_correct": True
    },

    # === CATEGORY 13: MORE TYPOS FROM CONSTANTS ===
    {
        "description": "Typo: អាគារ -> អគារ",
        "text": "អាគារខ្ពស់ៗកំពុងរីកដុះដាលនៅកណ្តាលក្រុង។",
        "expected_error": "អាគារ",
        "suggestion": "អគារ"
    },
    {
        "description": "Typo: វិធានការណ៍ -> វិធានការ",
        "text": "រដ្ឋាភិបាលដាក់ចេញវិធានការណ៍ថ្មីៗ។",
        "expected_error": "វិធានការណ៍",
        "suggestion": "វិធានការ"
    },
    {
        "description": "Typo: ស្រុកកំនើត -> ស្រុកកំណើត",
        "text": "ខ្ញុំនឹកស្រុកកំនើតរបស់ខ្ញុំណាស់។",
        "expected_error": "ស្រុកកំនើត",
        "suggestion": "ស្រុកកំណើត"
    },
    {
        "description": "Typo: ចំនាយ -> ចំណាយ",
        "text": "យើងត្រូវកាត់បន្ថយការចំនាយដែលមិនចាំបាច់។",
        "expected_error": "ចំនាយ",
        "suggestion": "ចំណាយ"
    },
    {
        "description": "Typo: សបាយ -> សប្បាយ",
        "text": "ថ្ងៃនេះខ្ញុំពិតជាសបាយចិត្តណាស់។",
        "expected_error": "សបាយ",
        "suggestion": "សប្បាយ"
    },
    # === CATEGORY 14: MEDICAL & SCIENCE TERMS ===
    {
        "description": "Medical: វ៉ាក់សាំង (Correct)",
        "text": "ការចាក់វ៉ាក់សាំងការពារជំងឺឆ្លងបានយ៉ាងល្អ។",
        "is_correct": True
    },
    {
        "description": "Medical: មន្ទីរពេទ្យ (Correct)",
        "text": "មន្ទីរពេទ្យគន្ធបុប្ផាជួយសង្គ្រោះកុមារកម្ពុជាជាច្រើន។",
        "is_correct": True
    },
    {
        "description": "Science: បរិយាកាស (Correct)",
        "text": "ការបំពុលបរិយាកាសជះឥទ្ធិពលដល់សុខភាពមនុស្ស។",
        "is_correct": True
    },
    {
        "description": "Science: រស្មីសំយោគ (Correct)",
        "text": "រុក្ខជាតិត្រូវការកម្តៅថ្ងៃដើម្បីធ្វើរស្មីសំយោគ។",
        "is_correct": True
    },

    # === CATEGORY 15: NAMES & GEOGRAPHY ===
    {
        "description": "Geography: ទន្លេសាប (Correct)",
        "text": "ទន្លេសាបជាបឹងទឹកសាបដ៏ធំបំផុតនៅអាស៊ីអាគ្នេយ៍។",
        "is_correct": True
    },
    {
        "description": "Geography: ភ្នំពេញ (Correct)",
        "text": "រាជធានីភ្នំពេញមានការអភិវឌ្ឍយ៉ាងរហ័ស។",
        "is_correct": True
    },
    {
        "description": "Location: សៀមរាប (Correct)",
        "text": "ខេត្តសៀមរាបជាគោលដៅទេសចរណ៍ដ៏ទាក់ទាញ។",
        "is_correct": True
    },

    # === CATEGORY 16: ADVANCED CONTEXTUAL ERRORS ===
    {
        "description": "Context: ពី vs ពីរ in same sentence",
        "text": "គាត់ទិញត្រីពីរក្បាលពីផ្សារក្បែរផ្ទះ។", # Correct
        "is_correct": True
    },
    {
        "description": "Context: Wrong ពីរ instead of ពី",
        "text": "ខ្ញុំទទួលបានកាដូនេះពីរមិត្តភក្តិរបស់ខ្ញុំ។",
        "expected_error": "ពីរ",
        "suggestion": "ពី"
    },
    {
        "description": "Context: Wrong ពី instead of ពីរ",
        "text": "មានសិស្សពីនាក់កំពុងឈរនៅមាត់ទ្វារ។",
        "expected_error": "ពី",
        "suggestion": "ពីរ"
    },

    # === CATEGORY 17: COMPOUND TYPOS & MISPLACED DIACRITICS ===
    {
        "description": "Typo: បច្ចេកវិជ្ជា vs បច្ចេកវិទ្យា",
        "text": "បច្ចេកវិជ្ជាកុំព្យូទ័រកំពុងរីកចម្រើន។",
        "expected_error": "បច្ចេកវិជ្ជា",
        "suggestion": "បច្ចេកវិទ្យា"
    },
    {
        "description": "Typo: ព័ត៌មាន misspelling",
        "text": "សូមអានព័តមាននេះឱ្យបានត្រឹមត្រូវ។", # Missing subscript logic or missing character
        "expected_error": "ព័តមាន",
        "suggestion": "ព័ត៌មាន"
    },
    {
        "description": "Typo: ពិបាក missing subscript",
        "text": "ការងារនេះពិបាកណាស់សម្រាប់ខ្ញុំ។", # Correct
        "is_correct": True
    },

    # === CATEGORY 18: MIXED LANGUAGE (False Positive Check) ===
    {
        "description": "Mixed: Khmer + English",
        "text": "ខ្ញុំប្រើ Facebook និង Telegram រាល់ថ្ងៃ។",
        "is_correct": True
    },
    {
        "description": "Mixed: Khmer + English AI",
        "text": "បច្ចេកវិទ្យា AI កំពុងមានឥទ្ធិពលលើពិភពលោក។",
        "is_correct": True
    },

    # === CATEGORY 19: ARCHAIC vs MODERN SPELLING ===
    {
        "description": "Spelling: គំរោង (Old) -> គម្រោង (New)",
        "text": "គំរោងសាងសង់ស្ពាននឹងចាប់ផ្តើមនៅខែក្រោយ។",
        "expected_error": "គំរោង",
        "suggestion": "គម្រោង"
    },
    {
        "description": "Spelling: អាស័យដ្ឋាន (Common) -> អាសយដ្ឋាន (Standard)",
        "text": "សូមបំពេញអាស័យដ្ឋានឱ្យបានត្រឹមត្រូវ។",
        "expected_error": "អាស័យដ្ឋាន",
        "suggestion": "អាសយដ្ឋាន"
    },

    # === CATEGORY 20: FRACTIONS & MEASUREMENTS ===
    {
        "description": "Measurement: គីឡូក្រាម (Correct)",
        "text": "ខ្ញុំទិញអង្ករចំនួន ៥០ គីឡូក្រាម។",
        "is_correct": True
    },
    {
        "description": "Measurement: គីឡូម៉ែត្រ (Correct)",
        "text": "ផ្លូវនេះមានប្រវែង ១០០ គីឡូម៉ែត្រ។",
        "is_correct": True
    },

    # === CATEGORY 21: SPECIFIC WORD ERRORS FROM LOGS ===
    {
        "description": "Word error: អាជ្ញាប័ណ្ណ (Correct)",
        "text": "ក្រុមហ៊ុនមានអាជ្ញាប័ណ្ណត្រឹមត្រូវតាមច្បាប់។",
        "is_correct": True
    },
    {
        "description": "Word error: វិញ្ញាបនបត្រ (Correct)",
        "text": "សិស្សទទួលបានវិញ្ញាបនបត្របញ្ជាក់ការសិក្សា។",
        "is_correct": True
    },
    {
        "description": "Word error: បណ្តុះបណ្តាល (Correct)",
        "text": "មជ្ឈមណ្ឌលនេះមានវគ្គបណ្តុះបណ្តាលវិជ្ជាជីវៈ។",
        "is_correct": True
    },
    {
        "description": "Word error: អភិវឌ្ឍ (Correct)",
        "text": "យើងត្រូវរួមគ្នាអភិវឌ្ឍសហគមន៍របស់យើង។",
        "is_correct": True
    },
    # === CATEGORY 22: MORE COMPLEX & RARE CASES ===
    {
        "description": "Rare: សូរ្យវរ្ម័ន (Historical - Correct)",
        "text": "ព្រះបាទសូរ្យវរ្ម័នទី២បានកសាងប្រាសាទអង្គរវត្ត។",
        "is_correct": True
    },
    {
        "description": "Historical: អាណាចក្រអង្គរ (Correct)",
        "text": "សម័យអាណាចក្រអង្គរគឺជាសម័យកាលដ៏រុងរឿងបំផុត។",
        "is_correct": True
    },
    {
        "description": "Complex: សេចក្តីសម្រេចចិត្ត (Correct)",
        "text": "នេះគឺជាសេចក្តីសម្រេចចិត្តមួយដ៏ពិបាក។",
        "is_correct": True
    },
    {
        "description": "Typo: បេតិកភណ្ឌ misspelling",
        "text": "យើងត្រូវការពារបេតិកភ័ណ្ឌជាតិ។", # Typo: ភ័ណ្ឌ vs ភណ្ឌ
        "expected_error": "បេតិកភ័ណ្ឌ",
        "suggestion": "បេតិកភណ្ឌ"
    },
    {
        "description": "Typo: ឧស្សាហកម្ម misspelling",
        "text": "វិស័យឧស្សាហកមផលិតផលកំពុងរីកចម្រើន។", # Typo: ឧស្សាហកម
        "expected_error": "ឧស្សាហកម",
        "suggestion": "ឧស្សាហកម្ម"
    },
    {
        "description": "Contextual: 'ពី' instead of 'ពីរ' with classifier",
        "text": "ខ្ញុំមានឆ្មាពីរក្បាលនៅផ្ទះ។", # Correct
        "is_correct": True
    },
    {
        "description": "Contextual: 'ពីរ' instead of 'ពី' location",
        "text": "គាត់ទើបតែមកពីរធ្វើការ។",
        "expected_error": "ពីរ",
        "suggestion": "ពី"
    },
    {
        "description": "Spelling: បញ្ញាសិប្បនិម្មិត (Correct)",
        "text": "បញ្ញាសិប្បនិម្មិតគឺជាអនាគតនៃបច្ចេកវិទ្យា។",
        "is_correct": True
    },
    {
        "description": "Spelling: ព័ត៌មាន (Correct)",
        "text": "ព័ត៌មានពិតជួយឱ្យយើងមានការយល់ដឹងច្រើន។",
        "is_correct": True
    },
    {
        "description": "Typo: សាកលវិទ្យាល័យ (Correct)",
        "text": "សាកលវិទ្យាល័យភូមិន្ទភ្នំពេញជាសាលាដ៏ល្បី។",
        "is_correct": True
    },
    {
        "description": "Typo: សាលារៀន (Correct)",
        "text": "ក្មេងៗសប្បាយចិត្តនឹងការទៅសាលារៀន។",
        "is_correct": True
    },
    {
        "description": "Modern: ឌីជីថល (Correct)",
        "text": "ការអប់រំតាមបែបឌីជីថលមានសារៈសំខាន់ណាស់។",
        "is_correct": True
    },
    {
        "description": "Modern: អនឡាញ (Correct)",
        "text": "ការទិញទំនិញអនឡាញកំពុងពេញនិយម។",
        "is_correct": True
    },
    {
        "description": "Typo: អាសយដ្ឋាន (Correct)",
        "text": "សូមផ្ញើអាសយដ្ឋានរបស់អ្នកមកខ្ញុំ។",
        "is_correct": True
    },
    {
        "description": "Typo: ជោគជ័យ (Correct)",
        "text": "សូមជូនពរឱ្យអ្នកទទួលបានជោគជ័យគ្រប់ភារកិច្ច។",
        "is_correct": True
    },
    {
        "description": "Typo: បរិស្ថាន (Correct)",
        "text": "ការថែរក្សាបរិស្ថានជាកាតព្វកិច្ចរបស់បុគ្គលគ្រប់រូប។",
        "is_correct": True
    },
    {
        "description": "Typo: សុខភាព (Correct)",
        "text": "សុខភាពគឺជាទ្រព្យសម្បត្តិដ៏មហាសាល។",
        "is_correct": True
    },
    # === CATEGORY 23: ADDITIONAL STRESS CASES & FINAL SET ===
    {
        "description": "Modern: តេឡេក្រាម (Correct)",
        "text": "បច្ចុប្បន្នយើងប្រើតេឡេក្រាមដើម្បីទំនាក់ទំនងគ្នា។",
        "is_correct": True
    },
    {
        "description": "Modern: យូធូប (Correct)",
        "text": "ក្មេងៗចូលចិត្តមើលវីដេអូកម្សាន្តនៅលើយូធូប។",
        "is_correct": True
    },
    {
        "description": "Typo: បាក់តេរី (Correct)",
        "text": "យើងត្រូវលាងដៃឱ្យស្អាតដើម្បីការពារបាក់តេរី។",
        "is_correct": True
    },
    {
        "description": "Typo: វីរុស (Correct)",
        "text": "វីរុសកូរ៉ូណាបានបង្កផលប៉ះពាល់ដល់ពិភពលោក។",
        "is_correct": True
    },
    {
        "description": "Contextual: 'និង' vs 'នឹង' combined",
        "text": "ស្អែកនេះខ្ញុំនឹងទិញសៀវភៅនិងប៊ិច។", # Correct
        "is_correct": True
    },
    {
        "description": "Typo: រចនាប័ទ្ម (Correct)",
        "text": "ប្រាសាទខ្មែរមានរចនាប័ទ្មខុសៗគ្នាទៅតាមសម័យកាល។",
        "is_correct": True
    },
    {
        "description": "Typo: សោភ័ណភាព (Correct)",
        "text": "ការរៀបចំទីក្រុងឱ្យមានសោភ័ណភាពជួយទាក់ទាញទេសចរ។",
        "is_correct": True
    },
    {
        "description": "Typo: សមត្ថភាព (Correct)",
        "text": "យើងត្រូវពង្រឹងសមត្ថភាពខ្លួនឯងជានិច្ច។",
        "is_correct": True
    },
    {
        "description": "Typo: ស្ថិរភាព (Correct)",
        "text": "ស្ថិរភាពនយោបាយជាកត្តាចាំបាច់សម្រាប់ការអភិវឌ្ឍ។",
        "is_correct": True
    },
    {
        "description": "Typo: ឯករាជ្យភាព (Correct)",
        "text": "កម្ពុជាបានប្រារព្ធខួបអនុស្សាវរីយ៍នៃទិវាបុណ្យឯករាជ្យជាតិ។",
        "is_correct": True
    },
    {
        "description": "Typo: សន្តិសុខ (Correct)",
        "text": "ការរក្សាសន្តិសុខសណ្តាប់ធ្នាប់សង្គមជាកាតព្វកិច្ចរួម។",
        "is_correct": True
    },
    {
        "description": "Typo: យុត្តិធម៌ (Correct)",
        "text": "យើងចង់បានសង្គមមួយដែលមានយុត្តិធម៌ពេញលេញ។",
        "is_correct": True
    },
    {
        "description": "Final: Cambodia Kingdom (Correct)",
        "text": "ព្រះរាជាណាចក្រកម្ពុជាគឺជាទឹកដីអច្ឆរិយៈ។",
        "is_correct": True
    }
]

def run_test_suite():
    print("=" * 100)
    print(f"{'KHMER SPELL CHECKER HEAVY TEST SUITE':^100}")
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
                details = f"Detected {len(detected_errors)} false errors: " + ", ".join([f"'{e['original']}'" for e in detected_errors.values()])
        else:
            expected_word = case.get("expected_error")
            found = False
            for err_idx, err_info in detected_errors.items():
                # Flexible matching for expected error
                if expected_word == err_info['original'] or expected_word in err_info['original'] or err_info['original'] in expected_word:
                    found = True
                    # Check suggestion if provided
                    if "suggestion" in case:
                        suggestions = err_info.get('suggestions', [])
                        suggested = suggestions[0] if suggestions else "None"
                        if case["suggestion"] == suggested or case["suggestion"] in suggestions:
                            details = f"Correctly suggested: {case['suggestion']}"
                        else:
                            details = f"Wrong suggestion: {suggested} (Exp: {case['suggestion']})"
                    else:
                        details = "Detected correctly"
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
