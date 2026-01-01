from src.upd.scan.parse_scan import parse_scan_dict as upd_parse_scan_dict
from src.upd.scan.parse_scan import parse_scan_dict_with_ocr_result as upd_parse_scan_dict_with_ocr_result
from src.ocr_result import OcrResult


def parse_scan_dict(img_path: str, tesseract_path: str) -> dict:
    result = upd_parse_scan_dict(img_path, tesseract_path)
    return result


def parse_scan_dict_with_ocr_result(img_path: str, ocr_result: OcrResult) -> dict:
    return upd_parse_scan_dict_with_ocr_result(img_path, ocr_result)