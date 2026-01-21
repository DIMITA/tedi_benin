"""
Seed job categories for Employment vertical
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import JobCategory

def seed_job_categories():
    """Seed job categories"""
    app = create_app()

    with app.app_context():
        print("💼 Seeding Job Categories...")

        job_categories = [
            {
                'name': 'Agriculture & Fishing',
                'name_fr': 'Agriculture & Pêche',
                'description': 'Farming, livestock, fishing, forestry',
                'sector': 'primary'
            },
            {
                'name': 'Manufacturing',
                'name_fr': 'Industrie Manufacturière',
                'description': 'Production, assembly, processing industries',
                'sector': 'secondary'
            },
            {
                'name': 'Construction',
                'name_fr': 'Construction',
                'description': 'Building, infrastructure, civil engineering',
                'sector': 'secondary'
            },
            {
                'name': 'Retail & Wholesale Trade',
                'name_fr': 'Commerce',
                'description': 'Shops, markets, wholesalers, street vendors',
                'sector': 'tertiary'
            },
            {
                'name': 'Transportation',
                'name_fr': 'Transport',
                'description': 'Taxi, moto-taxi, logistics, delivery',
                'sector': 'tertiary'
            },
            {
                'name': 'Hospitality & Food Services',
                'name_fr': 'Hôtellerie & Restauration',
                'description': 'Hotels, restaurants, cafes, catering',
                'sector': 'tertiary'
            },
            {
                'name': 'Education',
                'name_fr': 'Éducation',
                'description': 'Teachers, trainers, tutors, education administrators',
                'sector': 'tertiary'
            },
            {
                'name': 'Healthcare',
                'name_fr': 'Santé',
                'description': 'Doctors, nurses, pharmacists, healthcare workers',
                'sector': 'tertiary'
            },
            {
                'name': 'Financial Services',
                'name_fr': 'Services Financiers',
                'description': 'Banking, insurance, microfinance, mobile money',
                'sector': 'tertiary'
            },
            {
                'name': 'IT & Telecommunications',
                'name_fr': 'IT & Télécommunications',
                'description': 'Software, tech support, telecom services',
                'sector': 'tertiary'
            },
            {
                'name': 'Public Administration',
                'name_fr': 'Administration Publique',
                'description': 'Government, civil service, public sector',
                'sector': 'tertiary'
            },
            {
                'name': 'Professional Services',
                'name_fr': 'Services Professionnels',
                'description': 'Law, accounting, consulting, engineering',
                'sector': 'tertiary'
            },
            {
                'name': 'Personal Services',
                'name_fr': 'Services Personnels',
                'description': 'Hairdressing, tailoring, repair services, domestic work',
                'sector': 'tertiary'
            },
            {
                'name': 'Arts & Entertainment',
                'name_fr': 'Arts & Divertissement',
                'description': 'Artists, musicians, entertainment, media',
                'sector': 'tertiary'
            }
        ]

        created_count = 0
        for jc_data in job_categories:
            # Check if already exists
            existing = JobCategory.query.filter_by(name=jc_data['name']).first()
            if not existing:
                jc = JobCategory(**jc_data)
                db.session.add(jc)
                created_count += 1
                print(f"  ✅ Created: {jc_data['name']}")
            else:
                print(f"  ⏭️  Exists: {jc_data['name']}")

        db.session.commit()

        total = JobCategory.query.count()
        print(f"\n✅ Job Categories seeded successfully!")
        print(f"📊 Total job categories: {total}")
        print(f"🆕 Newly created: {created_count}")

if __name__ == '__main__':
    seed_job_categories()
