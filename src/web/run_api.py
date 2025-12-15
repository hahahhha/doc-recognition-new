import os, sys
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.web.app import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=3210)