import re

from src.ocr_result import OcrResult
from src.data_parse_object import DataParseObject


class BboxFinder:
    def __init__(self, ocr_result: OcrResult, extend_bbox_value: int, data_parse_objects: list[DataParseObject]):
        self.ocr_result = ocr_result
        self.EXTEND_BBOX_VALUE = extend_bbox_value
        self.parse_objects = data_parse_objects.copy()

    def find_value_by_title_bbox(self, title_bbox: list) -> str:
        title_right_x = title_bbox[1][0]
        title_top_y = title_bbox[1][1]
        title_bottom_y = title_bbox[2][1]

        result = []

        for bbox, text, conf in self.ocr_result:
            cur_left_x = bbox[0][0]
            cur_top_y = bbox[0][1]
            cur_bottom_y = bbox[2][1]
            if cur_left_x > title_right_x and cur_top_y >= title_top_y - self.EXTEND_BBOX_VALUE and cur_bottom_y <= title_bottom_y + self.EXTEND_BBOX_VALUE:
                if text not in result and text != ' ':
                    result.append(text)

        return ' '.join(result)

    def find_values(self) -> dict:
        result = dict(zip(
            [po.json_field_title for po in self.parse_objects],
            ['not found' for _ in range(len(self.parse_objects))]
        ))

        for po in self.parse_objects:
            for bbox, text, conf in self.ocr_result:
                # нашли координаты названия поля
                if any(re.search(pat, text, re.IGNORECASE) for pat in po.title_search_patterns):
                    result[po.json_field_title] = self.find_value_by_title_bbox(bbox)
                    # print(f'found field: {po.field_title} : {bbox}')
        return result