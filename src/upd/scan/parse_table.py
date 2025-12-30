import re
import cv2
import numpy as np
from img2table.ocr import TesseractOCR
from img2table.document import Image
from PIL import Image as PILImage
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



# def get_cells_list(ocr_result: OcrResult, table, img_delta_y: int) -> list:
#     text_by_cell = dict()
#     # идем по всем ячейкам, получаем текст внутри них путем перебора для всех ячеек распознанных результатов
#     for row_ind, row in table.content.items():
#         for cell in row:
#             cell_x1 = cell.bbox.x1
#             cell_y1 = cell.bbox.y1 + img_delta_y
#             cell_x2 = cell.bbox.x2
#             cell_y2 = cell.bbox.y2 + img_delta_y
#             for bbox, text, c in ocr_result:
#                 cur_mn_x, cur_mn_y = bbox[0]
#                 cur_mx_x, cur_mx_y = bbox[2]
#                 # проверка, что cell.bbox внутри текущего bbox'а
#                 if cell_x1 <= cur_mn_x and cell_y1 <= cur_mn_y \
#                         and cell_x2 >= cur_mx_x and cell_y2 >= cur_mx_y:
#                     if cell not in text_by_cell:
#                         text_by_cell[cell] = []
#                     if text not in text_by_cell[cell]:
#                         text_by_cell[cell].append(text)
#     result_table = []
#     for key in text_by_cell:
#         coords = [[key.bbox.x1, key.bbox.y1], [key.bbox.x2, key.bbox.y2]]
#         text = ' '.join(text_by_cell[key])
#         result_table.append({
#             "coordinates": coords,
#             "text": text
#         })
#
#     return result_table


def draw_table(cells: list[dict]):
    """Для проверки распознанной таблицы"""
    canvas = np.zeros((1920, 1080, 3), dtype=np.uint8)
    for cell in cells:
        p1, p2 = cell['coordinates']
        x1, y1 = p1
        x2, y2 = p2
        canvas = cv2.rectangle(canvas, (x1, y1), (x2, y2), (255, 0, 0), 2)
    cv2.imwrite('table.png', canvas)
    print(len(cells))


def parse_table_to_cells_list(img_path: str, ocr_result: OcrResult) -> list[dict]:
    border_y = find_table_top_border(ocr_result)

    ocr = TesseractOCR(n_threads=1, lang="rus")
    doc = Image(img_path)
    extracted_tables = doc.extract_tables(ocr=ocr,
                                          implicit_rows=False,
                                          implicit_columns=False,
                                          borderless_tables=False,
                                          min_confidence=50)
    if not extracted_tables:
        raise Exception("Не удалось распознать таблицу в документе")
    found_table = extracted_tables[0]
    cells_list = []
    for id_row, row in enumerate(found_table.content.values()):
        for id_col, cell in enumerate(row):
            x1 = cell.bbox.x1
            y1 = cell.bbox.y1
            x2 = cell.bbox.x2
            y2 = cell.bbox.y2
            value = cell.value
            to_dict_cell = {
                "coordinates": [[x1, y1], [x2, y2]],
                "text": value
            }
            if y1 > border_y:
                cells_list.append(to_dict_cell)
    # draw_table(cells_list)
    return cells_list