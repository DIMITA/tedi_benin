"""
Generate realistic employment data with multi-source validation
"""
import sys
import os
import random
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Commune, JobCategory, EmploymentStats, EmploymentSourceContribution, DataSource
from app.utils.data_quality import MultiSourceQualityScorer

# Unemployment rates by sector (%)
BASE_UNEMPLOYMENT_RATES = {
    'primary': (3, 8),      # Agriculture - lower unemployment
    'secondary': (8, 15),   # Manufacturing/Construction
    'tertiary': (10, 20)    # Services - higher unemployment
}

# Informality rates by sector (%)
INFORMALITY_RATES = {
    'primary': (70, 90),    # Agriculture - very high
    'secondary': (40, 65),  # Manufacturing - medium-high
    'tertiary': (50, 75)    # Services - high
}

# Median salaries by sector (XOF monthly)
SALARY_RANGES = {
    'primary': (30000, 60000),
    'secondary': (50000, 120000),
    'tertiary': (45000, 150000)
}

def generate_multi_source_values(base_value, num_sources=3):
    """Generate values from multiple sources with realistic variance"""
    sources = []

    for i in range(num_sources):
        variance = random.uniform(-0.12, 0.12)
        source_value = base_value * (1 + variance)

        confidence = random.uniform(0.70, 0.92) if i < 2 else random.uniform(0.60, 0.80)
        weight = 1.0 if i == 0 else random.uniform(0.65, 0.90)

        sources.append({
            'value': source_value,
            'confidence': confidence,
            'weight': weight
        })

    return sources

def calculate_indices(job_category, unemployment_rate, informal_rate, median_salary, commune_population):
    """Calculate all labeling indices for employment"""

    # Skill level index (0-100)
    if job_category.sector == 'primary':
        skill_level_index = random.uniform(15, 40)
    elif job_category.sector == 'secondary':
        skill_level_index = random.uniform(35, 70)
    else:  # tertiary
        if 'IT' in job_category.name or 'Professional' in job_category.name or 'Financial' in job_category.name:
            skill_level_index = random.uniform(60, 90)
        elif 'Education' in job_category.name or 'Healthcare' in job_category.name:
            skill_level_index = random.uniform(55, 85)
        else:
            skill_level_index = random.uniform(30, 60)

    # Employment pressure index (0-100, higher = more pressure/scarce jobs)
    # Based on unemployment rate
    employment_pressure_index = min(unemployment_rate * 5, 100)  # Convert to 0-100 scale

    # Informality rate index (already 0-100%)
    informality_rate_index = informal_rate

    # Salary range estimation
    if median_salary < 50000:
        salary_range_estimation = 'low'
    elif median_salary < 90000:
        salary_range_estimation = 'medium'
    elif median_salary < 150000:
        salary_range_estimation = 'high'
    else:
        salary_range_estimation = 'very_high'

    return {
        'job_category_label': job_category.sector,
        'skill_level_index': skill_level_index,
        'employment_pressure_index': employment_pressure_index,
        'informality_rate_index': informality_rate_index,
        'salary_range_estimation': salary_range_estimation
    }

def generate_employment_data():
    """Generate realistic employment statistics with multi-source validation"""
    app = create_app()

    with app.app_context():
        print("💼 Generating Employment Data with Multi-Source Validation...")

        # Get all necessary data
        communes = Commune.query.all()
        job_categories = JobCategory.query.all()
        data_sources = DataSource.query.all()

        if len(data_sources) < 3:
            print("⚠️  Need at least 3 data sources. Found:", len(data_sources))
            return

        print(f"📊 Found {len(communes)} communes and {len(job_categories)} job categories")

        years = [2021, 2022, 2023]
        created_count = 0
        contribution_count = 0

        # Generate data for all communes (employment data more universally available)
        target_communes = communes

        print(f"🎯 Generating data for {len(target_communes)} communes")

        for commune in target_communes:
            # Estimate labor force (rough estimate based on population)
            if commune.population:
                labor_force = int(commune.population * random.uniform(0.35, 0.45))  # 35-45% of population
            else:
                labor_force = random.randint(5000, 30000)

            for job_category in job_categories:
                # Not all categories in all communes
                if random.random() < 0.20:  # Skip 20%
                    continue

                for year in years:
                    # Calculate labor force for this category
                    if job_category.sector == 'primary':
                        category_share = random.uniform(0.25, 0.50)  # Agriculture dominates in many areas
                    elif job_category.sector == 'secondary':
                        category_share = random.uniform(0.08, 0.20)
                    else:
                        category_share = random.uniform(0.10, 0.30)

                    category_labor_force = int(labor_force * category_share * random.uniform(0.05, 0.20))

                    # Base unemployment rate
                    unemp_range = BASE_UNEMPLOYMENT_RATES.get(job_category.sector, (8, 15))
                    base_unemployment = random.uniform(unemp_range[0], unemp_range[1])

                    # Year trend (unemployment generally decreasing slightly)
                    year_adjustment = (2023 - year) * random.uniform(0.5, 1.5)
                    unemployment_rate = max(base_unemployment - year_adjustment, 2.0)

                    total_employed = int(category_labor_force * (1 - unemployment_rate / 100))
                    total_unemployed = category_labor_force - total_employed

                    # Generate multi-source values for key metric
                    num_sources = random.choices([2, 3], weights=[0.4, 0.6])[0]
                    source_values = generate_multi_source_values(total_employed, num_sources)

                    # Calculate quality score
                    values = [sv['value'] for sv in source_values]
                    confidences = [sv['confidence'] for sv in source_values]
                    weights = [sv['weight'] for sv in source_values]

                    quality_result = MultiSourceQualityScorer.calculate_quality_score(
                        values, confidences, weights
                    )

                    final_employed = int(quality_result['final_value'])
                    quality_score = quality_result['quality_score']

                    # Informal sector
                    informal_range = INFORMALITY_RATES.get(job_category.sector, (50, 70))
                    informal_rate = random.uniform(informal_range[0], informal_range[1])
                    informal_employed = int(final_employed * informal_rate / 100)

                    # Salaries
                    salary_range = SALARY_RANGES.get(job_category.sector, (40000, 100000))
                    median_salary = random.uniform(salary_range[0], salary_range[1])

                    # Participation rate
                    participation_rate = random.uniform(40, 65)

                    # Demographics
                    youth_employment = int(final_employed * random.uniform(0.15, 0.30))
                    female_employment = int(final_employed * random.uniform(0.35, 0.55))

                    # Calculate indices
                    indices = calculate_indices(
                        job_category,
                        unemployment_rate,
                        informal_rate,
                        median_salary,
                        commune.population
                    )

                    # Create EmploymentStats record
                    stat = EmploymentStats(
                        commune_id=commune.id,
                        job_category_id=job_category.id,
                        data_source_id=data_sources[0].id,
                        year=year,
                        quarter=None,
                        total_employed=final_employed,
                        total_unemployed=total_unemployed,
                        labor_force=category_labor_force,
                        unemployment_rate=unemployment_rate,
                        participation_rate=participation_rate,
                        informal_employed=informal_employed,
                        informal_rate=informal_rate,
                        median_salary=median_salary,
                        min_salary=median_salary * 0.6,
                        max_salary=median_salary * 2.0,
                        currency='XOF',
                        youth_employment=youth_employment,
                        female_employment=female_employment,
                        data_quality_score=quality_score,
                        is_estimated=quality_score < 0.75,
                        **indices
                    )

                    db.session.add(stat)
                    db.session.flush()

                    # Create source contributions
                    selected_sources = random.sample(data_sources, num_sources)
                    for i, (source, sv) in enumerate(zip(selected_sources, source_values)):
                        contribution = EmploymentSourceContribution(
                            employment_stat_id=stat.id,
                            data_source_id=source.id,
                            contribution_weight=sv['weight'],
                            confidence_score=sv['confidence'],
                            is_primary=(i == 0),
                            source_value=sv['value'],
                            deviation_from_final=abs((sv['value'] - final_employed) / final_employed) if final_employed > 0 else 0
                        )
                        db.session.add(contribution)
                        contribution_count += 1

                    created_count += 1

                    if created_count % 100 == 0:
                        db.session.commit()
                        print(f"  ⏳ Progress: {created_count} stats created...")

        # Final commit
        db.session.commit()

        print(f"\n✅ Employment Data generated successfully!")
        print(f"📊 Total statistics: {created_count}")
        print(f"🔗 Source contributions: {contribution_count}")
        print(f"📈 Average sources per stat: {contribution_count/created_count:.1f}")

        # Show sample
        sample = EmploymentStats.query.first()
        if sample:
            print(f"\n📋 Sample record:")
            print(f"   Commune: {sample.commune.name}")
            print(f"   Job Category: {sample.job_category.name}")
            print(f"   Year: {sample.year}")
            print(f"   Employed: {sample.total_employed:,}")
            print(f"   Unemployment Rate: {sample.unemployment_rate:.1f}%")
            print(f"   Informality: {sample.informal_rate:.1f}%")
            print(f"   Median Salary: {sample.median_salary:,.0f} XOF")
            print(f"   Quality Score: {sample.data_quality_score:.2%}")
            print(f"   Sources: {len(sample.source_contributions)}")

if __name__ == '__main__':
    generate_employment_data()
