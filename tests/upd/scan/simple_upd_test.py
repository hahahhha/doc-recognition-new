import easyocr
import cv2
import numpy as np
from src.upd.scan.ocr_result import OcrResult
from src.upd.scan.parse_header import parse_header_to_dict
from src.upd.scan.parse_table import parse_table

def simple_upd_test(ocr_res):
    for k, v in parse_header_to_dict(ocr_res).items():
        print(f'{k}: {v}')



if __name__ == '__main__':
    print('started')
    img = cv2.imread('./../../scan_images/upd1_page1.jpg', cv2.IMREAD_GRAYSCALE)
    reader = easyocr.Reader(['ru'])
    ocr = reader.readtext(img)
    ocr_result = OcrResult()
    for bbox, text, confidence in ocr:
        ocr_result.insert(bbox, text, confidence)
        # print(text)
    print('ocr created\n')
    parse_table(img, ocr_result)
