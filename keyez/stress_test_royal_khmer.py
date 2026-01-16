#!/usr/bin/env python3
"""
Stress Test Suite for Royal Khmer (Raja Sap) Logic
Tests the system's ability to handle royal vocabulary and register mismatches.
"""

import sys
import unittest
sys.path.insert(0, '/home/kosol/AstroAI/keyez/landing')

from spell_checker_advanced import check_spelling

class TestRoyalKhmer(unittest.TestCase):
    
    def run_check(self, text, description):
        """Helper to run check and print results"""
        print(f"\nTest: {text}")
        print(f"Desc: {description}")
        result = check_spelling(text)
        errors = result.get('errors', {})
        if errors:
            print(f"  ⚠ Errors: {len(errors)}")
            for idx, err in errors.items():
                print(f"    - '{err['original']}' -> {err.get('suggestions')} ({err.get('error_type')})")
        else:
            print("  ✓ No errors")
        return errors

    def test_correct_royal_usage(self):
        """Test correct usage of royal subjects with royal verbs"""
        print("\n=== Testing Correct Royal Usage ===")
        test_cases = [
            "ព្រះមហាក្សត្រសោយព្រះស្ងោយ",  # King eats food
            "សម្តេចយាងទៅព្រះវិហារ",        # Samdech goes to temple
            "ព្រះករុណាទ្រង់ព្រះសណ្តាប់",   # King listens
            "ព្រះបាទជ័យវរ្ម័នទ្រង់យាង",     # King Jayavarman goes
            "ព្រះសង្ឃឆាន់ចង្ហាន់",          # Monk eats food
        ]
        for text in test_cases:
            errors = self.run_check(text, "Correct Royal Usage")
            # We expect NO register mismatch errors
            register_errors = [e for e in errors.values() if e.get('error_type') == 'register_mismatch']
            self.assertEqual(len(register_errors), 0, f"False positive register error for: {text}")

    def test_correct_common_usage(self):
        """Test correct usage of common subjects with common verbs"""
        print("\n=== Testing Correct Common Usage ===")
        test_cases = [
            "ខ្ញុំញ៉ាំបាយ",          # I eat rice
            "គាត់ដើរទៅផ្សារ",       # He walks to market
            "យើងទៅសាលារៀន",       # We go to school
            "គេហូបបាយ",            # They eat rice
        ]
        for text in test_cases:
            errors = self.run_check(text, "Correct Common Usage")
            register_errors = [e for e in errors.values() if e.get('error_type') == 'register_mismatch']
            self.assertEqual(len(register_errors), 0, f"False positive register error for: {text}")

    def test_register_mismatch_royal_subject_common_verb(self):
        """Test Royal Subject + Common Verb (Should be flagged)"""
        print("\n=== Testing Mismatch: Royal Subject + Common Verb ===")
        
        # Expected suggestions based on SEMANTIC_REGISTER_MAP
        test_cases = [
            ("ព្រះមហាក្សត្រញ៉ាំបាយ", ["សោយ", "ពិសា", "ទទួលទាន", "ឆាន់"]),
            ("សម្តេចដើរលេង", ["យាង", "យាងទៅ", "ស្តេចយាង", "យាងកម្សាន្ត"]),
            ("ព្រះករុណាទៅផ្សារ", ["យាង", "យាងទៅ", "ស្តេចយាង"]),
            ("ព្រះបាទហូបបាយ", ["សោយ", "ពិសា", "ទទួលទាន", "ឆាន់"]), 
        ]
        
        detected_count = 0
        for text, expected_suggestions in test_cases:
            errors = self.run_check(text, "Royal Subject + Common Verb")
            
            # Check if ANY error suggests one of the expected royal words
            found_correct_suggestion = False
            for err in errors.values():
                for sugg in err.get('suggestions', []):
                    if sugg in expected_suggestions:
                        found_correct_suggestion = True
                        break
                if found_correct_suggestion:
                    break
            
            if found_correct_suggestion:
                detected_count += 1
                print("    -> Correct suggestion found!")
            else:
                print("    -> correct suggestion NOT found.")

        # Assert that ALL mismatches are detected now
        self.assertEqual(detected_count, len(test_cases), "Failed to detect some royal/common mismatches")

    def test_register_mismatch_common_subject_royal_verb(self):
        """Test Common Subject + Royal Verb (Should be flagged)"""
        print("\n=== Testing Mismatch: Common Subject + Royal Verb ===")
        
        test_cases = [
            ("ខ្ញុំសោយព្រះស្ងោយ", ["ញ៉ាំ", "ហូប", "ស៊ី", "បរិភោគ"]),
            ("គាត់យាងទៅផ្ទះ", ["ទៅ", "ដើរ", "ធ្វើដំណើរ"]),
            ("យើងទ្រង់យាង", ["ទៅ", "ដើរ", "ធ្វើដំណើរ"]),
        ]
        
        detected_count = 0
        for text, expected_suggestions in test_cases:
            errors = self.run_check(text, "Common Subject + Royal Verb")
            
            found_correct_suggestion = False
            for err in errors.values():
                for sugg in err.get('suggestions', []):
                    if sugg in expected_suggestions:
                        found_correct_suggestion = True
                        break
                if found_correct_suggestion:
                    break
            
            if found_correct_suggestion:
                detected_count += 1
                print("    -> Correct suggestion found!")
            else:
                print("    -> correct suggestion NOT found.")
        
        self.assertEqual(detected_count, len(test_cases), "Failed to detect some common/royal mismatches")

    def test_royal_vocabulary_whitelist(self):
        """Verify royal vocabulary is valid and not flagged as spelling errors"""
        print("\n=== Testing Royal Vocabulary Validity ===")
        royal_words = [
            "ព្រះបរមរាជវាំង", "ព្រះរាជពិធី", "ព្រះរាជក្រឹត្យ", "ព្រះរាជទាន",
            "ព្រះសង្ឃរាជ", "ព្រះករុណា", "ព្រះបាទ", "សម្តេច", "នរោត្តម", "សីហមុនី",
            "សោយទិវង្គត", "ប្រសូត", "យាង", "និមន្ត", "ថ្វាយ"
        ]
        
        misspelled_count = 0
        for word in royal_words:
            # Check single word
            result = check_spelling(word)
            errors = result.get('errors', {})
            
            # Filter for spelling errors specifically
            spelling_errors = [e for e in errors.values() if e.get('error_type') == 'spelling']
            
            if spelling_errors:
                print(f"  X '{word}' flagged as spelling error")
                misspelled_count += 1
            else:
                # print(f"  ✓ '{word}' is valid")
                pass
                
        if misspelled_count == 0:
            print("  ✓ All tested royal vocabulary recognized correctly.")
        else:
            print(f"  ⚠ {misspelled_count} royal words flagged as errors.")
        
        self.assertEqual(misspelled_count, 0, "Some royal vocabulary words are missing from whitelist")

if __name__ == '__main__':
    unittest.main()
