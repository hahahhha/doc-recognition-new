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

def find_pair_with_min_dist(first_bboxes, second_bboxes):
    mn_dist = float('inf')
    result = []
    for bbox in first_bboxes:
        for bbox2 in second_bboxes:
            if dist(bbox[0], bbox2[0]) < mn_dist:
                result = [bbox, bbox2]
                mn_dist = dist(bbox[0], bbox2[0])

    return result


def find_document_num_and_date(bbox_finder: BboxFinder):
    # bbox товарная накладная
    waybill_bbox = bbox_finder.find_sentence_bbox_sequences(
        [['товарная'], ['накладная']]
    )[0]
    # max_delta_x получена экспериментально :))
    print(waybill_bbox, 'waybill_bbox')
    found_values = bbox_finder.find_value_by_title_bbox(waybill_bbox, max_delta_x=400)
    return found_values


def parse_header_to_dict(ocr_result: OcrResult) -> dict:
    bbox_finder = BboxFinder(
        ocr_result=ocr_result,
        extend_bbox_value=EXTEND_BBOX_VALUE,
        data_parse_objects=parse_objects
    )
    bbox_finder.ocr_result.print(confidence=False, coordinates=True)
    find_document_num_and_date(bbox_finder)
    result = bbox_finder.find_values()
    result['num_and_date'] = find_document_num_and_date(bbox_finder)
    return result
