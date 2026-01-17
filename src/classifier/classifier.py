import re

from src.ocr_result import OcrResult
from src.classifier.document_types import DocumentType

# УПД
from src.classifier.upd_regex import UPD_REGEX
# Счет-фактура
from src.classifier.invoice_regex import INVOICE_REGEX, SINGLE_WORD_INVOICE_REGEX
# Торговая накладная
from src.classifier.waybill_regex import WAYBILL_REGEX


def check_words_in_ocr_result(ocr_result: OcrResult, regex_words_lists):
    is_word_found = [False] * len(regex_words_lists)

    for bbox, text, conf in ocr_result:
        for index, word_regexes in enumerate(regex_words_lists):
            if any(re.search(pat, text, re.IGNORECASE) for pat in word_regexes):
                is_word_found[index] = True
                break

    return all(is_word_found)


def get_document_type(ocr_result: OcrResult) -> DocumentType:
    if check_words_in_ocr_result(ocr_result, UPD_REGEX):
        return DocumentType.UPD
    elif check_words_in_ocr_result(ocr_result, WAYBILL_REGEX):
        return DocumentType.WAYBILL
    elif check_words_in_ocr_result(ocr_result, INVOICE_REGEX):
        return DocumentType.INVOICE
    elif check_words_in_ocr_result(ocr_result, SINGLE_WORD_INVOICE_REGEX):
        return DocumentType.INVOICE
    else:
        return DocumentType.UNRECOGNIZED