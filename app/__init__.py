from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
import cloudinary
import cloudinary.uploader
import cloudinary.api
from config import config
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='default'):
    """Application factory pattern"""
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Initialize Cloudinary
    if app.config['CLOUDINARY_CLOUD_NAME']:
        cloudinary.config(
            cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
            api_key=app.config['CLOUDINARY_API_KEY'],
            api_secret=app.config['CLOUDINARY_API_SECRET']
        )
    
    # Register blueprints
    from app.routes import main, products, ai_routes, admin, blog
    
    app.register_blueprint(main.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(ai_routes.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(blog.bp)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
