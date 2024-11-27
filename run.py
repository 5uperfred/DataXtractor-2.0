from flask import Flask
import config

def create_app():
    app = Flask(__name__)
    
    from app.routes import bp
    app.register_blueprint(bp, url_prefix=config.API_V1_STR)
    
    @app.route('/')
    def index():
        return {
            "name": config.PROJECT_NAME,
            "version": config.VERSION,
            "description": config.DESCRIPTION,
            "endpoints": [
                f"{config.API_V1_STR}/extract",
                f"{config.API_V1_STR}/extract/ocr",
                f"{config.API_V1_STR}/extract/columns"
            ]
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
