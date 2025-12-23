# app.py
from flask import Flask
from flask_cors import CORS
from extensions import db
from routes import main_bp
from utils import refresh_idiom_cache
import os
from dotenv import load_dotenv
from utils import refresh_idiom_cache, datetimeformat

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)

    

    # Configuration
    app.secret_key = os.getenv("FLASK_SECRET", "dev_secret")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://root:root%password@localhost/kannada_db?charset=utf8mb4')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize Extensions
    db.init_app(app)

    app.add_template_filter(datetimeformat) 

 

    # Register Blueprints (Routes)
    app.register_blueprint(main_bp)

    # Create Tables & Load Cache
    with app.app_context():
        db.create_all()
        refresh_idiom_cache()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)