from src.ocr_result import OcrResult
from .parse_header import parse_header_to_dict

# товарная накладная

def parse_scan_dict(img_path: str, tesseract_path) -> dict:
    return {}


def parse_scan_dict_with_ocr_result(img_path: str, ocr_result: OcrResult) -> dict:
    return parse_header_to_dict(ocr_result)