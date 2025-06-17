import os
import sys
# DON'T CHANGE THIS PATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.ingestion import ingestion_bp
from src.routes.matching import matching_bp
from src.routes.scoring import scoring_bp
from src.routes.insights import insights_bp
from src.routes.monitoring import monitoring_bp
from src.utils.error_handling import ErrorHandler
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pricing_intelligence.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, origins="*")
    
    # Register error handlers
    ErrorHandler.register_error_handlers(app)
    
    # Register blueprints
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(ingestion_bp, url_prefix='/api')
    app.register_blueprint(matching_bp, url_prefix='/api')
    app.register_blueprint(scoring_bp, url_prefix='/api')
    app.register_blueprint(insights_bp, url_prefix='/api')
    app.register_blueprint(monitoring_bp, url_prefix='/api')
    
    # Create tables
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            raise
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {
            'status': 'healthy',
            'service': 'pricing-intelligence-api',
            'version': '1.0.0'
        }
    
    return app

app = create_app()

if __name__ == '__main__':
    try:
        logger.info("Starting Pricing Intelligence Platform API")
        app.run(host='0.0.0.0', port=5001, debug=True)
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        sys.exit(1)

