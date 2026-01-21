"""
Update existing agriculture data with labeling indices
"""
import sys
import os
import random

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import AgriStats, Crop, Commune

# Crop type mappings
CROP_TYPE_MAP = {
    'Maize': 'cereals',
    'Rice': 'cereals',
    'Cassava': 'tubers',
    'Yam': 'tubers',
    'Cotton': 'cash_crops',
    'Pineapple': 'fruits',
    'Cashew': 'cash_crops',
    'Tomato': 'vegetables',
    'Beans': 'legumes',
    'Groundnut': 'legumes'
}

# Geographic zones by region (Benin)
GEO_ZONE_MAP = {
    'Alibori': 'north',
    'Atacora': 'north',
    'Borgou': 'north',
    'Donga': 'north',
    'Collines': 'central',
    'Zou': 'central',
    'Plateau': 'central',
    'Littoral': 'coastal',
    'Atlantique': 'coastal',
    'Mono': 'coastal',
    'Couffo': 'coastal',
    'Ouémé': 'south'
}

def update_agriculture_indices():
    """Update existing agriculture statistics with labeling indices"""
    app = create_app()

    with app.app_context():
        print("🌾 Updating Agriculture Data with Labeling Indices...")

        # Get all crops for mapping
        crops = {crop.id: crop for crop in Crop.query.all()}

        # Get all communes with regions
        communes = {commune.id: commune for commune in Commune.query.join(Commune.region).all()}

        # Get all agri stats
        agri_stats = AgriStats.query.all()
        total = len(agri_stats)
        updated = 0

        print(f"📊 Found {total} agriculture statistics to update")

        for stat in agri_stats:
            # Get crop and commune
            crop = crops.get(stat.crop_id)
            commune = communes.get(stat.commune_id)

            if not crop or not commune:
                continue

            # 1. Crop Type
            stat.crop_type = CROP_TYPE_MAP.get(crop.name, 'other')

            # 2. Geographic Zone
            region_name = commune.region.name if commune.region else 'central'
            stat.geo_zone = GEO_ZONE_MAP.get(region_name, 'central')

            # 3. Climate Risk Level (based on zone and randomness)
            if stat.geo_zone == 'north':
                stat.climate_risk_level = random.choices(['medium', 'high'], weights=[0.6, 0.4])[0]
            elif stat.geo_zone == 'coastal':
                stat.climate_risk_level = random.choices(['low', 'medium'], weights=[0.5, 0.5])[0]
            else:
                stat.climate_risk_level = random.choices(['low', 'medium', 'high'], weights=[0.4, 0.5, 0.1])[0]

            # 4. Soil Quality Index (60-95)
            # Better soil in south/coastal, variable in north
            if stat.geo_zone in ['south', 'coastal']:
                stat.soil_quality_index = random.uniform(70, 95)
            elif stat.geo_zone == 'central':
                stat.soil_quality_index = random.uniform(65, 85)
            else:  # north
                stat.soil_quality_index = random.uniform(60, 80)

            # 5. Yield Estimation Class (based on actual yield if available)
            if stat.yield_tonnes_per_ha:
                # Get typical yield for crop
                typical_yields = {
                    'cereals': 2.0,
                    'tubers': 10.0,
                    'cash_crops': 1.5,
                    'legumes': 1.0,
                    'vegetables': 15.0,
                    'fruits': 20.0
                }
                typical = typical_yields.get(stat.crop_type, 5.0)

                if stat.yield_tonnes_per_ha < typical * 0.7:
                    stat.yield_estimation_class = 'low'
                elif stat.yield_tonnes_per_ha > typical * 1.3:
                    stat.yield_estimation_class = 'high'
                else:
                    stat.yield_estimation_class = 'medium'
            else:
                stat.yield_estimation_class = random.choice(['low', 'medium', 'high'])

            # 6. Price Volatility Index (20-80)
            # Cash crops more volatile
            if stat.crop_type == 'cash_crops':
                stat.price_volatility_index = random.uniform(50, 80)
            elif stat.crop_type in ['cereals', 'tubers']:
                stat.price_volatility_index = random.uniform(30, 60)
            else:
                stat.price_volatility_index = random.uniform(20, 50)

            # 7. Mechanization Level
            # More mechanized in larger communes and for cereals/cash crops
            population = commune.population if commune.population else 50000

            if population > 100000 and stat.crop_type in ['cereals', 'cash_crops']:
                stat.mechanization_level = random.choices(
                    ['semi_mechanized', 'mechanized'],
                    weights=[0.6, 0.4]
                )[0]
            elif population > 50000:
                stat.mechanization_level = random.choices(
                    ['manual', 'semi_mechanized'],
                    weights=[0.4, 0.6]
                )[0]
            else:
                stat.mechanization_level = random.choices(
                    ['manual', 'semi_mechanized'],
                    weights=[0.7, 0.3]
                )[0]

            updated += 1

            if updated % 100 == 0:
                print(f"  ⏳ Progress: {updated}/{total} ({updated*100//total}%)")

        # Commit all changes
        db.session.commit()

        print(f"\n✅ Agriculture indices updated successfully!")
        print(f"📊 Total updated: {updated}/{total}")

        # Show sample
        sample = AgriStats.query.first()
        if sample:
            print(f"\n📋 Sample updated record:")
            print(f"   Crop Type: {sample.crop_type}")
            print(f"   Geo Zone: {sample.geo_zone}")
            print(f"   Climate Risk: {sample.climate_risk_level}")
            print(f"   Soil Quality: {sample.soil_quality_index:.1f}")
            print(f"   Yield Class: {sample.yield_estimation_class}")
            print(f"   Price Volatility: {sample.price_volatility_index:.1f}")
            print(f"   Mechanization: {sample.mechanization_level}")

if __name__ == '__main__':
    update_agriculture_indices()
