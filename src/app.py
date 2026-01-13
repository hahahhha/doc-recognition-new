from flask import Flask, request, jsonify, make_response
import logging
import flask.cli

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.classifier import DocumentType


from project_scripts.parse_scan_to_dict import parse_scan_to_dict


def disable_logging(app):
    log = logging.getLogger('werkzeug')
    app.logger.disabled = True
    log.disabled = True
    flask.cli.show_server_banner = lambda *args: None
    logging.getLogger('pytesseract').disabled = True


def create_scan_response(img_path: str, tesseract_path: str = ''):
    parse_result = parse_scan_to_dict(img_path, tesseract_path)
    doc_type, type_name = parse_result['document_type']
    parse_result['document_type'] = type_name

    response = make_response(jsonify(parse_result))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Document-Type'] = str(doc_type).lower() if doc_type != DocumentType.WAYBILL else 'torg12'
    return response


def create_app() -> Flask:
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'

    # disable_logging(app)

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok'})

    @app.route('/scan/tesseract', methods=['GET'])
    def scan_by_route_with_tesseract_path():
        path_img = request.args['url']
        tesseract_path = request.args['tesseract_path']
        return create_scan_response(img_path=path_img, tesseract_path=tesseract_path)

    @app.route('/scan', methods=['GET'])
    def scan_by_route():
        path_img = request.args['url']
        return create_scan_response(img_path=path_img)

    return app
