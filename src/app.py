import cv2
import tempfile
import os
from flask import Flask, request, jsonify

from upd import parse_scan_dict

def create_app() -> Flask:
    app = Flask(__name__)

    # Создаем папку для временных файлов
    TEMP_FOLDER = os.path.join(os.path.dirname(__file__), 'temp_uploads')
    os.makedirs(TEMP_FOLDER, exist_ok=True)

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok'})

    @app.route('/scan', methods=['POST'])  # Изменено с GET на POST
    def scan():
        # Проверяем, есть ли файл в запросе
        if 'image' not in request.files:
            return jsonify({'error': 'no image part'}), 400

        image_file = request.files['image']

        # Проверяем, есть ли имя файла
        if image_file.filename == '':
            return jsonify({'error': 'no selected file'}), 400

        # Проверяем расширение файла
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        file_ext = os.path.splitext(image_file.filename)[1].lower()

        if file_ext not in allowed_extensions:
            return jsonify({'error': f'unsupported file type: {file_ext}'}), 400

        with tempfile.NamedTemporaryFile(
                suffix=file_ext,
                dir=TEMP_FOLDER,  # Используем нашу папку
                delete=False  # Не удалять сразу, чтобы cv2 успел прочитать
        ) as tmp:
            # Сохраняем файл
            image_file.save(tmp.name)
            temp_path = tmp.name
        img = cv2.imread(temp_path)

        if img is None:
            return jsonify({'error': 'cannot read image file'}), 400

        # Обрабатываем изображение
        parse_result = parse_scan_dict(img)
        return jsonify(parse_result)
        # Создаем временный файл в безопасной директории
        # try:
        #     with tempfile.NamedTemporaryFile(
        #             suffix=file_ext,
        #             dir=TEMP_FOLDER,  # Используем нашу папку
        #             delete=False  # Не удалять сразу, чтобы cv2 успел прочитать
        #     ) as tmp:
        #         # Сохраняем файл
        #         image_file.save(tmp.name)
        #         temp_path = tmp.name
        #
        #     try:
        #         # Читаем изображение
        #         img = cv2.imread(temp_path)
        #
        #         if img is None:
        #             return jsonify({'error': 'cannot read image file'}), 400
        #
        #         # Обрабатываем изображение
        #         parse_result = parse_scan_dict(img)
        #         return jsonify(parse_result)
        #
        #     finally:
        #         # Удаляем временный файл после обработки
        #         if os.path.exists(temp_path):
        #             os.remove(temp_path)
        #
        # except PermissionError as e:
        #     return jsonify({'error': f'permission denied: {str(e)}'}), 500
        # except Exception as e:
        #     print(e.args)
        #     return jsonify({'error': f'processing failed: {str(e)}'}), 500

    return app
