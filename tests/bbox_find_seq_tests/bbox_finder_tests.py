import unittest

from src.ocr_result import OcrResult
from project_scripts.bbox_finder import BboxFinder

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
            [[375, 475], [487, 475], [487, 493], [375, 493]], # товарная
            [[491, 475], [614, 475], [614, 493], [491, 493]] # накладная
        ]
        actual, flag = bbox_finder.find_sentence_bbox_sequences(
            [['товарная'], ['накладная']]
        )
        self.assertListEqual(expected, actual)

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
        actual, flag = bbox_finder.find_sentence_bbox_sequences(
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


if __name__ == '__main__':
    unittest.main()