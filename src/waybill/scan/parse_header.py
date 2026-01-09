import re
from project_scripts.bbox_finder import BboxFinder
from src.ocr_result import OcrResult
from src.data_parse_object import DataParseObject


EXTEND_BBOX_VALUE = 20

parse_objects = [
    # есть несколько слов грузополучатель, поэтому убрал
    # DataParseObject('Грузополучатель', ['грузополучатель'], 'receiver'),
    DataParseObject('Поставщик', ['поставщик'], 'supplier'),
    DataParseObject('Плательщик', ['плательщик'], 'payer'),
    DataParseObject('Основание', ['основание'], 'footing')
]

def find_document_num_and_date(bbox_finder: BboxFinder) -> tuple:
    # bbox товарная накладная
    waybill_bboxes_lists, success = bbox_finder.find_sentence_bbox_sequences(
        [['товарная'], ['накладная']]
    )
    if not success:
        return 'not found', 'not found'
    singled_bboxes = []
    for bbox_list in waybill_bboxes_lists:
        singled_bboxes.append(BboxFinder.get_single_bbox(bbox_list))
    title_bbox = min(singled_bboxes, key=lambda bbox: bbox[0][1])
    # print(waybill_bbox, 'waybill_bbox')
    found_values = bbox_finder.find_value_by_title_bbox(title_bbox)
    if len(found_values) < 2:
        return 'not found', 'not found',
    return found_values.split()[0], found_values.split()[1]


def find_basis(bbox_finder: BboxFinder) -> dict:
    basis = {
        "number": "not found", # example: "7788/УЕ"
        "date": "not found",
    }

    number_found_bboxes = bbox_finder.find_all_matching_bboxes(['номер'])
    date_found_bboxes = bbox_finder.find_all_matching_bboxes(['дата'])

    number_found_bboxes.sort(key=lambda bbox: (-bbox[0][0], bbox[0][1]))
    date_found_bboxes.sort(key=lambda bbox: (-bbox[0][0], bbox[0][1]))

    rightest_top_number_bbox = number_found_bboxes[0]
    rightest_top_date_bbox = date_found_bboxes[0]

    basis["number"] = bbox_finder.find_value_by_title_bbox(rightest_top_number_bbox)
    basis["date"] = bbox_finder.find_value_by_title_bbox(rightest_top_date_bbox)
    return basis


def find_contract(bbox_finder: BboxFinder) -> dict:
    contract = {
        "number": "not found", # example: "7788/УЕ"
        "date": "not found",
    }

    number_found_bboxes = bbox_finder.find_all_matching_bboxes(['номер'])
    date_found_bboxes = bbox_finder.find_all_matching_bboxes(['дата'])

    number_found_bboxes.sort(key=lambda bbox: (-bbox[0][0], bbox[0][1]))
    date_found_bboxes.sort(key=lambda bbox: (-bbox[0][0], bbox[0][1]))

    rightest_bottom_number_bbox = number_found_bboxes[0]
    rightest_bottom_date_bbox = date_found_bboxes[0]

    contract["number"] = bbox_finder.find_value_by_title_bbox(rightest_bottom_number_bbox)
    contract["date"] = bbox_finder.find_value_by_title_bbox(rightest_bottom_date_bbox)
    return contract


def parse_receiver(line: str) -> dict:
    receiver = {
        "name": "ООО \"Торговый дом \"Комплексный\"",
        "inn": "7799434926",
        "kpp": "121170",
        "address": "Москва г, Кутузовский пр-кт, дом № 1/7, строение 2",
        "bankAccount": "40702810399994349242",
        "bankName": "ПАО СБЕРБАНК",
        "bik": "044525225",
        "correspondentAccount": "30101810400000000225"
    }

    return receiver

def parse_header_to_dict(ocr_result: OcrResult) -> dict:
    bbox_finder = BboxFinder(
        ocr_result=ocr_result,
        extend_bbox_value=EXTEND_BBOX_VALUE,
        data_parse_objects=parse_objects
    )
    find_document_num_and_date(bbox_finder)
    result = bbox_finder.find_values_by_parse_objects()
    # result = dict()
    doc_num, doc_date = find_document_num_and_date(bbox_finder)
    result["documentNumber"] = doc_num
    result["documentDate"] = doc_date

    result["basis"] = find_basis(bbox_finder)
    # находит автоматически из-за большого EXTENDED_BBOX_VALUE, может быть ошибка потенциально
    result["contract"] = find_contract(bbox_finder)
    return result
