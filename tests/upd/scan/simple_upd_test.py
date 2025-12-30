import cv2
import easyocr
import pytesseract
import time
import json
import os

from src.upd.scan.ocr_result import OcrResult
from src.upd.scan.parse_header import parse_header_to_dict


def parse_and_print_res(ocr_res):
    result = parse_header_to_dict(ocr_res)
    for k, v in result.items():
        print(f'{k}: {v}')
    print(f'\n\ntotal length: {len(result)}')


def get_easyocr_result(image_path: str) -> OcrResult:
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    reader = easyocr.Reader(['ru', 'en'])
    res = reader.readtext(img)
    ocr_result = OcrResult()
    for bbox, text, conf in res:
        ocr_result.insert(bbox, text, conf)
    return ocr_result


def get_tesseract_result(image_path):
    try:
        os.access(image_path, os.R_OK)
        print('доступ есть')
    except Exception as e:
        print('Нет доступа к файлу', e)
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Не удалось открыть изображение: {image_path}")

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


def test_tesseract_and_easyocr():
    img_path = './../../scan_images/upd1_page1.jpg'
    print('started')
    start_time = time.time()
    ocr_result = get_tesseract_result(img_path)
    # ocr_result = get_easyocr_result(img_path)
    end_time = time.time()
    parse_and_print_res(ocr_result)
    print('\n\n=======OCR RESULT=======')
    ocr_result.print()
    print('\n\n=======TAKEN TIME=======')
    print(end_time - start_time)


def test_parse_header(img_path: str) -> None:
    print('started')
    start_time = time.time()

    ocr_result = get_tesseract_result(img_path)
    result = parse_header_to_dict(ocr_result)
    print(json.dumps(result, indent=4, ensure_ascii=False))
    end_time = time.time()
    print('\n\n=======TAKEN TIME=======')
    print(end_time - start_time)

    print('\n\n=======OCR RESULT=======')
    # ocr_result.print(coordinates=True)
    # нашлись только инн\кпп продавца и покупателя

if __name__ == '__main__':
    test_parse_header(r'C:\Users\User\Desktop\prj_test_img\upd1_page1_problem.jpg')