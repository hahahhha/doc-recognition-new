import cv2
import tempfile
import os
from flask import Flask, request, jsonify

from upd import parse_scan_dict

def create_app() -> Flask:
    app = Flask(__name__)

    # Создаем папку для временных файлов
    # TEMP_FOLDER = os.path.join(os.path.dirname(__file__), 'temp_uploads')
    # os.makedirs(TEMP_FOLDER, exist_ok=True)

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok'})


    @app.route('/scan', methods=['GET'])
    def scan_by_route():
        path_img = request.args['url']
        tesseract_path = request.args['tesseract_path']
        img = cv2.imread(path_img)
        parse_result = parse_scan_dict(img)
        return jsonify(parse_result)

    return app
