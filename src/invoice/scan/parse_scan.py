from src.project_scripts.bbox_finder import BboxFinder
from src.upd.scan.parse_scan import parse_scan_dict as upd_parse_scan_dict
from src.upd.scan.parse_header import parse_header_to_dict
from src.ocr_result import OcrResult
from src.project_scripts.parse_table_by_borders import parse_table_by_borders

def prettify_result(result: dict) -> dict:
    result_copy = result.copy()
    result_copy['shipper'] = result['consignor']
    del result_copy['consignor']
    result_copy['document_info'] = {
        "document_type": "Счет-фактура"
    }
    return result_copy


def parse_scan_dict(img_path: str, tesseract_path: str) -> dict:
    result = upd_parse_scan_dict(img_path, tesseract_path)
    return prettify_result(result)


def parse_table_to_cells_list(img_path: str, ocr_result: OcrResult) -> list[dict]:
    bbox_finder = BboxFinder(ocr_result, 5, [])
    bottom_bboxes = bbox_finder.find_all_matching_bboxes(['всего'])
    top_bboxes = bbox_finder.find_all_matching_bboxes(['валюта'])
    if bottom_bboxes and top_bboxes:
        bottom_y = max(bottom_bboxes, key=lambda b: b[2][1])[0][1]
        top_y = min(top_bboxes, key=lambda b: b[2][1])[2][1]
        return parse_table_by_borders(img_path, top_y, bottom_y)
    return []


def parse_scan_dict_with_ocr_result(img_path: str, ocr_result: OcrResult) -> dict:
    result = parse_header_to_dict(ocr_result)
    table = parse_table_to_cells_list(img_path, ocr_result)
    result['table'] = table
    return prettify_result(result)