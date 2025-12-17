import re

from .ocr_result import OcrResult
from .data_parse_object import DataParseObject


extend_bbox_value = 5

parse_objects = [
    DataParseObject("продавец", "продавец", "seller_name"),
    DataParseObject("инн/кпп продавца", r"инн.*кпп\s*продавца", 'seller_inn/kpp'),
    DataParseObject("грузоотправитель и его адрес", r"грузоотправитель\s*и\s*его\s*адрес", 'consignor_address'),
    DataParseObject("грузополучатель и его адрес", r"грузополучатель\s*и\s*его\s*адрес", 'consignee_address'),
    DataParseObject("к платежно-расчетному документу", r"к\s*платежно.*расчетному\s*документу", 'payment_document'),
    DataParseObject("инн/кпп покупателя", r"инн.*кпп\s*покупателя", 'buyer_inn/kpp'),
    DataParseObject("валюта: наименование, код", r"валюта.*\s*наименование.*\s*код", 'currency'),
    DataParseObject("покупатель", r"^покупатель", "buyer_name")
]


def __find_text_by_title_bbox(ocr_result: OcrResult, title_bbox: list) -> str:
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


def parse_header_to_dict(ocr_result: OcrResult):
    pass