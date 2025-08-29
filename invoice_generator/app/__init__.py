from flask import Flask
from app.extensions import db, mail

def create_app():
    app = Flask(__name__)
    
    # Config
    app.config.from_object('config.Config')
    
    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    
    # Register Blueprints
    from app.routes import main
    app.register_blueprint(main)

    return app
