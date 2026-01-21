"""
TEDI Flask Application Factory
"""
from flask import Flask, g, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restx import Api
from celery import Celery

from config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
celery = Celery(__name__)


def create_app(config_name='default'):
    """
    Application factory pattern

    Args:
        config_name: Configuration name (development, production, testing)

    Returns:
        Flask application instance
    """
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=app.config['CORS_ORIGINS'])

    # Initialize Celery
    celery.conf.update(app.config)

    # Initialize Flask-RESTX API
    api = Api(
        app,
        version=app.config['API_VERSION'],
        title=app.config['API_TITLE'],
        description=app.config['API_DESCRIPTION'],
        doc='/api/docs',
        prefix='/api/v1'
    )

    # Register blueprints/namespaces
    from app.routes import agriculture, auth, realestate, employment, business, public, export

    api.add_namespace(public.ns, path='/public')
    api.add_namespace(agriculture.ns, path='/agriculture')
    api.add_namespace(auth.ns, path='/auth')

    # POST-MVP: New verticals
    api.add_namespace(realestate.ns, path='/realestate')
    api.add_namespace(employment.ns, path='/employment')
    api.add_namespace(business.ns, path='/business')
    
    # Export routes
    api.add_namespace(export.ns, path='/export')

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'version': app.config['API_VERSION']}, 200

    # Anti-scraping protection
    from app.utils.anti_scraping import (
        anti_scraping_middleware, 
        add_security_headers,
        log_api_access
    )
    
    @app.before_request
    def before_request():
        """Apply anti-scraping checks before each request"""
        # Skip for health check and docs
        if request.path in ['/health', '/api/docs', '/api/docs/']:
            return
        if request.path.startswith('/swaggerui'):
            return
        
        anti_scraping_middleware()
    
    @app.after_request
    def after_request(response):
        """Add security headers and log access"""
        response = add_security_headers(response)
        log_api_access(
            api_key_info=getattr(g, 'api_key_info', None),
            response_size=response.content_length or 0
        )
        return response

    return app


def create_celery_app(app=None):
    """
    Create Celery app instance

    Args:
        app: Flask application instance

    Returns:
        Celery application instance
    """
    app = app or create_app()
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
