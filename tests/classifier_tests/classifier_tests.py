import cv2
import unittest
from src.classifier import DocumentType, get_document_type
from src.ocr_result import OcrResult
from pathlib import Path

from src.project_scripts.tesseract_ocr_result import get_tesseract_ocr_result


class TestClassifierByOcrResult(unittest.TestCase):
    def __test_type_by_simple_keywords(self, keywords: list[str], expected: DocumentType):
        ocr_result = OcrResult()
        for word in keywords:
            # координаты не играют роли при распознавании типа документа
            ocr_result.insert(bbox=[(-1, -1), (-1, -1)], text=word, confidence=1)
        actual = get_document_type(ocr_result)
        self.assertEqual(expected, actual,
                         msg = f'In test_by_simple_keywords expected {expected}, got {actual}')


    def test_simple_upd_case(self):
        self.__test_type_by_simple_keywords(
            keywords=['универсальный', 'передаточный'],
            expected=DocumentType.UPD
        )

    def test_simple_invoice_case(self):
        self.__test_type_by_simple_keywords(
            keywords=['счёт', 'фактура'],
            expected=DocumentType.INVOICE
        )

    def test_simple_waybill_case(self):
        self.__test_type_by_simple_keywords(
            keywords=['товарная', 'накладная'],
            expected=DocumentType.WAYBILL
        )

    def __test_document_type_by_image_path(self, image_path: str, expected: DocumentType):
        img = cv2.imread(str(image_path))
        actual = get_document_type(get_tesseract_ocr_result(img))
        self.assertEqual(expected, actual)

    def test_upd_scans_type_recognize(self):
        names = ['upd1_page1.jpg', 'upd2_page1.jpg', 'upd4_page1.jpg']
        paths = [Path(__file__).parent.parent / 'scan_images' / name for name in names]
        for path in paths:
            self.__test_document_type_by_image_path(str(path), DocumentType.UPD)

    def test_invoice_scans_type_recognize(self):
        names = ['schet_factura1.jpg', 'schet_factura2.jpg', 'schet_factura4.jpg']
        paths = [Path(__file__).parent.parent / 'scan_images' / name for name in names]
        for path in paths:
            self.__test_document_type_by_image_path(str(path), DocumentType.INVOICE)

    def test_waybill_scans_type_recognize(self):
        names = ['torg1.jpg']
        paths = [Path(__file__).parent.parent / 'scan_images' / name for name in names]
        for path in paths:
            self.__test_document_type_by_image_path(str(path), DocumentType.WAYBILL)

    def test_invoice_zipped(self):
        name = 'schet-zip.jpg'
        path = Path(__file__).parent.parent / 'scan_images' / name
        self.__test_document_type_by_image_path(path, DocumentType.INVOICE)

if __name__ == '__main__':
    unittest.main()