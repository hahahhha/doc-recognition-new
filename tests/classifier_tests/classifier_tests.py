import cv2
import numpy as np
import pytesseract
import unittest
from src.classifier import DocumentType, get_document_type
from src.ocr_result import OcrResult
from pathlib import Path

def get_tesseract_ocr_result(img: np.ndarray) -> OcrResult:
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    data = pytesseract.image_to_data(
        img_rgb,
        lang='rus',
        output_type=pytesseract.Output.DICT,
        config="--oem 3 --psm 3"
    )
    ocr_result = OcrResult()
    for i in range(len(data['text'])):
        if data['conf'][i] != -1:
            # print(data['text'][i], data['level'][i])
            text = data['text'][i]
            left_x = data['left'][i]
            top_y = data['top'][i]
            bbox = [
                [left_x, top_y],
                [left_x + data['width'][i], top_y],
                [left_x + data['width'][i], top_y + data['height'][i]],
                [left_x, top_y + data['height'][i]],
            ]
            ocr_result.insert(bbox, text, data['conf'][i])

    return ocr_result


class TestClassifier(unittest.TestCase):
    def test_simple_upd_case(self):
        ocr_result = OcrResult()
        ocr_result.insert([(1, 10), (20, 20)], 'универсальный', 1)
        ocr_result.insert([(1, 10),( 20, 20)], 'передаточный', 1)
        expected = DocumentType.UPD
        actual = get_document_type(ocr_result)
        self.assertEqual(expected, actual)

    def __test_document_type_by_image_path(self, image_path: str, expected: DocumentType):
        img = cv2.imread(str(image_path))
        expected = DocumentType.UPD
        actual = get_document_type(get_tesseract_ocr_result(img))
        self.assertEqual(expected, actual)

    def test_upd_scans_recognize(self):
        names = ['upd1_page1.jpg', 'upd2_page1.jpg', 'upd4_page1.jpg']
        paths = [Path(__file__).parent.parent / 'scan_images' / name for name in names]
        for path in paths:
            self.__test_document_type_by_image_path(str(path), DocumentType.UPD)


if __name__ == '__main__':
    unittest.main()