from unittest import TestCase
from src.macro_script import MacroController

class TestMacroController(TestCase):
    def test_load_and_process_platform_map(self):
        g = MacroController(rune_model_dir="non-unittests/arrow_classifier_keras_gray.h5")
        retval = g.load_and_process_platform_map(r"unittest_data/test_valid_data.platform")
        self.assertNotEqual(retval, 0)

