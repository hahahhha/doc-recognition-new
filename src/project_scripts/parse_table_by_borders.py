import cv2
import tempfile, os
from img2table.ocr import TesseractOCR
from img2table.document import Image
from .extract_table_cells import extract_table_cells_to_list


def parse_table_by_borders(img_path: str, y_top = 0, y_bottom = 10**9) -> list[dict]:
    ocr = TesseractOCR(n_threads=1, lang="rus")
    img = cv2.imread(img_path)
    cropped = img[y_top : y_bottom, : ]
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