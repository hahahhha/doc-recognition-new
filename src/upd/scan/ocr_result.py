class OcrResult:
    """Класс для представления результатов ocr
    (на случай смены движка создается единая структура)
    Содержит список, где каждый элемент - спиоск из трех элементов: bbox, text, confidience
    """
    def __init__(self):
        self.__ocr_results = []

    def insert(self, bbox: list, text: str, confidence: float):
        bbox_to_int_points = [[int(p[0]), int(p[1])] for p in bbox]
        self.__ocr_results.append([bbox_to_int_points, text, confidence])

    def __iter__(self):
        return iter(self.__ocr_results)

    def print(self, confidience = False):
        for bbox, text, conf in self.__ocr_results:
            print(bbox, text, text if confidience else '')