"""
Database seeding script for TEDI
Initializes database with Benin geographical data and crops
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app, db
from app.models.geo import Country, Region, Commune
from app.models.agriculture import Crop
from app.models.metadata import DataSource
from app.models.auth import ApiKey


def seed_countries():
    """Seed countries table"""
    print("Seeding countries...")

    benin = Country(
        name="Bénin",
        iso_code="BEN",
        iso_code_2="BJ"
    )

    db.session.add(benin)
    db.session.commit()

    print(f"✓ Added country: {benin.name}")
    return benin


def seed_regions(country):
    """Seed regions/departments of Benin"""
    print("\nSeeding regions...")

    regions_data = [
        "Alibori", "Atacora", "Atlantique", "Borgou",
        "Collines", "Couffo", "Donga", "Littoral",
        "Mono", "Ouémé", "Plateau", "Zou"
    ]

    regions = []
    for region_name in regions_data:
        region = Region(
            name=region_name,
            country_id=country.id
        )
        regions.append(region)
        db.session.add(region)

    db.session.commit()

    print(f"✓ Added {len(regions)} regions")
    return regions


def seed_communes(regions):
    """Seed communes for major regions"""
    print("\nSeeding communes...")

    # Sample communes for each region (simplified for MVP)
    communes_data = {
        "Atlantique": ["Abomey-Calavi", "Allada", "Kpomassè", "Ouidah", "Sô-Ava", "Toffo", "Tori-Bossito", "Zè"],
        "Littoral": ["Cotonou"],
        "Ouémé": ["Porto-Novo", "Adjarra", "Adjohoun", "Aguégués", "Akpro-Missérété", "Avrankou", "Bonou", "Dangbo", "Sèmè-Kpodji"],
        "Zou": ["Abomey", "Agbangnizoun", "Bohicon", "Cové", "Djidja", "Ouinhi", "Za-Kpota", "Zangnanado", "Zogbodomey"],
        "Borgou": ["Parakou", "Bembèrèkè", "Kalalé", "N'Dali", "Nikki", "Pèrèrè", "Sinendé", "Tchaourou"],
        "Alibori": ["Kandi", "Banikoara", "Gogounou", "Karimama", "Malanville", "Ségbana"],
        "Atacora": ["Natitingou", "Boukoumbé", "Cobly", "Kérou", "Kouandé", "Matéri", "Péhunco", "Tanguiéta", "Toucountouna"],
        "Donga": ["Djougou", "Bassila", "Copargo", "Ouaké"],
        "Collines": ["Savalou", "Bantè", "Dassa-Zoumè", "Glazoué", "Ouèssè", "Savè"],
        "Mono": ["Lokossa", "Athiémé", "Bopa", "Comè", "Grand-Popo", "Houéyogbé"],
        "Couffo": ["Aplahoué", "Djakotomey", "Dogbo", "Klouékanmè", "Lalo", "Toviklin"],
        "Plateau": ["Pobè", "Adja-Ouèrè", "Ifangni", "Kétou", "Sakété"]
    }

    region_map = {r.name: r for r in regions}
    commune_count = 0

    for region_name, commune_names in communes_data.items():
        if region_name in region_map:
            region = region_map[region_name]

            for commune_name in commune_names:
                commune = Commune(
                    name=commune_name,
                    region_id=region.id
                )
                db.session.add(commune)
                commune_count += 1

    db.session.commit()

    print(f"✓ Added {commune_count} communes")


def seed_crops():
    """Seed crops table with strategic crops for MVP"""
    print("\nSeeding crops...")

    crops_data = [
        # Strategic crops for MVP (3 crops as per MVP scope)
        {"name": "Maize", "name_fr": "Maïs", "category": "cereals", "fao_code": "56"},
        {"name": "Rice", "name_fr": "Riz", "category": "cereals", "fao_code": "27"},
        {"name": "Cassava", "name_fr": "Manioc", "category": "tubers", "fao_code": "125"},

        # Additional crops for completeness
        {"name": "Yam", "name_fr": "Igname", "category": "tubers", "fao_code": "136"},
        {"name": "Cotton", "name_fr": "Coton", "category": "fiber", "fao_code": "328"},
        {"name": "Pineapple", "name_fr": "Ananas", "category": "fruits", "fao_code": "574"},
        {"name": "Cashew", "name_fr": "Anacarde", "category": "nuts", "fao_code": "217"},
        {"name": "Tomato", "name_fr": "Tomate", "category": "vegetables", "fao_code": "388"},
        {"name": "Beans", "name_fr": "Haricots", "category": "legumes", "fao_code": "176"},
        {"name": "Groundnut", "name_fr": "Arachide", "category": "legumes", "fao_code": "242"},
    ]

    for crop_data in crops_data:
        crop = Crop(**crop_data)
        db.session.add(crop)

    db.session.commit()

    print(f"✓ Added {len(crops_data)} crops")


def seed_data_sources():
    """Seed data sources"""
    print("\nSeeding data sources...")

    sources_data = [
        {
            "name": "FAOSTAT",
            "url": "https://www.fao.org/faostat/en/",
            "description": "Food and Agriculture Organization Statistical Database",
            "license": "CC BY-NC-SA 3.0 IGO",
            "organization": "FAO",
            "source_type": "external"
        },
        {
            "name": "World Bank Agriculture",
            "url": "https://data.worldbank.org/topic/agriculture",
            "description": "World Bank Agriculture & Rural Development Data",
            "license": "CC BY 4.0",
            "organization": "World Bank",
            "source_type": "external"
        },
        {
            "name": "INStaD Benin",
            "url": "https://instad.bj/",
            "description": "Institut National de la Statistique et de la Démographie du Bénin",
            "license": "Open Data",
            "organization": "INStaD",
            "source_type": "external"
        },
        {
            "name": "data.gouv.bj",
            "url": "https://data.gouv.bj/",
            "description": "Portail Open Data du Bénin",
            "license": "Open Data",
            "organization": "Government of Benin",
            "source_type": "external"
        }
    ]

    for source_data in sources_data:
        source = DataSource(**source_data)
        db.session.add(source)

    db.session.commit()

    print(f"✓ Added {len(sources_data)} data sources")


def seed_api_keys():
    """Seed demo API keys"""
    print("\nSeeding demo API keys...")

    # Create a demo API key for testing
    demo_key = ApiKey.create_key(
        name="Demo API Key",
        owner_name="Demo User",
        owner_email="demo@tedi.africa",
        owner_organization="TEDI",
        expires_in_days=None,  # Never expires
        scopes=["*"]  # All permissions
    )

    db.session.add(demo_key)
    db.session.commit()

    print(f"✓ Created demo API key: {demo_key.key}")
    print(f"  Email: demo@tedi.africa")
    print(f"  Scopes: * (all)")


def main():
    """Main seeding function"""
    print("=" * 60)
    print("TEDI Database Seeding Script")
    print("=" * 60)

    # Create Flask app context
    app = create_app('development')

    with app.app_context():
        # Drop all tables and recreate
        print("\nDropping existing tables...")
        db.drop_all()

        print("Creating tables...")
        db.create_all()

        # Seed data
        country = seed_countries()
        regions = seed_regions(country)
        seed_communes(regions)
        seed_crops()
        seed_data_sources()
        seed_api_keys()

        print("\n" + "=" * 60)
        print("✓ Database seeded successfully!")
        print("=" * 60)


if __name__ == '__main__':
    main()
