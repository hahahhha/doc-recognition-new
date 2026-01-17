from src.project_scripts.bbox_finder import BboxFinder
from src.upd.scan.parse_scan import parse_scan_dict as upd_parse_scan_dict
from src.upd.scan.parse_header import parse_header_to_dict
from src.upd.scan.parse_table import parse_table_to_cells_list
from src.upd.scan.parse_scan import parse_scan_dict_with_ocr_result as upd_parse_scan_dict_with_ocr_result
from src.ocr_result import OcrResult


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
    print('hueat')
    return prettify_result(result)


def parse_scan_dict_with_ocr_result(img_path: str, ocr_result: OcrResult) -> dict:
    result = parse_header_to_dict(ocr_result)
    table = parse_table_to_cells_list(img_path, ocr_result)
    bbox_finder = BboxFinder(ocr_result, 5, [])
    bottom_bboxes = bbox_finder.find_all_matching_bboxes(['всего'])
    print(*bottom_bboxes, sep='\n')
    if bottom_bboxes:
        bottom_bbox = max(bottom_bboxes, key=lambda b: b[0][1])
        bottom_y = bottom_bbox[0][1] - 5
        table = [cell for cell in table if cell['coordinates'][0][1] < bottom_y]
        result['table'] = table
    return prettify_result(result)