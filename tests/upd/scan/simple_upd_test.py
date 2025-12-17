from src.upd.scan.parse_header_old import parse_header_to_dict


def simple_upd_test(ocr_res):
    for k, v in parse_header_to_dict(ocr_res).items():
        print(f'{k}: {v}')



if __name__ == '__main__':
    pass
    # print('started')
    # img = cv2.imread('./../../scan_images/upd1_page1.jpg', cv2.IMREAD_GRAYSCALE)
    # reader = easyocr.Reader(['ru'])
    # ocr = reader.readtext(img)
    # ocr_result = OcrResult()
    # for bbox, text, confidence in ocr:
    #     ocr_result.insert(bbox, text, confidence)
    #     # print(text)
    # print('ocr created\n')
    # res = parse_table('./../../scan_images/upd1_page1.jpg', ocr_result)
    # print(*res[:100], sep='\n')
