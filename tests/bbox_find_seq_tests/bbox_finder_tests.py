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
        actual = bbox_finder.find_sentence_bbox_sequences(
            [['товарная'], ['накладная']]
        )[0][0]
        self.assertListEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()