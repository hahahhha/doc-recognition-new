import cv2
import tempfile, os
from img2table.ocr import TesseractOCR
from img2table.document import Image

from src.project_scripts.bbox_finder import BboxFinder
from src.project_scripts.extract_table_cells import extract_table_cells_to_list
from src.ocr_result import OcrResult

EXTEND_BBOX_VALUE = 10


def parse_table_to_cells_list(img_path: str, ocr_result: OcrResult) -> list[dict]:
    bbox_finder = BboxFinder(
        ocr_result=ocr_result,
        extend_bbox_value=EXTEND_BBOX_VALUE,
        data_parse_objects=[]
    )

    op_type_bboxes_seq, op_type_bboxes_found = bbox_finder.find_sentence_bbox_sequences_with_success([
        ['вид'], ['операции']
    ])
    total_bboxes = bbox_finder.find_all_matching_bboxes(['итого'])

    img = cv2.imread(img_path)
    cells_list = []
    if op_type_bboxes_found and total_bboxes:
        op_type_bbox = bbox_finder.get_single_bbox(op_type_bboxes_seq[0])
        total_bbox = total_bboxes[0]

        y_top = op_type_bbox[2][1]
        y_bottom = total_bbox[0][1]
        cropped = img[y_top:y_bottom + 10, :]

        ocr = TesseractOCR(n_threads=1, lang="rus")

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            temp_path = tmp_file.name

        cv2.imwrite(temp_path, cropped)

        try:
            doc = Image(src=temp_path)
            extracted_tables = doc.extract_tables(ocr=ocr,
                                                  implicit_rows=False,
                                                  implicit_columns=False,
                                                  borderless_tables=False,
                                                  min_confidence=50)

            if not extracted_tables:
                raise Exception("Не удалось распознать таблицу в документе")
            cells_list = extract_table_cells_to_list(extracted_tables[0])

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    return cells_list