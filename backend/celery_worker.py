"""
Celery Worker Entry Point

This file initializes the Celery worker with all tasks and configuration.

Usage:
    # Start worker
    celery -A celery_worker.celery_app worker --loglevel=info

    # Start beat scheduler
    celery -A celery_worker.celery_app beat --loglevel=info

    # Start both (development only)
    celery -A celery_worker.celery_app worker --beat --loglevel=info

    # With specific queues
    celery -A celery_worker.celery_app worker -Q scheduler,agriculture --loglevel=info
"""
import os
from app import create_app, create_celery_app

# Set default config
os.environ.setdefault('FLASK_ENV', 'development')

# Create Flask app
flask_app = create_app()

# Create Celery app
celery_app = create_celery_app(flask_app)

# Load Celery configuration from celeryconfig.py
celery_app.config_from_object('app.celeryconfig')

# Import all task modules to register them
from app.tasks import scheduler
from app.tasks import agriculture
from app.tasks import realestate
from app.tasks import employment
from app.tasks import business

# For debugging: print registered tasks
if __name__ == '__main__':
    print("\n📋 Registered Celery tasks:")
    for task_name in sorted(celery_app.tasks.keys()):
        if not task_name.startswith('celery.'):
            print(f"  ✓ {task_name}")
    print()
