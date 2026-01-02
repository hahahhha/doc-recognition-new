import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)

from app import create_app

if __name__ == '__main__':
    # print('server started')
    app = create_app()
    app.run(port=3210)