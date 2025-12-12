import easyocr
import numpy as np
from src.upd.scan.parse_header import parse_header_to_dict
from src.upd.scan.parse_table import parse_table_to_dict
from src.upd.scan.ocr_result import OcrResult


def parse_scan_dict(img: np.ndarray) -> dict:
    reader = easyocr.Reader(['ru'])
    ocr = reader.readtext(img)
    ocr_result = OcrResult()
    for bbox, text, confidence in ocr:
        ocr_result.insert(bbox, text, confidence)

    result = parse_header_to_dict(ocr_result)
    result["table"] = parse_table_to_dict(img, ocr_result)
    return result