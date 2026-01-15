import cv2
import pytesseract

from .parse_header import parse_header_to_dict
from .parse_table import parse_table_to_cells_list
from src.ocr_result import OcrResult
from src.project_scripts.tesseract_ocr_result import get_tesseract_ocr_result


def parse_scan_dict(img_path: str, tesseract_path) -> dict:
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    ocr_result = get_tesseract_ocr_result(img)
    result = parse_header_to_dict(ocr_result)
    result["table"] = parse_table_to_cells_list(img_path, ocr_result)
    return result


def parse_scan_dict_with_ocr_result(img_path: str, ocr_result: OcrResult) -> dict:
    result = parse_header_to_dict(ocr_result)
    result = parse_header_to_dict(ocr_result)
    result["table"] = parse_table_to_cells_list(img_path, ocr_result)
    return result