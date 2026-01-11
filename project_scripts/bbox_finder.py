import re
from itertools import product
from math import dist

from src.ocr_result import OcrResult
from src.data_parse_object import DataParseObject


class BboxFinder:
    def __init__(self, ocr_result: OcrResult, extend_bbox_value: int, data_parse_objects: list[DataParseObject]):
        self.__ocr_result = ocr_result
        self.__EXTEND_BBOX_VALUE = extend_bbox_value
        self.__parse_objects = data_parse_objects.copy()

    def find_all_matching_bboxes(self, to_find_regexes: list) -> list:
        bboxes = []
        for bbox, text, conf in self.__ocr_result:
            if any(re.search(pat, text, re.IGNORECASE) for pat in to_find_regexes):
                bboxes.append(bbox)
        return bboxes

    @staticmethod
    def get_single_bbox(bboxes_list: list[list[list[int]]]) -> list[list[int]]:
        """Возвращает единый bbox, покрывающий все bbox'ы,
        переданные в списке - находит "самый" левый верхний, самый правый верхний и т.д."""
        left_x = min([bbox[0][0] for bbox in bboxes_list])
        right_x = max([bbox[1][0] for bbox in bboxes_list])
        top_y = min([bbox[0][1] for bbox in bboxes_list])
        bottom_y = max([bbox[2][1] for bbox in bboxes_list])
        return [
            [left_x, top_y],
            [right_x, top_y],
            [right_x, bottom_y],
            [left_x, bottom_y]
        ]

    def find_sentence_bbox_sequences(self, sentence_word_regexes: list[list[str]], max_neighbour_words_dist = 10) -> tuple[list[list], bool]:
        """Находит bbox какого-либо набора рядом стоящих слов.
        Возвращает bbox вида [[x_left, y_top], [x_right, y_bottom]] и флаг - успех поиска
        Необходимо в связи с тем, что tesseract настроен на считывание отдельных слов, но не словосочетаний.
        Принцип работы - для каждого regex функция ищет все подходящие слова, сохраняя их bbox,
        когда для каждого regex будут найдены подходящие bbox'ы, подходящим набором bbox'ом (итоговым словосочетанием)
        будет считаться такая комбинация, у которой суммарное расстояние соседних bbox'ов наименьшее
        """
        # список bbox'ов, найденных для каждого regex, переданного в функцию
        found_words_bboxes = [[] for _ in range(len(sentence_word_regexes))]
        for ind, regex_list in enumerate(sentence_word_regexes):
            for bbox, text, conf in self.__ocr_result:
                if any(re.search(pat, text, re.IGNORECASE) for pat in regex_list):
                    found_words_bboxes[ind].append(bbox)
        if any(len(bboxes_list) == 0 for bboxes_list in found_words_bboxes):
            return [], False

        # самое большое кол-во найденных bbox'ов для слова
        max_found_bbox_amount = len(max(found_words_bboxes, key=len))
        bbox_sequences = []
        # перебираем все возможные варианты взять последовательность bbox'ов
        # index_combination - кортеж, где index_combination[i] - один из вариантов индекса bbox'а,
        # который мог бы стоять на i-ом индексе в итоговой последовательности
        for index_combination in product(
                list(range(max_found_bbox_amount)),
                repeat=len(sentence_word_regexes)
        ):
            sum_dist = 0
            # идем по парам индексов, т.к. ищем суммарное попарное расстояние
            for i in range(0, len(index_combination) - 1):
                cur_bbox_ind = index_combination[i]
                next_bbox_ind = index_combination[i + 1]
                # проверяем, может ли быть такой индекс в принципе
                if cur_bbox_ind >= len(found_words_bboxes[i]):
                    continue
                if next_bbox_ind >= len(found_words_bboxes[i + 1]):
                    continue
                cur_bbox = found_words_bboxes[i][cur_bbox_ind]
                next_bbox = found_words_bboxes[i + 1][next_bbox_ind]
                # проверка на то, что слова слишком далеко друг от друга, такое не подходит
                if dist(cur_bbox[1], next_bbox[0]) > max_neighbour_words_dist:
                    break
                sum_dist += dist(cur_bbox[1], next_bbox[0])
            # если цикл не разу не прерывался, значит все слова находятся на допустимом расстоянии
            else:
                cur_bbox_seq = [found_words_bboxes[i][index_combination[i]] for i in range(len(index_combination))]
                bbox_sequences.append((
                    cur_bbox_seq,
                    sum_dist
                ))
        # ищем подходящую последовательность, сравнивая суммарную длину
        # min_dist = min(bbox_sequences, key=lambda s: s[1])[1]
        return [seq for seq, d in bbox_sequences], True

    def find_value_by_title_bbox(self, title_bbox: list) -> str:
        title_right_x = title_bbox[1][0]
        title_top_y = title_bbox[1][1]
        title_bottom_y = title_bbox[2][1]

        result = []

        for bbox, text, conf in self.__ocr_result:
            cur_left_x = bbox[0][0]
            cur_top_y = bbox[0][1]
            cur_bottom_y = bbox[2][1]
            if cur_left_x > title_right_x and \
                    cur_top_y >= title_top_y - self.__EXTEND_BBOX_VALUE and cur_bottom_y <= title_bottom_y + self.__EXTEND_BBOX_VALUE:
                if text not in result and text != ' ':
                    result.append(text)

        return ' '.join(result)

    def find_values_by_parse_objects(self) -> dict:
        result = dict(zip(
            [po.json_field_title for po in self.__parse_objects],
            ['not found' for _ in range(len(self.__parse_objects))]
        ))

        for po in self.__parse_objects:
            for bbox, text, conf in self.__ocr_result:
                # нашли координаты названия поля
                if any(re.search(pat, text, re.IGNORECASE) for pat in po.title_search_patterns):
                    result[po.json_field_title] = self.find_value_by_title_bbox(bbox)
                    # print(f'found field: {po.field_title} : {bbox}')
        return result


    @property
    def ocr_result(self):
        return self.__ocr_result

    @property
    def EXTEND_BBOX_VALUE(self):
        return self.__EXTEND_BBOX_VALUE

    @property
    def parse_objects(self):
        return self.__parse_objects