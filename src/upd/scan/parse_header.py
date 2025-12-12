import re

from .ocr_result import OcrResult
from .data_parse_object import DataParseObject

# насколько расширяются границы bbox при поиске текста
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


def __find_buyer_and_seller_address(ocr_result: OcrResult, buyer_seller_edge_y: int) -> list:
    seller_address = ''
    buyer_address = ''
    for bbox, text, conf in ocr_result:
        if re.search('^адрес:', text, re.IGNORECASE):
            # print(f'edge: {buyer_seller_edge_y}, cur_y: {bbox[0][1]}')
            value = __find_text_by_title_bbox(ocr_result, bbox)
            if bbox[0][1] > buyer_seller_edge_y:
                buyer_address += value
            else:
                seller_address += value
    return [buyer_address, seller_address]


def __find_seller_and_buyer_data(ocr_result: OcrResult):
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
                field_value= __find_text_by_title_bbox(ocr_result, bbox)
                result[parse_obj.json_field_title] = field_value

    buyer_address, seller_adders = __find_buyer_and_seller_address(ocr_result, buyer_top_y)
    result['buyer_address'] = buyer_address
    result['seller_address'] = seller_adders
    return result


def __get_data_from_name_and_address_line(data, key) -> dict:
    line = data[key]
    if ',' in line:
        first_comma_ind = line.index(',')
        return {
            "name": line[:first_comma_ind],
            "address": line[first_comma_ind + 1:]
        }
    return {
        "name": line,
        "address": ""
    }

def parse_header_to_dict(ocr_result: OcrResult):
    """В будущем будет добавлна обработка nlp для более точных результатов"""
    data = __find_seller_and_buyer_data(ocr_result)
    seller = {
        "name": data['seller_name'],
        "address": data['seller_address'],
        "inn": data['seller_inn/kpp'].split('/')[0],
        "kpp": data['seller_inn/kpp'].split('/')[1]
    }
    consignor = __get_data_from_name_and_address_line(data, 'consignor_address')
    consignee = __get_data_from_name_and_address_line(data, 'consignee_address')
    buyer = {
        "name": data['buyer_name'],
        "address": data['buyer_address'],
        "inn": data['buyer_inn/kpp'].split('/')[0],
        "kpp": data['buyer_inn/kpp'].split('/')[1]
    }
    return {
        "seller": seller,
        "consignor": consignor,
        "consignee": consignee,
        "buyer": buyer
    }
