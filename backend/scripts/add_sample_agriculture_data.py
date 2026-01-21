"""
Script to add sample agriculture data for demonstration
Generates realistic production data for major communes and crops in Benin
"""
import sys
import os
import random
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app, db
from app.models.geo import Commune
from app.models.agriculture import Crop, AgriStats
from app.models.metadata import DataSource


def generate_realistic_data(crop_name, year, base_production):
    """
    Generate realistic agriculture statistics with some variance

    Args:
        crop_name: Name of the crop
        year: Year of data
        base_production: Base production amount

    Returns:
        Dictionary with agriculture statistics
    """
    # Add year-based trend (slight increase or decrease)
    year_factor = 1 + (year - 2020) * 0.03  # 3% growth per year

    # Add random variance (-10% to +15%)
    variance = random.uniform(0.9, 1.15)

    production = base_production * year_factor * variance

    # Calculate related metrics
    # Typical yields in Benin (tonnes per hectare)
    typical_yields = {
        "Maize": random.uniform(1.2, 2.5),
        "Rice": random.uniform(2.0, 4.0),
        "Cassava": random.uniform(8.0, 15.0),
        "Yam": random.uniform(10.0, 18.0),
        "Cotton": random.uniform(1.0, 1.5),
        "Pineapple": random.uniform(30.0, 50.0),
        "Cashew": random.uniform(0.4, 0.8),
        "Tomato": random.uniform(15.0, 25.0),
        "Beans": random.uniform(0.8, 1.5),
        "Groundnut": random.uniform(1.0, 1.8),
    }

    yield_per_ha = typical_yields.get(crop_name, 2.0) * random.uniform(0.9, 1.1)
    area_harvested = production / yield_per_ha if yield_per_ha > 0 else 0

    # Prices in XOF per kg (West African CFA franc)
    typical_prices = {
        "Maize": random.uniform(150, 250),
        "Rice": random.uniform(300, 500),
        "Cassava": random.uniform(80, 150),
        "Yam": random.uniform(200, 350),
        "Cotton": random.uniform(250, 400),
        "Pineapple": random.uniform(100, 200),
        "Cashew": random.uniform(500, 800),
        "Tomato": random.uniform(150, 300),
        "Beans": random.uniform(400, 600),
        "Groundnut": random.uniform(300, 500),
    }

    price_per_kg = typical_prices.get(crop_name, 200) * random.uniform(0.95, 1.05)

    # Data quality score (0.7 to 1.0 for realistic data)
    quality_score = random.uniform(0.85, 0.98)

    return {
        "production_tonnes": round(production, 2),
        "yield_tonnes_per_ha": round(yield_per_ha, 2),
        "area_harvested_ha": round(area_harvested, 2),
        "price_per_kg": round(price_per_kg, 2),
        "data_quality_score": round(quality_score, 2),
        "is_estimated": random.choice([False, False, False, True])  # 25% estimated
    }


def add_agriculture_data():
    """Add sample agriculture data for Benin"""
    print("Adding sample agriculture data...")

    # Get data source (use FAOSTAT as default source)
    fao_source = DataSource.query.filter_by(name="FAOSTAT").first()
    if not fao_source:
        print("⚠ FAOSTAT data source not found. Run seed_database.py first.")
        return

    # Get all communes
    communes = Commune.query.all()
    print(f"Found {len(communes)} communes")

    # Get strategic crops (first 3 as per MVP)
    strategic_crops = Crop.query.limit(3).all()
    if len(strategic_crops) < 3:
        print("⚠ Less than 3 crops found. Run seed_database.py first.")
        return

    print(f"Strategic crops: {', '.join(c.name for c in strategic_crops)}")

    # Get all crops for broader coverage
    all_crops = Crop.query.all()

    # Years to generate data for
    years = [2020, 2021, 2022, 2023]

    # Production levels by commune type (in tonnes)
    production_levels = {
        "major": 5000,    # Major cities
        "medium": 2000,   # Medium communes
        "small": 500      # Small communes
    }

    # Major agricultural communes in Benin
    major_communes = [
        "Abomey-Calavi", "Cotonou", "Porto-Novo", "Parakou",
        "Djougou", "Bohicon", "Kandi", "Natitingou", "Savalou"
    ]

    stats_added = 0

    for commune in communes:
        # Determine commune production level
        if commune.name in major_communes:
            level = "major"
        elif random.random() > 0.7:
            level = "medium"
        else:
            level = "small"

        base_production = production_levels[level]

        # For strategic crops, add data for all years
        for crop in strategic_crops:
            for year in years:
                # Check if data already exists
                existing = AgriStats.query.filter_by(
                    commune_id=commune.id,
                    crop_id=crop.id,
                    year=year
                ).first()

                if existing:
                    continue

                # Generate data
                data = generate_realistic_data(crop.name, year, base_production)

                # Create AgriStats entry
                stat = AgriStats(
                    commune_id=commune.id,
                    crop_id=crop.id,
                    year=year,
                    data_source_id=fao_source.id,
                    production_tonnes=data["production_tonnes"],
                    yield_tonnes_per_ha=data["yield_tonnes_per_ha"],
                    area_harvested_ha=data["area_harvested_ha"],
                    price_per_kg=data["price_per_kg"],
                    price_currency="XOF",
                    data_quality_score=data["data_quality_score"],
                    is_estimated=data["is_estimated"]
                )

                db.session.add(stat)
                stats_added += 1

        # For major communes, add some data for other crops too
        if level == "major" and len(all_crops) > 3:
            other_crops = [c for c in all_crops if c not in strategic_crops]
            selected_other_crops = random.sample(other_crops, min(3, len(other_crops)))

            for crop in selected_other_crops:
                # Only add data for recent years
                for year in [2022, 2023]:
                    existing = AgriStats.query.filter_by(
                        commune_id=commune.id,
                        crop_id=crop.id,
                        year=year
                    ).first()

                    if existing:
                        continue

                    data = generate_realistic_data(crop.name, year, base_production * 0.5)

                    stat = AgriStats(
                        commune_id=commune.id,
                        crop_id=crop.id,
                        year=year,
                        data_source_id=fao_source.id,
                        production_tonnes=data["production_tonnes"],
                        yield_tonnes_per_ha=data["yield_tonnes_per_ha"],
                        area_harvested_ha=data["area_harvested_ha"],
                        price_per_kg=data["price_per_kg"],
                        price_currency="XOF",
                        data_quality_score=data["data_quality_score"],
                        is_estimated=data["is_estimated"]
                    )

                    db.session.add(stat)
                    stats_added += 1

    # Commit all changes
    db.session.commit()

    print(f"\n✓ Added {stats_added} agriculture statistics entries")

    # Show summary
    total_stats = AgriStats.query.count()
    communes_with_data = db.session.query(AgriStats.commune_id).distinct().count()
    crops_with_data = db.session.query(AgriStats.crop_id).distinct().count()

    print(f"\nDatabase Summary:")
    print(f"  Total statistics: {total_stats}")
    print(f"  Communes with data: {communes_with_data}/{len(communes)}")
    print(f"  Crops with data: {crops_with_data}/{len(all_crops)}")
    print(f"  Years covered: {', '.join(map(str, years))}")


def main():
    """Main function"""
    print("=" * 60)
    print("TEDI Agriculture Data Generator")
    print("=" * 60)

    # Create Flask app context
    app = create_app('development')

    with app.app_context():
        add_agriculture_data()

        print("\n" + "=" * 60)
        print("✓ Agriculture data added successfully!")
        print("=" * 60)
        print("\nYou can now:")
        print("  1. Test the API: curl -H 'X-API-KEY: your-key' http://localhost:5000/api/v1/agriculture/index")
        print("  2. View in dashboard: http://localhost:3000/agriculture")
        print("  3. Check API docs: http://localhost:5000/api/docs")


if __name__ == '__main__':
    main()
