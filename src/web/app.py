import cv2
import tempfile
from flask import Flask, request, jsonify
from src.upd.scan.parse_scan import parse_scan_dict


def create_app() -> Flask:
    app = Flask(__name__)

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok'})

    @app.route('/scan', methods=['GET'])
    def scan():
        if 'image' not in request.files:
            return jsonify({'error': 'no image part'}), 400

        image_file = request.files['image']

        if image_file.filename == '':
            return jsonify({'error': 'no image part'}), 400

        with tempfile.NamedTemporaryFile(suffix='.jpg') as tmp:
            image_file.save(tmp.name)
            img = cv2.imread(tmp.name)
            parse_result = parse_scan_dict(img)
            return jsonify(parse_result)


    return app