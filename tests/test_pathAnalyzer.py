from unittest import TestCase
from src.terrain_analyzer import PathAnalyzer
import random
TEST_VALID_PLATFORM__DIR = r"unittest_data/test_valid_data.platform"
TEST_CORRUPT_PLATFORM_DIR = r"unittest_data/test_corrupt_data.platform"

class TestPathAnalyzer(TestCase):
    def test_load(self):
        with self.subTest():
            analyzer = PathAnalyzer()
            retval = analyzer.load(TEST_VALID_PLATFORM__DIR)
            self.assertEqual(len(retval), 4)
        with self.subTest():
            analyzer = PathAnalyzer()
            retval = analyzer.load(TEST_CORRUPT_PLATFORM_DIR)
            self.assertEqual(retval, 0)

    def test_verify_data_file(self):
        with self.subTest():
            analyzer = PathAnalyzer()
            retval = analyzer.verify_data_file(TEST_VALID_PLATFORM__DIR)
            self.assertEqual(len(retval), 4)
        with self.subTest():
            analyzer = PathAnalyzer()
            retval = analyzer.verify_data_file(TEST_CORRUPT_PLATFORM_DIR)
            self.assertEqual(retval, 0)

    def test_hash(self):
        test_string = "testdata123"
        analyzer = PathAnalyzer()
        retval = analyzer.hash(test_string)
        self.assertEqual(len(retval), 8)

    def test_pathfind(self):
        analyzer = PathAnalyzer()
        analyzer.load(TEST_VALID_PLATFORM__DIR)
        analyzer.generate_solution_dict()
        error = False
        for hash1 in analyzer.platforms.keys():
            for hash2 in analyzer.platforms.keys():
                if hash1 == hash2:
                    continue
                rval = analyzer.pathfind(hash1, hash2)
                if not rval:
                    error = True

        self.assertFalse(error)

    def test_generate_solution_dict(self):
        analyzer = PathAnalyzer()
        analyzer.load(TEST_VALID_PLATFORM__DIR)
        error = False
        for hash1 in analyzer.platforms.keys():
            if analyzer.platforms[hash1].solutions == []:
                error = True
        self.assertFalse(error)

    def test_move_platform(self):
        analyzer = PathAnalyzer()
        analyzer.load(TEST_VALID_PLATFORM__DIR)
        error = False
        for hash1 in analyzer.platforms.keys():
            for hash2 in analyzer.platforms.keys():
                if hash1 == hash2:
                    continue
                analyzer.move_platform(hash1, hash2)
                if analyzer.platforms[hash2].last_visit != 0:
                    error = True

        self.assertFalse(error)

    def test_select_move(self):
        analyzer = PathAnalyzer()
        analyzer.load(TEST_VALID_PLATFORM__DIR)
        error = False
        for key in list(analyzer.platforms.keys()) + list(analyzer.oneway_platforms.keys()):
            if not analyzer.select_move(key):
                error = True

        self.assertFalse(error)