import re
import cv2
import numpy as np
from img2table import document
from PIL import Image
from io import BytesIO

from .ocr_result import OcrResult


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



def get_cells_list(ocr_result: OcrResult, table, img_delta_y: int) -> list:
    text_by_cell = dict()
    # идем по всем ячейкам, получаем текст внутри них путем перебора для всех ячеек распознанных результатов
    for row_ind, row in table.content.items():
        for cell in row:
            cell_x1 = cell.bbox.x1
            cell_y1 = cell.bbox.y1 + img_delta_y
            cell_x2 = cell.bbox.x2
            cell_y2 = cell.bbox.y2 + img_delta_y
            for bbox, text, c in ocr_result:
                cur_mn_x, cur_mn_y = bbox[0]
                cur_mx_x, cur_mx_y = bbox[2]
                # проверка, что cell.bbox внутри текущего bbox'а
                if cell_x1 <= cur_mn_x and cell_y1 <= cur_mn_y \
                        and cell_x2 >= cur_mx_x and cell_y2 >= cur_mx_y:
                    if cell not in text_by_cell:
                        text_by_cell[cell] = []
                    if text not in text_by_cell[cell]:
                        text_by_cell[cell].append(text)
    result_table = []
    for key in text_by_cell:
        coords = [[key.bbox.x1, key.bbox.y1], [key.bbox.x2, key.bbox.y2]]
        text = ' '.join(text_by_cell[key])
        result_table.append({
            "coordinates": coords,
            "text": text
        })

    return result_table


def parse_table_to_dict(img: np.ndarray, ocr_result: OcrResult):
    border_y = find_table_top_border(ocr_result)
    h, w = img.shape[:2]
    cropped_img = img[border_y: h, 0 : w]
    pil_table_img = Image.fromarray(cropped_img)

    buf = BytesIO()
    pil_table_img.save(buf, format="PNG")
    buf.seek(0)

    doc = document.Image(buf)
    extracted_tables = doc.extract_tables(ocr=None)
    if not extracted_tables:
        raise Exception("Не удалось распознать таблицу в скане документа")
    table = extracted_tables[0]
    cells = get_cells_list(ocr_result, table, border_y)
    return cells