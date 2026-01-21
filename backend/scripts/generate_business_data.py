"""
Generate realistic business data with multi-source validation
"""
import sys
import os
import random
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Commune, BusinessSector, BusinessStats, BusinessSourceContribution, DataSource
from app.utils.data_quality import MultiSourceQualityScorer

# Business density by commune type (businesses per 1000 people)
BUSINESS_DENSITY_RANGES = {
    'urban': (15, 35),
    'peri_urban': (8, 18),
    'rural': (3, 10)
}

# Formality rates by sector category (%)
FORMALITY_RATES = {
    'primary': (15, 35),    # Agriculture - mostly informal
    'secondary': (40, 65),  # Manufacturing - mixed
    'tertiary': (30, 60)    # Services - mixed
}

def get_commune_type(commune):
    """Determine commune type"""
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
        variance = random.uniform(-0.10, 0.10)
        source_value = max(int(base_value * (1 + variance)), 1)

        confidence = random.uniform(0.72, 0.93) if i < 2 else random.uniform(0.62, 0.82)
        weight = 1.0 if i == 0 else random.uniform(0.70, 0.95)

        sources.append({
            'value': source_value,
            'confidence': confidence,
            'weight': weight
        })

    return sources

def calculate_indices(sector, num_businesses, commune_population, formality_rate, year):
    """Calculate all labeling indices for business"""

    # Business density index (0-100)
    if commune_population and commune_population > 0:
        density_per_1000 = (num_businesses / commune_population) * 1000
        business_density_index = min((density_per_1000 / 40) * 100, 100)  # Normalize to 0-100
    else:
        business_density_index = random.uniform(20, 60)

    # Sector growth score (0-100)
    # Tertiary growing fastest, primary slowest
    if sector.category == 'tertiary':
        sector_growth_score = random.uniform(55, 85)
    elif sector.category == 'secondary':
        sector_growth_score = random.uniform(40, 70)
    else:  # primary
        sector_growth_score = random.uniform(25, 55)

    # Year adjustment (growth over time)
    sector_growth_score += (year - 2021) * random.uniform(2, 5)
    sector_growth_score = min(sector_growth_score, 100)

    # Economic resilience index (0-100)
    # Based on formality and sector stability
    base_resilience = formality_rate * 0.6  # Higher formality = more resilience
    if sector.category == 'primary':
        base_resilience += random.uniform(10, 25)  # Agriculture is resilient
    elif sector.category == 'tertiary':
        base_resilience += random.uniform(5, 20)
    else:
        base_resilience += random.uniform(8, 22)

    economic_resilience_index = min(base_resilience, 100)

    # Market gap indicator (0-100, higher = more opportunity)
    # Inverse of business density (more gap where fewer businesses)
    market_gap_indicator = max(100 - business_density_index + random.uniform(-15, 15), 0)
    market_gap_indicator = min(market_gap_indicator, 100)

    # Competition intensity
    if business_density_index > 70:
        competition_intensity = random.choices(['medium', 'high'], weights=[0.3, 0.7])[0]
    elif business_density_index > 40:
        competition_intensity = random.choices(['low', 'medium', 'high'], weights=[0.2, 0.6, 0.2])[0]
    else:
        competition_intensity = random.choices(['low', 'medium'], weights=[0.7, 0.3])[0]

    # Market saturation
    if business_density_index > 75:
        market_saturation = random.choices(['saturated', 'oversaturated'], weights=[0.6, 0.4])[0]
    elif business_density_index > 50:
        market_saturation = random.choices(['balanced', 'saturated'], weights=[0.7, 0.3])[0]
    elif business_density_index > 25:
        market_saturation = random.choices(['undersaturated', 'balanced'], weights=[0.4, 0.6])[0]
    else:
        market_saturation = 'undersaturated'

    # Innovation score (0-100)
    if sector.category == 'tertiary' and 'Technology' in sector.name:
        innovation_score = random.uniform(60, 90)
    elif sector.category == 'tertiary':
        innovation_score = random.uniform(30, 65)
    elif sector.category == 'secondary':
        innovation_score = random.uniform(25, 55)
    else:
        innovation_score = random.uniform(15, 40)

    # Digital adoption rate (0-100%)
    if 'Technology' in sector.name:
        digital_adoption_rate = random.uniform(70, 95)
    elif sector.category == 'tertiary':
        digital_adoption_rate = random.uniform(30, 60)
    elif sector.category == 'secondary':
        digital_adoption_rate = random.uniform(20, 45)
    else:
        digital_adoption_rate = random.uniform(10, 30)

    return {
        'business_density_index': business_density_index,
        'sector_growth_score': sector_growth_score,
        'economic_resilience_index': economic_resilience_index,
        'market_gap_indicator': market_gap_indicator,
        'competition_intensity': competition_intensity,
        'market_saturation': market_saturation,
        'innovation_score': innovation_score,
        'digital_adoption_rate': digital_adoption_rate
    }

def generate_business_data():
    """Generate realistic business statistics with multi-source validation"""
    app = create_app()

    with app.app_context():
        print("🏢 Generating Business Data with Multi-Source Validation...")

        # Get all necessary data
        communes = Commune.query.all()
        business_sectors = BusinessSector.query.all()
        data_sources = DataSource.query.all()

        if len(data_sources) < 3:
            print("⚠️  Need at least 3 data sources. Found:", len(data_sources))
            return

        print(f"📊 Found {len(communes)} communes and {len(business_sectors)} business sectors")

        years = [2021, 2022, 2023]
        created_count = 0
        contribution_count = 0

        # Generate data for all communes
        target_communes = communes

        print(f"🎯 Generating data for {len(target_communes)} communes")

        for commune in target_communes:
            commune_type = get_commune_type(commune)

            # Calculate number of businesses based on population
            if commune.population:
                density_range = BUSINESS_DENSITY_RANGES[commune_type]
                businesses_per_1000 = random.uniform(density_range[0], density_range[1])
                total_businesses = int((commune.population / 1000) * businesses_per_1000)
            else:
                total_businesses = random.randint(100, 1000)

            for sector in business_sectors:
                # Not all sectors in all communes
                if commune_type == 'rural' and sector.category == 'tertiary' and 'Technology' in sector.name:
                    continue  # Skip tech in rural areas

                if random.random() < 0.15:  # Skip 15%
                    continue

                for year in years:
                    # Sector share of total businesses
                    if sector.category == 'primary':
                        sector_share = random.uniform(0.10, 0.30) if commune_type == 'rural' else random.uniform(0.05, 0.15)
                    elif sector.category == 'secondary':
                        sector_share = random.uniform(0.08, 0.20)
                    else:  # tertiary
                        sector_share = random.uniform(0.15, 0.35)

                    num_businesses = int(total_businesses * sector_share * random.uniform(0.03, 0.12))
                    num_businesses = max(num_businesses, 5)  # At least 5 businesses

                    # Generate multi-source values
                    num_sources = random.choices([2, 3, 4], weights=[0.3, 0.5, 0.2])[0]
                    source_values = generate_multi_source_values(num_businesses, num_sources)

                    # Calculate quality score
                    values = [sv['value'] for sv in source_values]
                    confidences = [sv['confidence'] for sv in source_values]
                    weights = [sv['weight'] for sv in source_values]

                    quality_result = MultiSourceQualityScorer.calculate_quality_score(
                        values, confidences, weights
                    )

                    final_num_businesses = int(quality_result['final_value'])
                    quality_score = quality_result['quality_score']

                    # Business dynamics
                    birth_rate = random.uniform(5, 15)  # %
                    death_rate = random.uniform(3, 10)  # %
                    num_new = int(final_num_businesses * birth_rate / 100)
                    num_closed = int(final_num_businesses * death_rate / 100)

                    # Financial metrics
                    avg_revenue = random.uniform(2000000, 50000000)  # XOF per business
                    total_revenue = avg_revenue * final_num_businesses
                    avg_employees = random.uniform(2, 15)
                    total_employees = int(avg_employees * final_num_businesses)

                    # Formality
                    formality_range = FORMALITY_RATES.get(sector.category, (30, 50))
                    formality_rate = random.uniform(formality_range[0], formality_range[1])
                    formal_businesses = int(final_num_businesses * formality_rate / 100)
                    informal_businesses = final_num_businesses - formal_businesses

                    # Size distribution
                    micro = int(final_num_businesses * random.uniform(0.60, 0.80))
                    small = int(final_num_businesses * random.uniform(0.15, 0.25))
                    medium = int(final_num_businesses * random.uniform(0.03, 0.08))
                    large = final_num_businesses - micro - small - medium

                    # Calculate indices
                    indices = calculate_indices(
                        sector,
                        final_num_businesses,
                        commune.population,
                        formality_rate,
                        year
                    )

                    # Create BusinessStats record
                    stat = BusinessStats(
                        commune_id=commune.id,
                        sector_id=sector.id,
                        data_source_id=data_sources[0].id,
                        year=year,
                        quarter=None,
                        num_businesses=final_num_businesses,
                        num_new_businesses=num_new,
                        num_closed_businesses=num_closed,
                        business_birth_rate=birth_rate,
                        business_death_rate=death_rate,
                        total_revenue=total_revenue,
                        avg_revenue_per_business=avg_revenue,
                        total_employees=total_employees,
                        avg_employees_per_business=avg_employees,
                        currency='XOF',
                        micro_businesses=micro,
                        small_businesses=small,
                        medium_businesses=medium,
                        large_businesses=large,
                        formal_businesses=formal_businesses,
                        informal_businesses=informal_businesses,
                        formality_rate=formality_rate,
                        data_quality_score=quality_score,
                        is_estimated=quality_score < 0.75,
                        **indices
                    )

                    db.session.add(stat)
                    db.session.flush()

                    # Create source contributions
                    selected_sources = random.sample(data_sources, num_sources)
                    for i, (source, sv) in enumerate(zip(selected_sources, source_values)):
                        contribution = BusinessSourceContribution(
                            business_stat_id=stat.id,
                            data_source_id=source.id,
                            contribution_weight=sv['weight'],
                            confidence_score=sv['confidence'],
                            is_primary=(i == 0),
                            source_value=sv['value'],
                            deviation_from_final=abs((sv['value'] - final_num_businesses) / final_num_businesses) if final_num_businesses > 0 else 0
                        )
                        db.session.add(contribution)
                        contribution_count += 1

                    created_count += 1

                    if created_count % 100 == 0:
                        db.session.commit()
                        print(f"  ⏳ Progress: {created_count} stats created...")

        # Final commit
        db.session.commit()

        print(f"\n✅ Business Data generated successfully!")
        print(f"📊 Total statistics: {created_count}")
        print(f"🔗 Source contributions: {contribution_count}")
        print(f"📈 Average sources per stat: {contribution_count/created_count:.1f}")

        # Show sample
        sample = BusinessStats.query.first()
        if sample:
            print(f"\n📋 Sample record:")
            print(f"   Commune: {sample.commune.name}")
            print(f"   Sector: {sample.sector.name}")
            print(f"   Year: {sample.year}")
            print(f"   Businesses: {sample.num_businesses:,}")
            print(f"   Formality: {sample.formality_rate:.1f}%")
            print(f"   Density Index: {sample.business_density_index:.1f}")
            print(f"   Growth Score: {sample.sector_growth_score:.1f}")
            print(f"   Quality Score: {sample.data_quality_score:.2%}")
            print(f"   Sources: {len(sample.source_contributions)}")

if __name__ == '__main__':
    generate_business_data()
