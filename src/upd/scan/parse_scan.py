import os
import easyocr
import numpy as np
from ..scan.parse_header import parse_header_to_dict
from ..scan.parse_table import parse_table_to_dict
from ..scan.ocr_result import OcrResult


def parse_scan_dict(img: np.ndarray) -> dict:
    model_dir = os.path.join(os.path.expanduser('~'), '.EasyOCR')

    # Создайте директорию если нет
    os.makedirs(model_dir, exist_ok=True)
    reader = easyocr.Reader(['ru'], download_enabled=True, model_storage_directory=model_dir)
    ocr = reader.readtext(img)
    ocr_result = OcrResult()
    for bbox, text, confidence in ocr:
        ocr_result.insert(bbox, text, confidence)

    result = parse_header_to_dict(ocr_result)
    result["table"] = parse_table_to_dict(img, ocr_result)
    return result