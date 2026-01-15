import unittest

from src.ocr_result import OcrResult
from src.project_scripts import BboxFinder

class TestBboxFinder(unittest.TestCase):
    def test_simple_bbox_sequences_finding(self):
        # поиск "Товарная накладная"
        ocr_result = OcrResult()
        ocr_result.insert([
            [375, 475], [487, 475], [487, 493], [375, 493]
        ], 'товарная', 1)
        ocr_result.insert([
            [491, 475], [614, 475], [614, 493], [491, 493]
        ], 'нАкладная', 1)
        ocr_result.insert([
            [634, 452], [682, 452], [682, 466], [634, 466]
        ], 'номер', 1)
        bbox_finder = BboxFinder(ocr_result, 5, [])
        expected = [
            [
                [[375, 475], [487, 475], [487, 493], [375, 493]], # товарная
                [[491, 475], [614, 475], [614, 493], [491, 493]] # накладная
            ]
        ]
        actual, flag = bbox_finder.find_sentence_bbox_sequences_with_success(
            [['товарная'], ['накладная']]
        )
        self.assertEqual(sorted(expected), sorted(actual))

    def test_two_sentences_exists(self):
        ocr_result = OcrResult()
        ocr_result.insert(
            [[259, 753], [327, 753], [327, 768], [259, 768]],
         'Товарная',1)
        ocr_result.insert(
            [[333, 756], [409, 756], [409, 767], [333, 767]],
            'накладная', 1
        )
        ocr_result.insert(
            [[379, 479], [485, 479], [485, 493], [379, 493]],
            'ТОВАРНАЯ',
            1
        )
        ocr_result.insert(
            [[493, 479], [613, 479], [613, 496], [493, 496]],
            'НАКЛАДНАЯ',
            1
        )
        bbox_finder = BboxFinder(ocr_result, 10, [])
        actual, flag = bbox_finder.find_sentence_bbox_sequences_with_success(
            [['товарная'], ['накладная']]
        )
        expected = [
            [
                [[259, 753], [327, 753], [327, 768], [259, 768]],
                [[333, 756], [409, 756], [409, 767], [333, 767]]
            ],
            [
                [[379, 479], [485, 479], [485, 493], [379, 493]],
                [[493, 479], [613, 479], [613, 496], [493, 496]]
            ]
        ]
        self.assertEqual(len(expected), len(actual), 'длины не совпали')
        self.assertEqual(sorted(expected), sorted(actual))

    def test_single_bbox_finding(self):
        bbox1 = [
            [0, 0],
            [100, 0],
            [100, 100],
            [0, 100]
        ]
        bbox2 = [
            [10, 10],
            [20, 10],
            [20, 20],
            [10, 20]
        ]
        actual = BboxFinder.get_single_bbox([bbox1, bbox2])
        expected = [
            [0, 0],
            [100, 0],
            [100, 100],
            [0, 100]
        ]
        self.assertEqual(expected, actual)

    def test_two_first_words_and_one_second_case(self):
        ocr_result = OcrResult()
        ocr_result.insert(
            [[259, 753], [327, 753], [327, 768], [259, 768]],
            'Товарная', 1)
        ocr_result.insert(
            [[333, 756], [409, 756], [409, 767], [333, 767]],
            'накладная', 1
        )
        ocr_result.insert(
            [[379, 479], [485, 479], [485, 493], [379, 493]],
            'ТОВАРНАЯ',
            1
        )
        expected = [
            [
                [[259, 753], [327, 753], [327, 768], [259, 768]],
                [[333, 756], [409, 756], [409, 767], [333, 767]]
            ]
        ]
        bbox_finder = BboxFinder(ocr_result, 10, [])
        actual, flag = bbox_finder.find_sentence_bbox_sequences_with_success(
            [['товарная'], ['накладная']]
        )
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()