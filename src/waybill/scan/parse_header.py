import re
from math import dist
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

def find_document_num_and_date(bbox_finder: BboxFinder):
    # bbox товарная накладная
    waybill_bboxes_lists, success = bbox_finder.find_sentence_bbox_sequences(
        [['товарная'], ['накладная']]
    )
    if not success:
        return 'not found'
    singled_bboxes = []
    for bbox_list in waybill_bboxes_lists:
        singled_bboxes.append(BboxFinder.get_single_bbox(bbox_list))
    title_bbox = min(singled_bboxes, key=lambda bbox: bbox[0][1])
    # print(waybill_bbox, 'waybill_bbox')
    found_values = bbox_finder.find_value_by_title_bbox(title_bbox)
    if len(found_values) < 2:
        return 'not found'
    return found_values.split()[:2]


def parse_header_to_dict(ocr_result: OcrResult) -> dict:
    bbox_finder = BboxFinder(
        ocr_result=ocr_result,
        extend_bbox_value=EXTEND_BBOX_VALUE,
        data_parse_objects=parse_objects
    )
    find_document_num_and_date(bbox_finder)
    result = bbox_finder.find_values()
    result['num_and_date'] = find_document_num_and_date(bbox_finder)
    return result
