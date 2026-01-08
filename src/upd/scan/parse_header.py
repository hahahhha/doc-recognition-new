import re

from src.ocr_result import OcrResult
from src.data_parse_object import DataParseObject

from project_scripts.bbox_finder import BboxFinder

EXTEND_BBOX_VALUE = 10

# основные названия полей для поиска за исключением адресов (их поиск происходит отдельно)
# для распознавания тессерактом оставляю только одно слово
parse_objects = [
    DataParseObject("продавец", ["продавец"], "seller_name"),
    DataParseObject("инн/кпп продавца", [r"продавца"], 'seller_inn/kpp'),
    DataParseObject("грузоотправитель и его адрес", [r"грузоотправитель"], 'consignor_address'),
    DataParseObject("грузополучатель и его адрес", [r"грузополучатель"], 'consignee_address'),
    DataParseObject("к платежно-расчетному документу", [r"к\s*платежно"], 'payment_document'),
    DataParseObject("инн/кпп покупателя", [r"покупателя"], 'buyer_inn/kpp'),
    DataParseObject("валюта: наименование, код", [r"валюта"], 'currency'),
    DataParseObject("покупатель", [r"покупатель"], "buyer_name")
]

ADDRESS_PATTERNS = [r'адрес', r'апрес', r'адрее', r'апрее']
STATUS_PATTERNS = [r'статус', r'статуе', r'етатуе', r'етатус']


def get_consignor_or_consignee_data(parsed_data: dict, key: str) -> dict:
    if key not in parsed_data:
        print('consign failed')
        return {
            "name": "not found",
            "address": "not found"
        }

    # очистка из-за особенностей считывания
    address = (parsed_data[key]
               .replace('и', '', 1)
               .replace('его', '', 1)
               .replace('адрес', '', 1)
               .strip())
    first_comma = address.find(',')
    if first_comma == -1:
        return {
            "name": address,
            "address": ""
        }
    name_part, address_part = address[:first_comma], address[first_comma + 1:]
    # грузоотправитель
    consignor = {
        "name": name_part,
        "address": address_part
    }

    return consignor


def get_buyer_and_seller_address(ocr_result: OcrResult, bbox_finder: BboxFinder) -> tuple[str, str]:
    address_title_bboxes = [bbox for bbox, text, c in ocr_result
                            if any(re.search(pat, text, re.IGNORECASE) for pat in ADDRESS_PATTERNS)]
    address_title_bboxes.sort(key=lambda b: b[0][1])
    # print(*address_title_bboxes, sep='\n')
    if len(address_title_bboxes) < 2:
        print('buyer seller faileds')
        return 'not found', 'not found'

    seller_address = bbox_finder.find_value_by_title_bbox(address_title_bboxes[0]).strip()
    buyer_address = bbox_finder.find_value_by_title_bbox(address_title_bboxes[-1]).strip()
    print('buyer seller address:', buyer_address, seller_address)
    return buyer_address, seller_address


def get_currency(parsed_data: dict) -> dict:
    # убираем лишние части, появившиеся из-за особенностей считывания
    cleaned_line = parsed_data['currency']
    if 'код' in cleaned_line:
        cleaned_line = cleaned_line[cleaned_line.index('код') + len('код') : : ]
    elif 'наименование' in cleaned_line:
        cleaned_line = cleaned_line[cleaned_line.index('наименование') + len('наименование') : : ]
    parts = cleaned_line.split(',')
    # print(parts)
    currency = {
        "name": "not found",
        "code": "not found"
    }

    if len(parts) >= 1:
        currency['name'] = parts[0].strip().capitalize()
    if len(parts) >= 2:
        code = parts[1].strip()
        if ' ' in code:
            currency['code'] = code[ : code.index(' ')]
        else:
            currency['code'] = code
    return currency


def get_status(ocr_result: OcrResult) -> str:
    status_bboxes = [bbox for bbox, text, c in ocr_result
                   if any(re.search(pat, text, re.IGNORECASE) for pat in STATUS_PATTERNS)]
    if len(status_bboxes) < 1:
        print('status failed')
        return 'not found'
    # ищем самый лево-верхний
    status_bboxes.sort(key=lambda b: b[0])
    found_status = []
    status_bbox = status_bboxes[0]
    for bbox, text, conf in ocr_result:
        lt, rt, rb, lb = bbox
        left_x = lt[0]
        top_y = lt[1]
        bottom_y = lb[1]
        right_x = rt[0]
        if left_x > status_bbox[1][0] and top_y > status_bbox[1][1] - 30 and bottom_y < status_bbox[1][1] + 30 and right_x - status_bbox[1][0] < 120:
            found_status.append(text)

    status_line = ''.join(found_status)
    return ''.join([char for char in status_line if char.isdigit()])


def parse_header_to_dict(ocr_result: OcrResult) -> dict:
    bbox_finder = BboxFinder(
        ocr_result=ocr_result,
        extend_bbox_value=EXTEND_BBOX_VALUE,
        data_parse_objects=parse_objects
    )
    result = bbox_finder.find_values()
    seller_inn_kpp = result["seller_inn/kpp"].split('/')

    buyer_address, seller_address = get_buyer_and_seller_address(ocr_result, bbox_finder)

    seller = {
        "name": result["seller_name"].strip(),
        "address": seller_address.strip(),
        "inn": 'not found' if not seller_inn_kpp else seller_inn_kpp[0].strip(),
        "kpp": 'not found' if len(seller_inn_kpp) < 2 else seller_inn_kpp[1].strip()
    }

    buyer_inn_kpp = result["buyer_inn/kpp"].split('/')
    buyer = {
        "name": result["buyer_name"].strip(),
        "address": buyer_address.strip(),
        "inn": "not found" if not buyer_inn_kpp else buyer_inn_kpp[0].strip(),
        "kpp": "not found" if len(buyer_inn_kpp) < 2 else buyer_inn_kpp[1].strip()
    }

    consignor = get_consignor_or_consignee_data(result, 'consignor_address')
    consignee = get_consignor_or_consignee_data(result, 'consignee_address')

    currency = get_currency(result)

    status = get_status(ocr_result)

    formatted = {
        "seller": seller,
        "consignor": consignor,
        "consignee": consignee,
        "buyer": buyer,
        "currency": currency,
        "status": status
    }
    print(formatted)
    return formatted