"""
Setup Script for Data Ingestion Scheduler

This script initializes the database with:
1. Data sources for all implemented connectors
2. Sample dataset versions with scheduling enabled

Usage:
    python setup_scheduler_data.py
"""
import sys
from datetime import datetime, timedelta, date
from app import create_app, db
from app.models import DataSource, DatasetVersion, Commune


def create_data_sources():
    """Create data source records for all implemented connectors"""
    print("\n" + "="*60)
    print("STEP 1: Creating Data Sources")
    print("="*60)

    data_sources = [
        {
            'name': 'FAOSTAT',
            'url': 'https://www.fao.org/faostat/',
            'organization': 'Food and Agriculture Organization',
            'source_type': 'external',
            'update_frequency': 'quarterly',
            'is_active': True,
            'description': 'FAO Statistics Database - Agricultural production data'
        },
        {
            'name': 'World Bank',
            'url': 'https://data.worldbank.org/',
            'organization': 'World Bank Group',
            'source_type': 'external',
            'update_frequency': 'annual',
            'is_active': True,
            'description': 'World Bank Development Indicators'
        },
        {
            'name': 'ILOSTAT',
            'url': 'https://ilostat.ilo.org/',
            'organization': 'International Labour Organization',
            'source_type': 'external',
            'update_frequency': 'annual',
            'is_active': True,
            'description': 'ILO Employment Statistics'
        },
        {
            'name': 'OpenStreetMap',
            'url': 'https://www.openstreetmap.org/',
            'organization': 'OpenStreetMap Foundation',
            'source_type': 'external',
            'update_frequency': 'monthly',
            'is_active': True,
            'description': 'Crowdsourced geographic data'
        },
    ]

    created_count = 0
    for source_data in data_sources:
        existing = DataSource.query.filter_by(name=source_data['name']).first()

        if existing:
            print(f"  ⏭️  {source_data['name']} already exists (ID: {existing.id})")
        else:
            source = DataSource(**source_data)
            db.session.add(source)
            created_count += 1
            print(f"  ✅ Created {source_data['name']}")

    db.session.commit()
    print(f"\n✅ Data sources setup complete: {created_count} new, {len(data_sources) - created_count} existing")

    return DataSource.query.all()


def create_datasets_and_versions(data_sources):
    """Create dataset versions with scheduling"""
    print("\n" + "="*60)
    print("STEP 2: Creating Dataset Versions")
    print("="*60)

    # Check if we have any communes
    commune = Commune.query.first()
    if not commune:
        print("  ⚠️  WARNING: No communes found in database")
        print("  ⚠️  You may need to run data generation scripts first")

    # Dataset versions config by source
    versions_config = [
        {'source': 'FAOSTAT', 'version_name': 'Agriculture Production Data'},
        {'source': 'World Bank', 'version_name': 'Agriculture Indicators'},
        {'source': 'World Bank', 'version_name': 'Employment Indicators'},
        {'source': 'World Bank', 'version_name': 'Business Indicators'},
        {'source': 'ILOSTAT', 'version_name': 'Employment Statistics'},
        {'source': 'OpenStreetMap', 'version_name': 'Geospatial Infrastructure'},
    ]

    version_count = 0
    today = date.today()

    for version_config in versions_config:
        source_name = version_config['source']
        version_name = version_config['version_name']

        # Find source
        source = next((s for s in data_sources if s.name == source_name), None)
        if not source:
            print(f"  ⚠️  Source not found: {source_name}")
            continue

        # Generate unique version string
        version_string = f'auto_{today.strftime("%Y%m%d")}_{version_name.lower().replace(" ", "_")}'

        # Check if version already exists
        existing_version = DatasetVersion.query.filter_by(
            data_source_id=source.id,
            version=version_string
        ).first()

        if existing_version:
            print(f"  ⏭️  Version exists: {source.name} - {version_name} (ID: {existing_version.id})")
            continue

        # Calculate next check time based on frequency
        next_check_at = datetime.utcnow() + timedelta(minutes=5)  # First check in 5 minutes

        # Create new version
        version = DatasetVersion(
            data_source_id=source.id,
            version=version_string,
            release_date=today,
            check_enabled=True,
            next_check_at=next_check_at,
            source_reliability_score=None,  # Will be calculated after first run
            consecutive_failures=0,
            processing_status='pending',
        )
        db.session.add(version)
        version_count += 1
        print(f"  ✅ Created version: {source.name} - {version_name}")
        print(f"     Next check: {next_check_at.strftime('%Y-%m-%d %H:%M:%S')} UTC")

    db.session.commit()
    print(f"\n✅ Dataset versions setup complete: {version_count} new versions created")


def display_summary():
    """Display summary of setup"""
    print("\n" + "="*60)
    print("SETUP SUMMARY")
    print("="*60)

    # Count data sources
    sources = DataSource.query.filter_by(is_active=True).all()
    print(f"\n📊 Active Data Sources: {len(sources)}")
    for source in sources:
        print(f"  • {source.name} ({source.update_frequency})")

    # Count enabled dataset versions
    versions = DatasetVersion.query.filter_by(check_enabled=True).all()
    print(f"\n📅 Enabled Dataset Versions: {len(versions)}")
    for version in versions:
        source = version.data_source
        print(f"  • {version.version} ← {source.name if source else 'Unknown'}")
        print(f"    Next check: {version.next_check_at.strftime('%Y-%m-%d %H:%M:%S') if version.next_check_at else 'Not scheduled'}")

    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("""
1. Start Redis (if not running):
   docker-compose up -d redis

2. Start Celery worker:
   docker exec -it tedi_backend celery -A celery_worker.celery_app worker --loglevel=info

3. Start Celery beat scheduler (in another terminal):
   docker exec -it tedi_backend celery -A celery_worker.celery_app beat --loglevel=info

4. OR start both together (for development):
   docker exec -it tedi_backend celery -A celery_worker.celery_app worker --beat --loglevel=info

5. Monitor logs:
   docker logs -f tedi_backend | grep "Scheduler"

6. Manual test (optional):
   docker exec -it tedi_backend python -c "from app.tasks.scheduler import check_and_schedule_ingestions; print(check_and_schedule_ingestions())"

7. View Flower monitoring (optional):
   pip install flower
   celery -A celery_worker.celery_app flower
   Open: http://localhost:5555
    """)


def main():
    """Main setup function"""
    print("\n" + "="*60)
    print("DATA INGESTION SCHEDULER - SETUP")
    print("="*60)
    print("\nThis script will set up data sources and dataset versions")
    print("for the automatic data ingestion scheduler.\n")

    # Create Flask app context
    app = create_app()

    with app.app_context():
        # Step 1: Create data sources
        data_sources = create_data_sources()

        # Step 2: Create datasets and versions
        create_datasets_and_versions(data_sources)

        # Step 3: Display summary
        display_summary()

    print("\n✅ Setup complete! The scheduler is ready to run.\n")
    return 0


if __name__ == '__main__':
    sys.exit(main())
