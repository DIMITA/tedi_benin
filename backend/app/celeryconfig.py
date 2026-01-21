"""
Celery Beat Schedule Configuration

Defines when each data ingestion task should run.

Frequencies are aligned with the real update frequency of each data source:
- FAOSTAT: Quarterly (updates 1-2x per year, check quarterly)
- World Bank: Annual (updates yearly, check semi-annually)
- Satellite: Monthly (aggregate monthly data)
- Local surveys: On-event (manual trigger)
- OSM: Monthly
- Employment stats: Annual
- Business registries: Quarterly
"""
from celery.schedules import crontab
from datetime import timedelta


# Celery Beat Schedule
# This defines when periodic tasks should run
beat_schedule = {
    # ============================================================
    # MASTER SCHEDULER (runs every 6 hours)
    # ============================================================
    'check-datasets-for-updates': {
        'task': 'tasks.scheduler.check_and_schedule',
        'schedule': timedelta(hours=6),  # Every 6 hours
        'options': {
            'expires': 3600,  # Task expires after 1 hour if not picked up
        }
    },

    # ============================================================
    # MAINTENANCE TASKS
    # ============================================================
    'cleanup-old-logs': {
        'task': 'tasks.scheduler.cleanup_old_logs',
        'schedule': crontab(hour=2, minute=0, day_of_week=1),  # Every Monday at 2 AM
        'args': (90,),  # Keep 90 days of logs
    },

    'update-reliability-scores': {
        'task': 'tasks.scheduler.update_reliability_scores',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),  # Every Sunday at 3 AM
    },

    # ============================================================
    # AGRICULTURE TASKS
    # ============================================================
    # Note: Most agriculture tasks are now dispatched by the master scheduler
    # based on dataset_versions.next_check_at. However, you can still define
    # fixed schedules here if needed.

    # FAOSTAT - Quarterly check (updates 1-2x per year)
    # Disabled by default - let master scheduler handle it
    # 'ingest-faostat': {
    #     'task': 'tasks.agriculture.ingest_faostat',
    #     'schedule': crontab(hour=4, minute=0, day_of_month=1, month_of_year='1,4,7,10'),  # Jan, Apr, Jul, Oct
    #     'kwargs': {
    #         'dataset_version_id': 1,  # Set appropriately
    #         'data_source_id': 1,
    #         'country_code': 'BJ'
    #     }
    # },

    # World Bank Agriculture - Semi-annual check (updates annually)
    # 'ingest-worldbank-agriculture': {
    #     'task': 'tasks.agriculture.ingest_worldbank',
    #     'schedule': crontab(hour=5, minute=0, day_of_month=1, month_of_year='1,7'),  # Jan, Jul
    #     'kwargs': {
    #         'dataset_version_id': 2,
    #         'data_source_id': 2,
    #         'country_code': 'BJ'
    #     }
    # },

    # Satellite Data - Monthly
    # 'ingest-satellite-data': {
    #     'task': 'tasks.agriculture.ingest_satellite',
    #     'schedule': crontab(hour=6, minute=0, day_of_month=1),  # First day of each month
    #     'kwargs': {
    #         'dataset_version_id': 3,
    #         'data_source_id': 3
    #     }
    # },

    # ============================================================
    # REAL ESTATE TASKS
    # ============================================================
    # OpenStreetMap - Monthly
    # 'ingest-openstreetmap': {
    #     'task': 'tasks.realestate.ingest_osm',
    #     'schedule': crontab(hour=7, minute=0, day_of_month=15),  # 15th of each month
    #     'kwargs': {
    #         'dataset_version_id': 4,
    #         'data_source_id': 4,
    #         'country_code': 'BJ'
    #     }
    # },

    # Cadastre - Quarterly
    # 'ingest-cadastre': {
    #     'task': 'tasks.realestate.ingest_cadastre',
    #     'schedule': crontab(hour=8, minute=0, day_of_month=1, month_of_year='1,4,7,10'),
    #     'kwargs': {
    #         'dataset_version_id': 5,
    #         'data_source_id': 5
    #     }
    # },

    # Property Listings - Weekly (for price monitoring)
    # 'ingest-property-listings': {
    #     'task': 'tasks.realestate.ingest_listings',
    #     'schedule': crontab(hour=9, minute=0, day_of_week=1),  # Every Monday
    #     'kwargs': {
    #         'dataset_version_id': 6,
    #         'data_source_id': 6
    #     }
    # },

    # ============================================================
    # EMPLOYMENT TASKS
    # ============================================================
    # ILOSTAT - Annual
    # 'ingest-ilostat': {
    #     'task': 'tasks.employment.ingest_ilostat',
    #     'schedule': crontab(hour=10, minute=0, day_of_month=1, month_of_year='1'),  # Every January
    #     'kwargs': {
    #         'dataset_version_id': 7,
    #         'data_source_id': 7,
    #         'country_code': 'BJ'
    #     }
    # },

    # World Bank Employment - Annual
    # 'ingest-worldbank-employment': {
    #     'task': 'tasks.employment.ingest_worldbank',
    #     'schedule': crontab(hour=11, minute=0, day_of_month=1, month_of_year='1,7'),  # Jan, Jul
    #     'kwargs': {
    #         'dataset_version_id': 8,
    #         'data_source_id': 8,
    #         'country_code': 'BJ'
    #     }
    # },

    # ============================================================
    # BUSINESS TASKS
    # ============================================================
    # Business Registry (RCCM) - Quarterly
    # 'ingest-rccm': {
    #     'task': 'tasks.business.ingest_rccm',
    #     'schedule': crontab(hour=12, minute=0, day_of_month=1, month_of_year='1,4,7,10'),
    #     'kwargs': {
    #         'dataset_version_id': 9,
    #         'data_source_id': 9
    #     }
    # },

    # UNIDO/OECD - Annual
    # 'ingest-unido': {
    #     'task': 'tasks.business.ingest_unido',
    #     'schedule': crontab(hour=13, minute=0, day_of_month=1, month_of_year='1'),  # Every January
    #     'kwargs': {
    #         'dataset_version_id': 10,
    #         'data_source_id': 10,
    #         'country_code': 'BJ'
    #     }
    # },
}


# Celery configuration
timezone = 'UTC'
enable_utc = True

# Task result settings
result_expires = 3600  # Task results expire after 1 hour
result_backend_transport_options = {
    'master_name': 'mymaster',
}

# Task execution settings
task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'

# Task routing (optional - for task prioritization)
task_routes = {
    'tasks.scheduler.*': {'queue': 'scheduler'},
    'tasks.agriculture.*': {'queue': 'agriculture'},
    'tasks.realestate.*': {'queue': 'realestate'},
    'tasks.employment.*': {'queue': 'employment'},
    'tasks.business.*': {'queue': 'business'},
}

# Worker settings
worker_prefetch_multiplier = 1  # Only fetch one task at a time
worker_max_tasks_per_child = 100  # Restart worker after 100 tasks (memory management)

# Retry settings
task_acks_late = True  # Task is acked after execution, not before
task_reject_on_worker_lost = True  # Reject task if worker dies
