from flask import Flask, request, jsonify
import logging
import flask.cli
from scripts.parse_scan_to_dict import parse_scan_to_dict


def disable_logging(app):
    log = logging.getLogger('werkzeug')
    app.logger.disabled = True
    log.disabled = True
    flask.cli.show_server_banner = lambda *args: None
    logging.getLogger('pytesseract').disabled = True


def create_app() -> Flask:
    app = Flask(__name__)

    disable_logging(app)

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok'})

    @app.route('/scan/tesseract', methods=['GET'])
    def scan_by_route_with_tesseract_path():
        path_img = request.args['url']
        tesseract_path = request.args['tesseract_path']
        parse_result = parse_scan_to_dict(path_img, tesseract_path)
        return jsonify(parse_result)

    @app.route('/scan', methods=['GET'])
    def scan_by_route():
        path_img = request.args['url']
        parse_result = parse_scan_to_dict(path_img, '')
        return jsonify(parse_result)

    return app
