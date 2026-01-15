import re
from src.project_scripts.bbox_finder import BboxFinder
from src.ocr_result import OcrResult
from src.data_parse_object import DataParseObject


EXTEND_BBOX_VALUE = 20

parse_objects = [
    DataParseObject('Поставщик', ['поставщик'], 'supplier'),
    DataParseObject('Плательщик', ['плательщик'], 'payer'),
    DataParseObject('Основание', ['основание'], 'basis')
]

def find_document_num_and_date(bbox_finder: BboxFinder) -> tuple:
    # bbox товарная накладная
    waybill_bboxes_lists, success = bbox_finder.find_sentence_bbox_sequences_with_success(
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


def find_contract(bbox_finder: BboxFinder) -> dict:
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

    basis["number"] = bbox_finder.find_value_by_title_bbox(rightest_top_number_bbox, special_extend_bbox_value=6)
    date_splitted = (bbox_finder
                     .find_value_by_title_bbox(rightest_top_date_bbox, special_extend_bbox_value=6)
                     .split('.'))
    if len(date_splitted) >= 3:
        day, month, year = date_splitted[:3]
        basis["date"] = f'{year}-{month}-{day}'
    return basis


def parse_basis(line: str) -> dict:
    result = {
        "number": "not found",
        "date": "not found"
    }
    pattern = r'(\d+[\/\\]?[A-ZА-ЯЁ\/\\]*\d*[A-ZА-ЯЁ]*) от (\d{1,2})\.(\d{1,2})\.(\d{4})'

    match = re.search(pattern, line)

    if match:
        result["number"] = match.group(1)

        day = match.group(2).zfill(2)  # Добавляем ведущий ноль при необходимости
        month = match.group(3).zfill(2)  # Добавляем ведущий ноль при необходимости
        year = match.group(4)

        result["date"] = f"{year}-{month}-{day}"

    return result


def parse_organization_data(data_string: str) -> dict:
    result = {
        "name": "",
        "inn": "",
        "kpp": "",
        "address": "",
        "bankAccount": "",
        "bankName": "",
        "bik": "",
        "correspondentAccount": ""
    }
    if not data_string:
        return result
    # Извлекаем ИНН (10 или 12 цифр)
    inn_match = re.search(r'ИНН\s+(\d{10,12})', data_string)
    if inn_match:
        result["inn"] = inn_match.group(1)

    # Извлекаем название организации (от начала строки до ИНН)
    if inn_match:
        name_part = data_string[:inn_match.start()].strip()
        # Убираем запятую в конце, если есть
        name_part = name_part.rstrip(',')
        result["name"] = name_part

    # Извлекаем КПП (6 цифр, может быть после ИНН или адреса)
    kpp_match = re.search(r'КПП\s+(\d{9})', data_string)
    if not kpp_match:
        # Ищем 9 цифр после запятой или пробела
        kpp_match = re.search(r',\s*(\d{9})\s*,', data_string)
    if kpp_match:
        result["kpp"] = kpp_match.group(1)

    # Извлекаем адрес (между КПП и р/с или ИНН и р/с)
    # Сначала попробуем найти по паттерну "р/с" или "расчетный счет"
    bank_acc_match = re.search(r'р/с\s+(\d{20})', data_string)
    if not bank_acc_match:
        bank_acc_match = re.search(r'расчетный счет\s+(\d{20})', data_string)

    if bank_acc_match:
        # Адрес - это текст между КПП (или ИНН если нет КПП) и р/с
        start_idx = inn_match.end() if inn_match else 0
        if kpp_match:
            start_idx = kpp_match.end()

        # Ищем текст до "р/с" или "в банке"
        end_match = re.search(r'(р/с|в банке)', data_string[start_idx:])
        if end_match:
            address_part = data_string[start_idx:start_idx + end_match.start()].strip()
            # Чистим адрес от лишних запятых
            address_part = address_part.strip(', ')
            # Убираем возможные индексы в начале
            address_part = re.sub(r'^\d{6}\s*,?\s*', '', address_part)
            result["address"] = address_part

    # Извлекаем расчетный счет
    if bank_acc_match:
        result["bankAccount"] = bank_acc_match.group(1)

    # Извлекаем название банка (после "в банке" или "банке")
    bank_match = re.search(r'в банке\s+([^,]+)', data_string)
    if bank_match:
        result["bankName"] = bank_match.group(1).strip()

    # Извлекаем БИК
    bik_match = re.search(r'БИК\s+(\d{9})', data_string)
    if bik_match:
        result["bik"] = bik_match.group(1)

    # Извлекаем корр счет (после "к/с")
    corr_match = re.search(r'к/с\s+(\d{20})', data_string)
    if corr_match:
        result["correspondentAccount"] = corr_match.group(1)

    return result


def find_receiver(bbox_finder: BboxFinder) -> dict:
    receiver_bboxes = bbox_finder.find_all_matching_bboxes(['грузополучатель'])
    if not receiver_bboxes:
        # возвращается словарь с пустыми полями
        return parse_organization_data('')

    toppest_receiver_bbox = min(receiver_bboxes, key=lambda bbox: bbox[0][0])
    receiver_line = bbox_finder.find_value_by_title_bbox(toppest_receiver_bbox)

    return parse_organization_data(receiver_line)


def find_sender(bbox_finder: BboxFinder) -> dict:
    # ищет в области выше "организация-грузоотправитель" и левее правой границы самого верхнего "БИК"
    # самая верхняя организация
    sender_regexes = ['организация*грузо']
    sender_bboxes = bbox_finder.find_all_matching_bboxes(sender_regexes)

    bik_regexes = ['бик']
    bik_bboxes = bbox_finder.find_all_matching_bboxes(bik_regexes)

    if not sender_bboxes:
        # возвращается словарь с пустыми полями
        return parse_organization_data('')

    toppest_sender_bbox = min(sender_bboxes, key=lambda bbox: bbox[0][1])

    if not bik_bboxes:
        sender_line = bbox_finder.find_values_in_area(y_bottom=toppest_sender_bbox[0][1])
        return parse_organization_data(sender_line)

    toppest_bik_bbox = min(bik_bboxes, key=lambda bbox: bbox[0][1])

    if toppest_bik_bbox[0][1] > toppest_sender_bbox[1][1]:
        # оказался ниже, т.е. нужный бик не найден
        sender_line = bbox_finder.find_values_in_area(y_bottom=toppest_sender_bbox[0][1])
        return parse_organization_data(sender_line)

    sender_line = bbox_finder.find_values_in_area(
        x_right=toppest_bik_bbox[1][0] + 120, # с запасом
        y_bottom=toppest_sender_bbox[0][1]
    )

    return parse_organization_data(sender_line)


def parse_header_to_dict(ocr_result: OcrResult) -> dict:
    bbox_finder = BboxFinder(
        ocr_result=ocr_result,
        extend_bbox_value=EXTEND_BBOX_VALUE,
        data_parse_objects=parse_objects
    )
    find_document_num_and_date(bbox_finder)
    parsed = bbox_finder.find_values_by_parse_objects()
    result = dict()
    doc_num, doc_date = find_document_num_and_date(bbox_finder)
    result["documentNumber"] = doc_num
    result["documentDate"] = doc_date

    result["basis"] = parse_basis(parsed['basis'])

    result["contract"] = find_contract(bbox_finder)

    result["supplier"] = parse_organization_data(parsed['supplier'])
    result['payer'] = parse_organization_data(parsed['payer'])
    result['receiver'] = find_receiver(bbox_finder)
    result['sender'] = find_sender(bbox_finder)

    return result
