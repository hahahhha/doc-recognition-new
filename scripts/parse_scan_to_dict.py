import cv2

from src.classifier import classifier
from src.classifier.document_types import DocumentType

from src.upd.scan.parse_scan import (parse_scan_dict_with_ocr_result
                                     as upd_parse_scan_dict_with_ocr_result)
from src.invoice.scan.parse_scan import (parse_scan_dict_with_ocr_result
                                         as invoice_parse_scan_dict_with_ocr_result)
from src.waybill.scan.parse_scan import (parse_scan_dict_with_ocr_result
                                         as waybill_parse_scan_dict_with_ocr_result)

from scripts.tesseract_ocr_result import get_tesseract_ocr_result

def parse_scan_to_dict(img_path: str, tesseract_path: str = '') -> dict:
    img = cv2.imread(img_path)
    ocr_result = get_tesseract_ocr_result(img)
    document_type = classifier.get_document_type(ocr_result)

    if document_type == DocumentType.UPD:
        result = upd_parse_scan_dict_with_ocr_result(img_path, ocr_result)
        result['document_type'] = (DocumentType.UPD, 'Универсальный передаточный документ')
        return result
    elif document_type == DocumentType.WAYBILL:
        result = waybill_parse_scan_dict_with_ocr_result(img_path, ocr_result)
        result['document_type'] = (DocumentType.WAYBILL, 'Товарная накладная')
        return result
    elif document_type == DocumentType.INVOICE:
        result = invoice_parse_scan_dict_with_ocr_result(img_path, ocr_result)
        result['document_type'] = (DocumentType.INVOICE, 'Счёт-фактура')
        return result
    elif document_type == DocumentType.UNRECOGNIZED:
        return {
            'document_type': (DocumentType.UNRECOGNIZED, 'Не удалось распознать документ')
        }