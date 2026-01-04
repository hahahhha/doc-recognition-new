import re

from project_scripts.bbox_finder import BboxFinder
from src.ocr_result import OcrResult
from src.data_parse_object import DataParseObject


EXTEND_BBOX_VALUE = 20

parse_objects = [
    DataParseObject('Грузополучатель', ['грузополучатель'], 'consignor'),
    DataParseObject('Поставщик', ['поставщик'], 'provider'),
    DataParseObject('Плательщик', ['плательщик'], 'payer'),
    DataParseObject('Основание', ['основание'], 'footing')
]


def parse_header_to_dict(ocr_result: OcrResult) -> dict:
    bbox_finder = BboxFinder(
        ocr_result=ocr_result,
        extend_bbox_value=EXTEND_BBOX_VALUE,
        data_parse_objects=parse_objects
    )

    result = bbox_finder.find_values()
    return result
