import cv2
from abc import ABC, abstractmethod
from src.ocr_result import OcrResult
from src.project_scripts.tesseract_ocr_result import get_tesseract_ocr_result

class ScanParser(ABC):
    """Абстрактный класс для парсеров сканов документов разных типов
    """
    def parse_scan(self, img_path: str, ocr_result: OcrResult = None) -> dict:
        if ocr_result is None:
            img = cv2.imread(img_path)
            ocr_result = get_tesseract_ocr_result(img)
        result = self.parse_header(ocr_result)
        result["table"] = self.parse_table(img_path, ocr_result)
        return result


    @abstractmethod
    def parse_header(self, ocr_result: OcrResult) -> dict:
        pass

    @abstractmethod
    def parse_table(self, img_path: str, ocr_result: OcrResult) -> list[dict]:
        pass
