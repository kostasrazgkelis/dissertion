from flask import Flask
from flask_cors import CORS
import os
from db import init_app as init_app_db
from blueprints import init_app as init_app_bp

app = Flask(__name__, static_folder='static')
app.config.from_object(__name__)

CORS(app, resources={r'/*': {'origins': '*'}}, supports_credentials=True)

init_app_db(app)
init_app_bp(app)   


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=os.environ.get('FLASK_DEBUG', False))