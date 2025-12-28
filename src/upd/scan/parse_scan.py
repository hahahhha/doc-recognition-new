import cv2
import pytesseract
import numpy as np
from .parse_header import parse_header_to_dict
from .parse_table import parse_table_to_dict
from .ocr_result import OcrResult


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


def parse_scan_dict(img: np.ndarray) -> dict:
    ocr_result = get_tesseract_ocr_result(img)
    result = parse_header_to_dict(ocr_result)
    result["table"] = parse_table_to_dict(img, ocr_result)
    return result


