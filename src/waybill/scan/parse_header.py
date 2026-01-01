import re

from src.ocr_result import OcrResult
from src.data_parse_object import DataParseObject


EXTEND_BBOX_VALUE = 20

parse_objects = [
    DataParseObject('Грузополучатель', ['грузополучатель'], 'consignor'),
    DataParseObject('Поставщик', ['поставщик'], 'provider'),
    DataParseObject('Плательщик', ['плательщик'], 'payer'),
    DataParseObject('Основание', ['основание'], 'footing'),
    
]


def parse_header_to_dict(ocr_result: OcrResult) -> dict:
    return {}