"""
Seed business sectors for Business vertical
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import BusinessSector

def seed_business_sectors():
    """Seed business sectors"""
    app = create_app()

    with app.app_context():
        print("🏢 Seeding Business Sectors...")

        business_sectors = [
            {
                'name': 'Agriculture & Agribusiness',
                'name_fr': 'Agriculture & Agrobusiness',
                'description': 'Farming, livestock, agricultural inputs, processing',
                'category': 'primary'
            },
            {
                'name': 'Food & Beverage',
                'name_fr': 'Alimentation & Boissons',
                'description': 'Food processing, beverages, packaged goods',
                'category': 'secondary'
            },
            {
                'name': 'Textiles & Apparel',
                'name_fr': 'Textile & Habillement',
                'description': 'Clothing, fabrics, tailoring, fashion',
                'category': 'secondary'
            },
            {
                'name': 'Construction & Building Materials',
                'name_fr': 'Construction & Matériaux',
                'description': 'Construction companies, cement, hardware',
                'category': 'secondary'
            },
            {
                'name': 'Retail',
                'name_fr': 'Commerce de Détail',
                'description': 'Shops, supermarkets, boutiques, e-commerce',
                'category': 'tertiary'
            },
            {
                'name': 'Wholesale Trade',
                'name_fr': 'Commerce de Gros',
                'description': 'Wholesalers, distributors, importers',
                'category': 'tertiary'
            },
            {
                'name': 'Transportation & Logistics',
                'name_fr': 'Transport & Logistique',
                'description': 'Freight, delivery, courier services, warehousing',
                'category': 'tertiary'
            },
            {
                'name': 'Hospitality & Tourism',
                'name_fr': 'Hôtellerie & Tourisme',
                'description': 'Hotels, restaurants, travel agencies, tourism',
                'category': 'tertiary'
            },
            {
                'name': 'Financial Services',
                'name_fr': 'Services Financiers',
                'description': 'Banks, insurance, microfinance, fintech',
                'category': 'tertiary'
            },
            {
                'name': 'Real Estate',
                'name_fr': 'Immobilier',
                'description': 'Property development, agencies, management',
                'category': 'tertiary'
            },
            {
                'name': 'Technology & Telecom',
                'name_fr': 'Technologie & Télécom',
                'description': 'Software, IT services, telecom, startups',
                'category': 'tertiary'
            },
            {
                'name': 'Professional Services',
                'name_fr': 'Services Professionnels',
                'description': 'Legal, accounting, consulting, architecture',
                'category': 'tertiary'
            },
            {
                'name': 'Healthcare Services',
                'name_fr': 'Services de Santé',
                'description': 'Clinics, pharmacies, medical equipment',
                'category': 'tertiary'
            },
            {
                'name': 'Education Services',
                'name_fr': 'Services Éducatifs',
                'description': 'Private schools, training centers, tutoring',
                'category': 'tertiary'
            },
            {
                'name': 'Energy & Utilities',
                'name_fr': 'Énergie & Services Publics',
                'description': 'Solar, electricity, water, waste management',
                'category': 'secondary'
            },
            {
                'name': 'Manufacturing',
                'name_fr': 'Industrie Manufacturière',
                'description': 'General manufacturing, assembly, production',
                'category': 'secondary'
            },
            {
                'name': 'Personal Services',
                'name_fr': 'Services Personnels',
                'description': 'Salons, beauty, repair services, laundry',
                'category': 'tertiary'
            },
            {
                'name': 'Media & Entertainment',
                'name_fr': 'Médias & Divertissement',
                'description': 'TV, radio, publishing, events, music',
                'category': 'tertiary'
            }
        ]

        created_count = 0
        for bs_data in business_sectors:
            # Check if already exists
            existing = BusinessSector.query.filter_by(name=bs_data['name']).first()
            if not existing:
                bs = BusinessSector(**bs_data)
                db.session.add(bs)
                created_count += 1
                print(f"  ✅ Created: {bs_data['name']}")
            else:
                print(f"  ⏭️  Exists: {bs_data['name']}")

        db.session.commit()

        total = BusinessSector.query.count()
        print(f"\n✅ Business Sectors seeded successfully!")
        print(f"📊 Total business sectors: {total}")
        print(f"🆕 Newly created: {created_count}")

if __name__ == '__main__':
    seed_business_sectors()
