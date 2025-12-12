import re
import cv2
import numpy as np
from img2table.document import Image

from src.upd.scan.ocr_result import OcrResult


# величина отступа от границы шапки документа и таблицы
border_extend_value = 5


def find_table_top_border(ocr_result: OcrResult):
    """Поиск верхней границы таблицы по слову Валюта (ниже него начинается таблица)"""
    currency_bboxes = [bbox for bbox, text, c in ocr_result if re.search('валюта', text, re.IGNORECASE)]
    if not currency_bboxes:
        raise Exception("Не удалось найти ключевое слово Валюта для парсинга таблицы")
    currency_bbox = currency_bboxes[0]
    border_y = currency_bbox[2][1] # получил Y правого нижнего угла
    return border_y + border_extend_value


def parse_table(img: np.ndarray, ocr_result: OcrResult):
    border_y = find_table_top_border(ocr_result)
    h, w = img.shape[:2]
    cropped_img = img[border_y: h, 0 : w]
    table_img = Image(src=img,)
    # продолжать тут, чтобы можно было передать обрезанное изображение в либу