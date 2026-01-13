from src.ocr_result import OcrResult
from .parse_header import parse_header_to_dict
from .parse_table import parse_table_to_cells_list

# товарная накладная

def parse_scan_dict_with_ocr_result(img_path: str, ocr_result: OcrResult) -> dict:
    result = parse_header_to_dict(ocr_result)
    result["table"] = parse_table_to_cells_list(img_path, ocr_result)
    return result