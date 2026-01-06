from src.upd.scan.parse_scan import parse_scan_dict as upd_parse_scan_dict
from src.upd.scan.parse_scan import parse_scan_dict_with_ocr_result as upd_parse_scan_dict_with_ocr_result
from src.ocr_result import OcrResult


def prettify_result(result: dict) -> dict:
    result_copy = result.copy()
    result_copy['shipper'] = result['consignor']
    del result_copy['consignor']
    result_copy['document_info'] = {
        "document_type": "Счет-фактура"
    }
    return result_copy


def parse_scan_dict(img_path: str, tesseract_path: str) -> dict:
    result = upd_parse_scan_dict(img_path, tesseract_path)
    return prettify_result(result)


def parse_scan_dict_with_ocr_result(img_path: str, ocr_result: OcrResult) -> dict:
    return prettify_result(upd_parse_scan_dict_with_ocr_result(img_path, ocr_result))