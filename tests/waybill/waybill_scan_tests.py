import json
import cv2
from src.waybill.scan.parse_scan import parse_scan_dict_with_ocr_result as waybill_parse_scan_dict

from project_scripts.tesseract_ocr_result import get_tesseract_ocr_result

def simple_run(img_path: str):
    img = cv2.imread(img_path)
    ocr_result = get_tesseract_ocr_result(img)
    result = waybill_parse_scan_dict(img_path, ocr_result)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    simple_run(r'D:\doc-recognition-new\tests\scan_images\torg1.jpg')