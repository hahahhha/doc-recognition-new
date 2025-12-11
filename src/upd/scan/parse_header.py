import re
import cv2
import numpy as np
import shapely

from .ocr_result import OcrResult
from .parse_data_object import ParseDataObject

# насколько расширяются границы bbox при поиске текста
extend_bbox_value = 5

parse_objects = [
    ParseDataObject("продавец", "продавец", "seller"),
    ParseDataObject("инн/кпп продавца", r"инн.*кпп\s*продавца", 'seller inn/kpp'),
    ParseDataObject("грузоотправитель и его адрес", r"грузоотправитель\s*и\s*его\s*адрес", 'gruz address'),
    ParseDataObject("грузополучатель и его адрес", r"грузополучатель\s*и\s*его\s*адрес", 'poluchat address'),
    ParseDataObject("к платежно-расчетному документу", r"к\s*платежно.*расчетному\s*документу", 'platezh raschet'),
    ParseDataObject("инн/кпп покупателя", r"инн.*кпп\s*покупателя", 'buyer inn/kpp'),
    ParseDataObject("валюта: наименование, код", r"валюта.*\s*наименование.*\s*код", 'currency'),
]


def find_text_by_title_bbox(ocr_result: OcrResult, title_bbox: list) -> str:
    p1, p2, p3, p4 = title_bbox
    result_text = []
    # нужна для проверки ниже чем продавец или выше
    min_text_y_coord = 1e9
    for bbox, text, conf in ocr_result:
        left_top = bbox[0]
        right_bottom = bbox[2]
        if left_top[0] > p2[0] and left_top[1] >= p1[1] - extend_bbox_value and right_bottom[1] <= p3[1] + extend_bbox_value:
            result_text.append(text)
            min_text_y_coord = min(min_text_y_coord, left_top[1])

    return ''.join(result_text)


def find_buyer_and_seller_address(ocr_result: OcrResult, buyer_seller_edge_y: int) -> list:
    seller_address = ''
    buyer_address = ''
    for bbox, text, conf in ocr_result:
        if re.search('^адрес:', text, re.IGNORECASE):
            print(f'edge: {buyer_seller_edge_y}, cur_y: {bbox[0][1]}')
            value = find_text_by_title_bbox(ocr_result, bbox)
            if bbox[0][1] > buyer_seller_edge_y:
                buyer_address = value
            else:
                seller_address = value
    return [buyer_address, seller_address]


def find_seller_and_buyer_data(ocr_result: OcrResult):
    """Поиск по принципу: от слова Продавец: (левый верхний угол зоны) до К платежно-расчентому документу (левый нижний угол)"""
    result = dict()
    buyer_areas_found = [bbox for bbox, text, c in ocr_result if re.search(r'покупатель', text, re.IGNORECASE)][0]
    if not buyer_areas_found:
        raise Exception("не удалось найти поле покупатель на скане упд")
    print(f'buyer_area: {buyer_areas_found}')
    buyer_top_y = buyer_areas_found[0][1]
    for parse_obj in parse_objects:
        for bbox, text, c in ocr_result:
            # нашлось название поля, например инн/кпп покупателя и т.п.
            if re.search(parse_obj.title_search_pattern, text, re.IGNORECASE):
                field_value= find_text_by_title_bbox(ocr_result, bbox)
                result[parse_obj.json_field_title] = field_value

    buyer_address, seller_adders = find_buyer_and_seller_address(ocr_result, buyer_top_y)
    result['buyer_address'] = buyer_address
    result['seller_address'] = seller_adders
    return result




