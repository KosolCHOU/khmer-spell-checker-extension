
import unittest
from landing.spell_checker_advanced import check_spelling

class TestRule5Stress(unittest.TestCase):
    
    def run_case(self, subject, verb, expected_error=None, expected_suggestion=None):
        text = f"{subject}{verb}។"
        result = check_spelling(text)
        errors = result.get('errors', {})
        
        if expected_error:
            # We expect an error on the verb
            # The verb is likely the second token (index 1) or later depending on segmentation
            # But here we just check if ANY error matches
            
            found = False
            for idx, err in errors.items():
                if err['original'] == expected_error:
                    found = True
                    # Check suggestion if specified
                    if expected_suggestion:
                        self.assertIn(expected_suggestion, err['suggestions'], f"For '{text}': Expected suggestion '{expected_suggestion}' for '{expected_error}', got {err['suggestions']}")
                    break
            
            if not found:
                 self.fail(f"For '{text}': Expected error '{expected_error}' not detected. Errors found: {errors}")
        else:
            # We expect NO error on the verb
            for idx, err in errors.items():
                if err['original'] == verb:
                    self.fail(f"For '{text}': Unexpected error on verb '{verb}': {err}")

    def test_stress_eat(self):
        # Action: EAT
        # L1: ញ៉ាំ, L2: ពិសា, L3: ឆាន់, L4: សោយ
        
        # 1. Subject Level 1: ខ្ញុំ (I)
        self.run_case("ខ្ញុំ", "ញ៉ាំ", expected_error=None)
        self.run_case("ខ្ញុំ", "ពិសា", expected_error="ពិសា", expected_suggestion="ញ៉ាំ") # L1 using L2 -> Humble Rule violation
        self.run_case("ខ្ញុំ", "ឆាន់", expected_error="ឆាន់", expected_suggestion="ញ៉ាំ") # L1 using L3
        self.run_case("ខ្ញុំ", "សោយ", expected_error="សោយ", expected_suggestion="ញ៉ាំ") # L1 using L4 (Humble Rule)

        # 2. Subject Level 1: គាត់ (He)
        self.run_case("គាត់", "ញ៉ាំ", expected_error=None)
        self.run_case("គាត់", "ពិសា", expected_error=None)
        self.run_case("គាត់", "ឆាន់", expected_error="ឆាន់", expected_suggestion="ញ៉ាំ")
        self.run_case("គាត់", "សោយ", expected_error="សោយ", expected_suggestion="ញ៉ាំ")

        # 3. Subject Level 2: លោក (Mr/You Polite)
        self.run_case("លោក", "ញ៉ាំ", expected_error="ញ៉ាំ", expected_suggestion="ពិសា") # L2 using L1 -> Error (Underuse)
        self.run_case("លោក", "ពិសា", expected_error=None)
        self.run_case("លោក", "ឆាន់", expected_error="ឆាន់", expected_suggestion="ពិសា") # L2 using L3 -> Error (Overuse)
        self.run_case("លោក", "សោយ", expected_error="សោយ", expected_suggestion="ពិសា") # L2 using L4 -> Error

        # 4. Subject Level 3: ព្រះសង្ឃ (Monk)
        self.run_case("ព្រះសង្ឃ", "ញ៉ាំ", expected_error="ញ៉ាំ", expected_suggestion="ឆាន់") # L3 using L1 -> Error
        self.run_case("ព្រះសង្ឃ", "ពិសា", expected_error="ពិសា", expected_suggestion="ឆាន់") # L3 using L2 -> Error
        self.run_case("ព្រះសង្ឃ", "ឆាន់", expected_error=None)
        self.run_case("ព្រះសង្ឃ", "សោយ", expected_error=None) # L3 using L4 -> OK in current logic (3 > 4 False) - Monks using Royal? Debatable but checking logic consistency.

        # 5. Subject Level 4: ព្រះមហាក្សត្រ (King)
        self.run_case("ព្រះមហាក្សត្រ", "ញ៉ាំ", expected_error="ញ៉ាំ", expected_suggestion="សោយ") # L4 using L1 -> Error
        self.run_case("ព្រះមហាក្សត្រ", "ពិសា", expected_error="ពិសា", expected_suggestion="សោយ") # L4 using L2 -> Error
        self.run_case("ព្រះមហាក្សត្រ", "ឆាន់", expected_error="ឆាន់", expected_suggestion="សោយ") # L4 using L3 -> Error
        self.run_case("ព្រះមហាក្សត្រ", "សោយ", expected_error=None)

    def test_stress_sleep(self):
        # Action: SLEEP
        # L1: ដេក, L2: សម្រាក, L3: សឹង, L4: ផ្ទុំ

        # L1 Subject
        self.run_case("ខ្ញុំ", "ដេក", expected_error=None)
        self.run_case("ខ្ញុំ", "ផ្ទុំ", expected_error="ផ្ទុំ", expected_suggestion="ដេក")

        # L2 Subject
        self.run_case("លោកគ្រូ", "ដេក", expected_error="ដេក", expected_suggestion="សម្រាក")
        self.run_case("លោកគ្រូ", "សម្រាក", expected_error=None)
        self.run_case("លោកគ្រូ", "សឹង", expected_error="សឹង", expected_suggestion="សម្រាក")

        # L3 Subject
        self.run_case("ភិក្ខុ", "ដេក", expected_error="ដេក", expected_suggestion="សឹង")
        self.run_case("ភិក្ខុ", "សឹង", expected_error=None)

        # L4 Subject
        self.run_case("ស្ដេច", "ដេក", expected_error="ដេក", expected_suggestion="ផ្ទុំ")
        self.run_case("ស្ដេច", "ផ្ទុំ", expected_error=None)

    def test_stress_walk(self):
        # Action: WALK
        # L1: ដើរ, L2: អញ្ជើញ, L3: និមន្ត, L4: យាង

        self.run_case("ខ្ញុំ", "ដើរ", expected_error=None)
        self.run_case("ខ្ញុំ", "យាង", expected_error="យាង", expected_suggestion="ដើរ")

        self.run_case("លោក", "ដើរ", expected_error="ដើរ", expected_suggestion="អញ្ជើញ")
        self.run_case("លោក", "អញ្ជើញ", expected_error=None)

        self.run_case("ព្រះសង្ឃ", "ដើរ", expected_error="ដើរ", expected_suggestion="និមន្ត")
        self.run_case("ព្រះសង្ឃ", "និមន្ត", expected_error=None)

        self.run_case("ព្រះមហាក្សត្រ", "ដើរ", expected_error="ដើរ", expected_suggestion="យាង")
        self.run_case("ព្រះមហាក្សត្រ", "យាង", expected_error=None)
    
    def test_stress_die(self):
        # Action: DIE
        # L1: ស្លាប់, L2: អនិច្ចកម្ម, L3: សុគត, L4: សោយទិវង្គត

        self.run_case("ឆ្កែ", "ស្លាប់", expected_error=None)
        
        self.run_case("គាត់", "សោយទិវង្គត", expected_error="សោយទិវង្គត", expected_suggestion="ស្លាប់")

        self.run_case("លោកគ្រូ", "ស្លាប់", expected_error="ស្លាប់", expected_suggestion="អនិច្ចកម្ម")
        self.run_case("លោកគ្រូ", "អនិច្ចកម្ម", expected_error=None)

        self.run_case("ព្រះសង្ឃ", "ស្លាប់", expected_error="ស្លាប់", expected_suggestion="សុគត")
        self.run_case("ព្រះសង្ឃ", "សុគត", expected_error=None)

        self.run_case("ព្រះមហាក្សត្រ", "ស្លាប់", expected_error="ស្លាប់", expected_suggestion="សោយទិវង្គត")
        self.run_case("ព្រះមហាក្សត្រ", "សោយទិវង្គត", expected_error=None)

    def test_stress_speak(self):
        # Action: SPEAK
        # L1: និយាយ, L2: ប្រសាសន៍, L3: សង្ឃដីកា, L4: ព្រះបន្ទូល

        self.run_case("ខ្ញុំ", "និយាយ", expected_error=None)
        self.run_case("ខ្ញុំ", "ព្រះបន្ទូល", expected_error="ព្រះបន្ទូល", expected_suggestion="និយាយ")

        self.run_case("លោក", "និយាយ", expected_error="និយាយ", expected_suggestion="ប្រសាសន៍")
        self.run_case("លោក", "ប្រសាសន៍", expected_error=None)

        self.run_case("ព្រះសង្ឃ", "និយាយ", expected_error="និយាយ", expected_suggestion="សង្ឃដីកា")
        self.run_case("ព្រះសង្ឃ", "សង្ឃដីកា", expected_error=None)

        self.run_case("ព្រះមហាក្សត្រ", "និយាយ", expected_error="និយាយ", expected_suggestion="ព្រះបន្ទូល")
        self.run_case("ព្រះមហាក្សត្រ", "ព្រះបន្ទូល", expected_error=None)

    def test_stress_born(self):
        # Action: BORN
        # L1: កើត, L4: ប្រសូត

        self.run_case("ក្មេង", "កើត", expected_error=None)
        
        # Checking L4 Subject
        self.run_case("ព្រះរាជបុត្រ", "កើត", expected_error="កើត", expected_suggestion="ប្រសូត")
        self.run_case("ព្រះរាជបុត្រ", "ប្រសូត", expected_error=None)

    def test_stress_drink(self):
        # Action: DRINK
        # L1: ផឹក, L2: ពិសា, L3: ឆាន់, L4: សេព

        self.run_case("ខ្ញុំ", "ផឹក", expected_error=None)
        self.run_case("ខ្ញុំ", "សេព", expected_error="សេព", expected_suggestion="ផឹក")

        self.run_case("លោក", "ផឹក", expected_error="ផឹក", expected_suggestion="ពិសា")
        
        self.run_case("ព្រះសង្ឃ", "ផឹក", expected_error="ផឹក", expected_suggestion="ឆាន់")
        self.run_case("ព្រះសង្ឃ", "ឆាន់", expected_error=None)

        self.run_case("ស្តេច", "ផឹក", expected_error="ផឹក", expected_suggestion="សេព")

    def test_stress_bathe(self):
        # Action: BATHE
        # L1: ងូតទឹក, L2: ជម្រះកាយ, L3: ស្រង់, L4: សេពសោយ

        self.run_case("ក្មេង", "ងូតទឹក", expected_error=None)
        
        self.run_case("លោក", "ងូតទឹក", expected_error="ងូតទឹក", expected_suggestion="ជម្រះកាយ")
        
        self.run_case("ព្រះសង្ឃ", "ងូតទឹក", expected_error="ងូតទឹក", expected_suggestion="ស្រង់")
        self.run_case("ព្រះសង្ឃ", "ស្រង់", expected_error=None)

        self.run_case("ព្រះមហាក្សត្រ", "ងូតទឹក", expected_error="ងូតទឹក", expected_suggestion="សេពសោយ")

    def test_stress_see(self):
        # Action: SEE
        # L1: មើល, L2: ទស្សនា, L4: ទត

        self.run_case("ខ្ញុំ", "មើល", expected_error=None)
        
        self.run_case("ភ្ញៀវ", "មើល", expected_error="មើល", expected_suggestion="ទស្សនា")
        self.run_case("ភ្ញៀវ", "ទស្សនា", expected_error=None)

        self.run_case("ព្រះមហាក្សត្រ", "មើល", expected_error="មើល", expected_suggestion="ទត")
        self.run_case("ព្រះមហាក្សត្រ", "ទត", expected_error=None)

    def test_stress_give(self):
        # Action: GIVE
        # L1: ឱ្យ, L2: ជូន, L3: ប្រគេន, L4: ថ្វាយ

        self.run_case("ខ្ញុំ", "ឱ្យ", expected_error=None)
        
        # Note: 'give' is tricky because it depends on recipient, but Rule 5 might strictly check subject level vs verb level
        # Assuming Rule 5 checks Subject -> Verb consistency
        
        self.run_case("លោក", "ឱ្យ", expected_error="ឱ្យ", expected_suggestion="ជូន")
        self.run_case("លោក", "ជូន", expected_error=None) # Giving to someone respected

    def test_stress_return(self):
        # Action: RETURN
        # L1: ត្រឡប់, L3: និមន្តត្រឡប់, L4: យាងត្រឡប់

        self.run_case("ខ្ញុំ", "ត្រឡប់", expected_error=None)
        
        self.run_case("ព្រះសង្ឃ", "ត្រឡប់", expected_error="ត្រឡប់", expected_suggestion="និមន្តត្រឡប់")
        
        self.run_case("ព្រះមហាក្សត្រ", "ត្រឡប់", expected_error="ត្រឡប់", expected_suggestion="យាងត្រឡប់")

if __name__ == '__main__':
    unittest.main()
