"""
Seed property types for Real Estate vertical
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import PropertyType

def seed_property_types():
    """Seed property types"""
    app = create_app()

    with app.app_context():
        print("🏠 Seeding Property Types...")

        property_types = [
            {
                'name': 'Residential',
                'name_fr': 'Résidentiel',
                'description': 'Residential properties including houses, apartments, condos',
                'category': 'residential'
            },
            {
                'name': 'Commercial',
                'name_fr': 'Commercial',
                'description': 'Commercial properties including shops, offices, malls',
                'category': 'commercial'
            },
            {
                'name': 'Agricultural Land',
                'name_fr': 'Terrain Agricole',
                'description': 'Agricultural land for farming, livestock, plantations',
                'category': 'agricultural'
            },
            {
                'name': 'Industrial',
                'name_fr': 'Industriel',
                'description': 'Industrial properties including factories, warehouses, workshops',
                'category': 'industrial'
            },
            {
                'name': 'Mixed Use',
                'name_fr': 'Usage Mixte',
                'description': 'Mixed-use properties combining residential and commercial',
                'category': 'mixed'
            },
            {
                'name': 'Vacant Land',
                'name_fr': 'Terrain Nu',
                'description': 'Undeveloped land for future development',
                'category': 'land'
            }
        ]

        created_count = 0
        for pt_data in property_types:
            # Check if already exists
            existing = PropertyType.query.filter_by(name=pt_data['name']).first()
            if not existing:
                pt = PropertyType(**pt_data)
                db.session.add(pt)
                created_count += 1
                print(f"  ✅ Created: {pt_data['name']}")
            else:
                print(f"  ⏭️  Exists: {pt_data['name']}")

        db.session.commit()

        total = PropertyType.query.count()
        print(f"\n✅ Property Types seeded successfully!")
        print(f"📊 Total property types: {total}")
        print(f"🆕 Newly created: {created_count}")

if __name__ == '__main__':
    seed_property_types()
