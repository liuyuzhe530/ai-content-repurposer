from flask import Flask
from src.routes.main import main_bp
from src.routes.api import api_bp
from src.services.scheduler import init_scheduler
import os

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.environ.get('APP_SECRET_KEY', 'dev-secret-key')
    app.config['ANTHROPIC_API_KEY'] = os.environ.get('ANTHROPIC_API_KEY', '')
    app.config['APP_URL'] = os.environ.get('APP_URL', 'http://localhost:5000')
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    
    if app.config['FLASK_ENV'] != 'testing':
        init_scheduler(app)
    
    return app
