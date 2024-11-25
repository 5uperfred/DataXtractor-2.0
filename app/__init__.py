from flask import Flask
from config import settings

def create_app():
    app = Flask(__name__)
    
    from app.routes import api_router
    app.register_blueprint(api_router, url_prefix=settings.API_V1_STR)
    
    return app
