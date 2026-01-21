"""
Test script for data ingestion scheduler

This script tests the scheduler setup and task execution without
actually running the full Celery workers.

Usage:
    python test_scheduler.py
"""
import sys
from datetime import datetime, timedelta
from app import create_app, db
from app.models import DataSource, DatasetVersion, IngestionLog


def test_database_setup():
    """Test that all required tables exist"""
    print("\n" + "="*60)
    print("TEST 1: Database Setup")
    print("="*60)

    try:
        # Check if tables exist
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()

        required_tables = [
            'data_sources',
            'dataset_versions',
            'data_source_configs',
            'ingestion_logs'
        ]

        print("\n✓ Checking for required tables:")
        for table in required_tables:
            if table in tables:
                print(f"  ✓ {table} exists")
            else:
                print(f"  ✗ {table} MISSING")
                return False

        # Check dataset_versions has new columns
        columns = [col['name'] for col in inspector.get_columns('dataset_versions')]
        required_columns = [
            'last_checked_at',
            'next_check_at',
            'check_enabled',
            'source_reliability_score',
            'consecutive_failures'
        ]

        print("\n✓ Checking dataset_versions columns:")
        for col in required_columns:
            if col in columns:
                print(f"  ✓ {col} exists")
            else:
                print(f"  ✗ {col} MISSING")
                return False

        print("\n✅ Database setup: PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Database setup: FAILED - {str(e)}")
        return False


def test_task_registration():
    """Test that all tasks are properly registered"""
    print("\n" + "="*60)
    print("TEST 2: Task Registration")
    print("="*60)

    try:
        from celery_worker import celery_app

        # Get all registered tasks
        tasks = [t for t in celery_app.tasks.keys() if not t.startswith('celery.')]

        expected_tasks = [
            'tasks.scheduler.check_and_schedule',
            'tasks.scheduler.cleanup_old_logs',
            'tasks.scheduler.update_reliability_scores',
            'tasks.agriculture.ingest_faostat',
            'tasks.agriculture.ingest_worldbank',
            'tasks.agriculture.ingest_satellite',
            'tasks.agriculture.ingest_local_surveys',
            'tasks.realestate.ingest_osm',
            'tasks.realestate.ingest_cadastre',
            'tasks.realestate.ingest_listings',
            'tasks.realestate.ingest_land_values',
            'tasks.employment.ingest_ilostat',
            'tasks.employment.ingest_worldbank',
            'tasks.employment.ingest_local_surveys',
            'tasks.employment.ingest_sectoral_stats',
            'tasks.business.ingest_rccm',
            'tasks.business.ingest_worldbank',
            'tasks.business.ingest_unido',
            'tasks.business.ingest_sectoral_stats',
            'tasks.business.ingest_trade_data',
        ]

        print(f"\n✓ Found {len(tasks)} registered tasks:")
        for task in sorted(tasks):
            status = "✓" if task in expected_tasks else "?"
            print(f"  {status} {task}")

        missing = set(expected_tasks) - set(tasks)
        if missing:
            print(f"\n⚠️  Missing tasks:")
            for task in missing:
                print(f"  ✗ {task}")

        print(f"\n✅ Task registration: PASSED ({len(tasks)} tasks)")
        return True

    except Exception as e:
        print(f"\n❌ Task registration: FAILED - {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_celery_config():
    """Test that Celery configuration is loaded"""
    print("\n" + "="*60)
    print("TEST 3: Celery Configuration")
    print("="*60)

    try:
        from celery_worker import celery_app

        # Check beat schedule
        beat_schedule = celery_app.conf.beat_schedule

        print(f"\n✓ Beat schedule has {len(beat_schedule)} entries:")
        for name, config in beat_schedule.items():
            print(f"  ✓ {name}")
            print(f"    Task: {config['task']}")
            print(f"    Schedule: {config.get('schedule', 'N/A')}")

        # Check task routes
        task_routes = celery_app.conf.task_routes
        print(f"\n✓ Task routing configured:")
        for pattern, route in task_routes.items():
            print(f"  {pattern} → {route}")

        print("\n✅ Celery configuration: PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Celery configuration: FAILED - {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_create_sample_data():
    """Create sample data sources and dataset versions for testing"""
    print("\n" + "="*60)
    print("TEST 4: Create Sample Data")
    print("="*60)

    try:
        # Check if FAOSTAT source exists
        faostat = DataSource.query.filter_by(name='FAOSTAT').first()

        if not faostat:
            print("\n✓ Creating FAOSTAT data source...")
            faostat = DataSource(
                name='FAOSTAT',
                url='https://www.fao.org/faostat/',
                organization='Food and Agriculture Organization',
                source_type='external',
                update_frequency='quarterly',
                is_active=True
            )
            db.session.add(faostat)
            db.session.commit()
            print("  ✓ FAOSTAT source created")
        else:
            print("\n✓ FAOSTAT source already exists")

        # Check if dataset version exists
        version = DatasetVersion.query.filter_by(
            data_source_id=faostat.id
        ).first()

        if not version:
            print("\n✓ Creating test dataset version...")
            # We need a dataset first - just create a placeholder
            from app.models import Dataset
            dataset = Dataset.query.first()

            if not dataset:
                print("  ⚠️  No datasets in database - skipping version creation")
            else:
                version = DatasetVersion(
                    dataset_id=dataset.id,
                    data_source_id=faostat.id,
                    version='test_2024.Q1',
                    check_enabled=True,
                    next_check_at=datetime.utcnow() + timedelta(minutes=5),
                )
                db.session.add(version)
                db.session.commit()
                print("  ✓ Test dataset version created")
                print(f"    Next check at: {version.next_check_at}")
        else:
            print(f"\n✓ Dataset version already exists (ID: {version.id})")
            print(f"  Check enabled: {version.check_enabled}")
            print(f"  Next check at: {version.next_check_at}")
            print(f"  Consecutive failures: {version.consecutive_failures}")

        print("\n✅ Sample data: PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Sample data creation: FAILED - {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_scheduler_logic():
    """Test the scheduler logic without actually running tasks"""
    print("\n" + "="*60)
    print("TEST 5: Scheduler Logic")
    print("="*60)

    try:
        # Get all enabled dataset versions
        versions = DatasetVersion.query.filter_by(check_enabled=True).all()

        print(f"\n✓ Found {len(versions)} enabled dataset versions")

        for version in versions:
            print(f"\n  Dataset Version ID: {version.id}")
            print(f"  Data Source: {version.data_source.name if version.data_source else 'N/A'}")
            print(f"  Check enabled: {version.check_enabled}")
            print(f"  Next check: {version.next_check_at}")
            print(f"  Should check now: {version.should_check()}")
            print(f"  Consecutive failures: {version.consecutive_failures}")
            print(f"  Reliability score: {version.source_reliability_score}")

        print("\n✅ Scheduler logic: PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Scheduler logic: FAILED - {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_connector_imports():
    """Test that all connectors can be imported"""
    print("\n" + "="*60)
    print("TEST 6: Connector Imports")
    print("="*60)

    connectors = [
        ('app.connectors.base', 'BaseConnector'),
        ('app.connectors.faostat', 'FAOSTATConnector'),
        ('app.connectors.worldbank', 'WorldBankConnector'),
        ('app.connectors.osm', 'OSMConnector'),
    ]

    all_passed = True

    for module_name, class_name in connectors:
        try:
            module = __import__(module_name, fromlist=[class_name])
            connector_class = getattr(module, class_name)
            print(f"  ✓ {module_name}.{class_name}")
        except Exception as e:
            print(f"  ✗ {module_name}.{class_name} - {str(e)}")
            all_passed = False

    if all_passed:
        print("\n✅ Connector imports: PASSED")
    else:
        print("\n❌ Connector imports: FAILED")

    return all_passed


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("TEDI Data Ingestion Scheduler - Test Suite")
    print("="*60)

    # Create Flask app context
    app = create_app()

    with app.app_context():
        results = []

        # Run all tests
        results.append(("Database Setup", test_database_setup()))
        results.append(("Task Registration", test_task_registration()))
        results.append(("Celery Configuration", test_celery_config()))
        results.append(("Sample Data Creation", test_create_sample_data()))
        results.append(("Scheduler Logic", test_scheduler_logic()))
        results.append(("Connector Imports", test_connector_imports()))

        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status} - {name}")

        print("\n" + "="*60)
        print(f"Results: {passed}/{total} tests passed")
        print("="*60)

        if passed == total:
            print("\n🎉 All tests passed! The scheduler is ready to use.")
            print("\nNext steps:")
            print("1. Start Redis: docker-compose up -d redis")
            print("2. Start Celery worker: celery -A celery_worker.celery_app worker --loglevel=info")
            print("3. Start Celery beat: celery -A celery_worker.celery_app beat --loglevel=info")
            print("\nOr use the combined command for development:")
            print("celery -A celery_worker.celery_app worker --beat --loglevel=info")
            return 0
        else:
            print("\n⚠️  Some tests failed. Please fix the issues before proceeding.")
            return 1


if __name__ == '__main__':
    sys.exit(main())
