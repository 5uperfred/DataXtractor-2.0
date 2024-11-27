"""Initialize Flask application"""
import config

def create_app():
    from flask import Flask
    app = Flask(__name__)
    
    from .routes import bp
    app.register_blueprint(bp, url_prefix=config.API_V1_STR)
    
    return app
