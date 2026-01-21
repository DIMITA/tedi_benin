"""
Generate realistic real estate data with multi-source validation
"""
import sys
import os
import random
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Commune, PropertyType, RealEstateStats, RealEstateSourceContribution, DataSource
from app.utils.data_quality import MultiSourceQualityScorer

# Price ranges by property type (XOF per sqm)
PRICE_RANGES = {
    'residential': (50000, 250000),   # Residential
    'commercial': (100000, 500000),   # Commercial
    'agricultural': (10000, 50000),    # Agricultural land
    'industrial': (75000, 300000),    # Industrial
    'mixed': (80000, 350000),         # Mixed use
    'land': (20000, 150000)           # Vacant land
}

# Geographic zone modifiers
GEO_ZONE_PRICE_MULTIPLIERS = {
    'urban': 1.5,
    'peri_urban': 1.0,
    'rural': 0.6
}

def get_geo_zone(commune):
    """Determine geographic zone based on commune"""
    urban_communes = ['Cotonou', 'Porto-Novo', 'Parakou', 'Abomey-Calavi', 'Djougou']
    peri_urban = ['Bohicon', 'Lokossa', 'Natitingou', 'Kandi', 'Savalou']

    if commune.name in urban_communes:
        return 'urban'
    elif commune.name in peri_urban:
        return 'peri_urban'
    else:
        return 'rural'

def generate_multi_source_values(base_value, num_sources=3):
    """Generate values from multiple sources with realistic variance"""
    sources = []

    for i in range(num_sources):
        # Add variance: ±5-15%
        variance = random.uniform(-0.15, 0.15)
        source_value = base_value * (1 + variance)

        # Confidence score (higher for established sources)
        confidence = random.uniform(0.75, 0.95) if i < 2 else random.uniform(0.65, 0.85)

        # Weight (first source gets highest weight)
        weight = 1.0 if i == 0 else random.uniform(0.7, 0.9)

        sources.append({
            'value': source_value,
            'confidence': confidence,
            'weight': weight
        })

    return sources

def calculate_indices(property_type_category, geo_zone, price_per_sqm, commune_population):
    """Calculate all labeling indices for real estate"""

    # Price per sqm index (0-100, normalized)
    max_price = 500000  # Max expected price in XOF
    price_per_sqm_index = min((price_per_sqm / max_price) * 100, 100)

    # Price trend (based on random but weighted)
    trends = ['decreasing', 'stable', 'increasing', 'increasing_strong']
    if geo_zone == 'urban':
        price_trend = random.choices(trends, weights=[0.05, 0.15, 0.50, 0.30])[0]
    elif geo_zone == 'peri_urban':
        price_trend = random.choices(trends, weights=[0.10, 0.30, 0.45, 0.15])[0]
    else:  # rural
        price_trend = random.choices(trends, weights=[0.15, 0.50, 0.30, 0.05])[0]

    # Land risk level
    if geo_zone == 'urban' and property_type_category in ['residential', 'commercial']:
        land_risk_level = random.choices(['low', 'medium', 'high'], weights=[0.60, 0.30, 0.10])[0]
    elif geo_zone == 'rural':
        land_risk_level = random.choices(['low', 'medium', 'high'], weights=[0.20, 0.40, 0.40])[0]
    else:
        land_risk_level = random.choices(['low', 'medium', 'high'], weights=[0.40, 0.40, 0.20])[0]

    # Infrastructure score (0-100)
    if geo_zone == 'urban':
        infrastructure_score = random.uniform(65, 95)
    elif geo_zone == 'peri_urban':
        infrastructure_score = random.uniform(45, 75)
    else:
        infrastructure_score = random.uniform(25, 55)

    # Legal clarity index (0-100)
    if property_type_category in ['residential', 'commercial'] and geo_zone == 'urban':
        legal_clarity_index = random.uniform(70, 95)
    else:
        legal_clarity_index = random.uniform(40, 80)

    # Development potential
    if geo_zone == 'peri_urban':
        development_potential = random.choices(
            ['low', 'medium', 'high', 'very_high'],
            weights=[0.10, 0.25, 0.45, 0.20]
        )[0]
    elif geo_zone == 'urban':
        development_potential = random.choices(
            ['low', 'medium', 'high', 'very_high'],
            weights=[0.30, 0.40, 0.25, 0.05]
        )[0]
    else:
        development_potential = random.choices(
            ['low', 'medium', 'high', 'very_high'],
            weights=[0.40, 0.35, 0.20, 0.05]
        )[0]

    return {
        'geo_zone': geo_zone,
        'price_per_sqm_index': price_per_sqm_index,
        'price_trend': price_trend,
        'land_risk_level': land_risk_level,
        'infrastructure_score': infrastructure_score,
        'legal_clarity_index': legal_clarity_index,
        'development_potential': development_potential
    }

def generate_realestate_data():
    """Generate realistic real estate statistics with multi-source validation"""
    app = create_app()

    with app.app_context():
        print("🏠 Generating Real Estate Data with Multi-Source Validation...")

        # Get all necessary data
        communes = Commune.query.all()
        property_types = PropertyType.query.all()
        data_sources = DataSource.query.all()

        if len(data_sources) < 3:
            print("⚠️  Need at least 3 data sources. Found:", len(data_sources))
            return

        print(f"📊 Found {len(communes)} communes and {len(property_types)} property types")

        years = [2021, 2022, 2023]
        created_count = 0
        contribution_count = 0

        # Generate data for major communes (top 30 by population or importance)
        major_communes = sorted(
            [c for c in communes if c.population],
            key=lambda x: x.population if x.population else 0,
            reverse=True
        )[:30]

        # Also include communes with GPS coordinates
        gps_communes = [c for c in communes if c.center_lat and c.center_lon]
        target_communes = list(set(major_communes + gps_communes))[:35]

        print(f"🎯 Generating data for {len(target_communes)} communes")

        for commune in target_communes:
            geo_zone = get_geo_zone(commune)

            # Not all property types in all communes
            # Urban: all types, Rural: mainly agricultural + residential
            if geo_zone == 'rural':
                relevant_types = [pt for pt in property_types if pt.category in ['residential', 'agricultural', 'land']]
            elif geo_zone == 'peri_urban':
                relevant_types = [pt for pt in property_types if pt.category != 'industrial']
            else:
                relevant_types = property_types

            for property_type in relevant_types:
                for year in years:
                    # Skip some combinations for realism (not all types every year)
                    if random.random() < 0.15:
                        continue

                    # Base price per sqm
                    price_range = PRICE_RANGES.get(property_type.category, (50000, 200000))
                    base_price = random.uniform(price_range[0], price_range[1])

                    # Apply geo zone multiplier
                    base_price *= GEO_ZONE_PRICE_MULTIPLIERS[geo_zone]

                    # Year trend (prices generally increase)
                    year_multiplier = 1 + (year - 2021) * random.uniform(0.03, 0.08)
                    base_price *= year_multiplier

                    # Generate multi-source values
                    num_sources = random.choices([2, 3, 4], weights=[0.3, 0.5, 0.2])[0]
                    source_values = generate_multi_source_values(base_price, num_sources)

                    # Calculate quality score using MultiSourceQualityScorer
                    values = [sv['value'] for sv in source_values]
                    confidences = [sv['confidence'] for sv in source_values]
                    weights = [sv['weight'] for sv in source_values]

                    quality_result = MultiSourceQualityScorer.calculate_quality_score(
                        values, confidences, weights
                    )

                    final_price_per_sqm = quality_result['final_value']
                    quality_score = quality_result['quality_score']

                    # Generate other metrics
                    median_price = final_price_per_sqm * random.uniform(80, 150)  # For 80-150 sqm property
                    num_transactions = random.randint(5, 50) if geo_zone == 'urban' else random.randint(1, 15)

                    # Calculate indices
                    indices = calculate_indices(
                        property_type.category,
                        geo_zone,
                        final_price_per_sqm,
                        commune.population
                    )

                    # Create RealEstateStats record
                    stat = RealEstateStats(
                        commune_id=commune.id,
                        property_type_id=property_type.id,
                        data_source_id=data_sources[0].id,  # Primary source
                        year=year,
                        quarter=None,  # Annual data
                        median_price=median_price,
                        price_per_sqm=final_price_per_sqm,
                        min_price=median_price * 0.7,
                        max_price=median_price * 1.8,
                        currency='XOF',
                        num_transactions=num_transactions,
                        transaction_volume=median_price * num_transactions,
                        inventory_count=random.randint(num_transactions, num_transactions * 3),
                        days_on_market=random.uniform(30, 180),
                        rental_yield=random.uniform(3, 8) if property_type.category in ['residential', 'commercial'] else None,
                        data_quality_score=quality_score,
                        is_estimated=quality_score < 0.80,
                        property_type_label=property_type.category,
                        **indices
                    )

                    db.session.add(stat)
                    db.session.flush()  # Get stat.id

                    # Create source contributions
                    selected_sources = random.sample(data_sources, num_sources)
                    for i, (source, sv) in enumerate(zip(selected_sources, source_values)):
                        contribution = RealEstateSourceContribution(
                            real_estate_stat_id=stat.id,
                            data_source_id=source.id,
                            contribution_weight=sv['weight'],
                            confidence_score=sv['confidence'],
                            is_primary=(i == 0),
                            source_value=sv['value'],
                            deviation_from_final=abs((sv['value'] - final_price_per_sqm) / final_price_per_sqm)
                        )
                        db.session.add(contribution)
                        contribution_count += 1

                    created_count += 1

                    if created_count % 50 == 0:
                        db.session.commit()
                        print(f"  ⏳ Progress: {created_count} stats created...")

        # Final commit
        db.session.commit()

        print(f"\n✅ Real Estate Data generated successfully!")
        print(f"📊 Total statistics: {created_count}")
        print(f"🔗 Source contributions: {contribution_count}")
        print(f"📈 Average sources per stat: {contribution_count/created_count:.1f}")

        # Show sample
        sample = RealEstateStats.query.first()
        if sample:
            print(f"\n📋 Sample record:")
            print(f"   Commune: {sample.commune.name}")
            print(f"   Property Type: {sample.property_type.name}")
            print(f"   Year: {sample.year}")
            print(f"   Price/sqm: {sample.price_per_sqm:,.0f} XOF")
            print(f"   Geo Zone: {sample.geo_zone}")
            print(f"   Price Trend: {sample.price_trend}")
            print(f"   Infrastructure: {sample.infrastructure_score:.1f}")
            print(f"   Quality Score: {sample.data_quality_score:.2%}")
            print(f"   Sources: {len(sample.source_contributions)}")

if __name__ == '__main__':
    generate_realestate_data()
