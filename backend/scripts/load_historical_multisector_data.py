#!/usr/bin/env python3
"""
Load comprehensive historical data for all sectors (2010-2024)
- Real Estate
- Employment  
- Business

Generates realistic data with temporal trends for all 77 communes
"""

import sys
import random
import math
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db
from app.models.geo import Commune, Region, Country
from app.models.realestate import PropertyType, RealEstateStats
from app.models.employment import JobCategory, EmploymentStats
from app.models.business import BusinessSector, BusinessStats


def create_property_types():
    """Create property types if they don't exist"""
    types_data = [
        {'name': 'Residential', 'name_fr': 'Résidentiel', 'category': 'residential', 'description': 'Houses, apartments, villas'},
        {'name': 'Commercial', 'name_fr': 'Commercial', 'category': 'commercial', 'description': 'Shops, offices, restaurants'},
        {'name': 'Agricultural', 'name_fr': 'Agricole', 'category': 'agricultural', 'description': 'Farm land, agricultural buildings'},
        {'name': 'Industrial', 'name_fr': 'Industriel', 'category': 'industrial', 'description': 'Warehouses, factories'},
    ]
    
    for type_data in types_data:
        existing = PropertyType.query.filter_by(name=type_data['name']).first()
        if not existing:
            pt = PropertyType(**type_data)
            db.session.add(pt)
    
    db.session.commit()
    print(f"✓ Property types created/verified")
    return PropertyType.query.all()


def create_job_categories():
    """Create job categories if they don't exist"""
    categories_data = [
        {'name': 'Agriculture', 'name_fr': 'Agriculture', 'sector': 'primary'},
        {'name': 'Manufacturing', 'name_fr': 'Fabrication', 'sector': 'secondary'},
        {'name': 'Retail & Trade', 'name_fr': 'Commerce', 'sector': 'tertiary'},
        {'name': 'Services', 'name_fr': 'Services', 'sector': 'tertiary'},
        {'name': 'Education', 'name_fr': 'Éducation', 'sector': 'tertiary'},
        {'name': 'Healthcare', 'name_fr': 'Santé', 'sector': 'tertiary'},
        {'name': 'Construction', 'name_fr': 'Construction', 'sector': 'secondary'},
        {'name': 'Public Administration', 'name_fr': 'Administration publique', 'sector': 'tertiary'},
    ]
    
    for cat_data in categories_data:
        existing = JobCategory.query.filter_by(name=cat_data['name']).first()
        if not existing:
            jc = JobCategory(**cat_data)
            db.session.add(jc)
    
    db.session.commit()
    print(f"✓ Job categories created/verified")
    return JobCategory.query.all()


def create_business_sectors():
    """Create business sectors if they don't exist"""
    sectors_data = [
        {'name': 'Agriculture', 'name_fr': 'Agriculture', 'category': 'primary'},
        {'name': 'Manufacturing', 'name_fr': 'Fabrication', 'category': 'secondary'},
        {'name': 'Retail & Distribution', 'name_fr': 'Commerce de détail', 'category': 'tertiary'},
        {'name': 'Services', 'name_fr': 'Services', 'category': 'tertiary'},
        {'name': 'Transportation', 'name_fr': 'Transport', 'category': 'tertiary'},
        {'name': 'Tourism & Hospitality', 'name_fr': 'Tourisme', 'category': 'tertiary'},
        {'name': 'Technology & IT', 'name_fr': 'Technologie', 'category': 'tertiary'},
        {'name': 'Financial Services', 'name_fr': 'Services financiers', 'category': 'tertiary'},
        {'name': 'Real Estate', 'name_fr': 'Immobilier', 'category': 'tertiary'},
        {'name': 'Energy', 'name_fr': 'Énergie', 'category': 'secondary'},
    ]
    
    for sector_data in sectors_data:
        existing = BusinessSector.query.filter_by(name=sector_data['name']).first()
        if not existing:
            bs = BusinessSector(**sector_data)
            db.session.add(bs)
    
    db.session.commit()
    print(f"✓ Business sectors created/verified")
    return BusinessSector.query.all()


def generate_realistic_price(base_price, year, trend_factor=1.03):
    """Generate realistic real estate price with trend"""
    # Apply annual trend
    price = base_price * (trend_factor ** (year - 2010))
    
    # Add annual variation
    variation = random.gauss(0, 0.05)
    price *= (1 + variation)
    
    # Add seasonal component (simple sine wave)
    seasonal = 0.02 * math.sin(2 * math.pi * random.random())
    price *= (1 + seasonal)
    
    return max(price * 1000, 10000)  # Minimum price


def generate_realestate_data(property_types, communes):
    """Generate real estate statistics 2010-2024"""
    print("\n📍 Generating Real Estate Data (2010-2024)...")
    
    # Base prices per property type (in XOF per m²)
    base_prices = {
        'Residential': 150000,
        'Commercial': 250000,
        'Agricultural': 50000,
        'Industrial': 100000,
    }
    
    records = 0
    for commune in communes:
        for prop_type in property_types:
            for year in range(2010, 2025):
                # Skip some combinations randomly to simulate data availability
                if random.random() < 0.1:  # 10% chance to skip
                    continue
                
                base_price = base_prices.get(prop_type.name, 100000)
                median_price = generate_realistic_price(base_price, year, trend_factor=1.04)
                
                # Generate related metrics
                price_per_sqm = median_price / random.uniform(80, 200)  # Assumed property size
                num_transactions = int(random.gauss(
                    5 + (year - 2010) * 0.5,  # Growth trend
                    max(2, 3 - (year - 2010) * 0.1)  # Variance decreases over time
                ))
                num_transactions = max(1, num_transactions)
                
                rental_yield = random.uniform(3, 8)  # Annual rental yield %
                
                # Days on market (decreasing over time as market matures)
                days_on_market = random.gauss(
                    90 - (year - 2010) * 2,
                    20
                )
                days_on_market = max(7, days_on_market)
                
                # Data quality improves over time
                data_quality = min(1.0, 0.6 + (year - 2010) * 0.02 + random.uniform(-0.05, 0.05))
                
                # Geo-zone determination (urban, peri_urban, rural based on commune)
                if commune.population and commune.population > 100000:
                    geo_zone = 'urban'
                elif commune.population and commune.population > 20000:
                    geo_zone = 'peri_urban'
                else:
                    geo_zone = 'rural'
                
                # Price trend
                if year >= 2018:
                    price_trend = 'increasing' if random.random() > 0.3 else 'stable'
                elif year >= 2015:
                    price_trend = 'stable'
                else:
                    price_trend = 'decreasing' if random.random() > 0.4 else 'stable'
                
                # Land risk level
                land_risk_level = random.choice(['low', 'low', 'medium', 'high'])
                
                # Infrastructure score (0-100)
                if geo_zone == 'urban':
                    infrastructure_score = random.gauss(75, 15)
                elif geo_zone == 'peri_urban':
                    infrastructure_score = random.gauss(50, 20)
                else:
                    infrastructure_score = random.gauss(30, 15)
                infrastructure_score = max(0, min(100, infrastructure_score))
                
                # Legal clarity
                legal_clarity = random.gauss(60 + (year - 2010), 15)
                legal_clarity = max(0, min(100, legal_clarity))
                
                # Development potential
                if price_trend == 'increasing' and infrastructure_score > 60:
                    dev_potential = 'very_high'
                elif price_trend == 'increasing' or infrastructure_score > 50:
                    dev_potential = 'high'
                elif infrastructure_score > 30:
                    dev_potential = 'medium'
                else:
                    dev_potential = 'low'
                
                # Create record
                stat = RealEstateStats(
                    commune_id=commune.id,
                    property_type_id=prop_type.id,
                    year=year,
                    median_price=median_price,
                    price_per_sqm=price_per_sqm,
                    min_price=median_price * 0.7,
                    max_price=median_price * 1.3,
                    num_transactions=num_transactions,
                    transaction_volume=median_price * num_transactions,
                    inventory_count=random.randint(5, 50),
                    days_on_market=days_on_market,
                    rental_yield=rental_yield,
                    data_quality_score=data_quality,
                    is_estimated=(random.random() < 0.3),
                    property_type_label=prop_type.name,
                    geo_zone=geo_zone,
                    price_per_sqm_index=min(100, (price_per_sqm / 1000) * 10),
                    price_trend=price_trend,
                    land_risk_level=land_risk_level,
                    infrastructure_score=infrastructure_score,
                    legal_clarity_index=legal_clarity,
                    development_potential=dev_potential
                )
                
                db.session.add(stat)
                records += 1
                
                if records % 500 == 0:
                    print(f"  → {records} records generated...")
    
    db.session.commit()
    print(f"✓ Real Estate: {records} records created")


def generate_employment_data(job_categories, communes):
    """Generate employment statistics 2010-2024"""
    print("\n💼 Generating Employment Data (2010-2024)...")
    
    records = 0
    for commune in communes:
        commune_labor_force = max(500, (commune.population or 5000) // 3)  # ~1/3 of population
        
        for job_cat in job_categories:
            for year in range(2010, 2025):
                # Skip some combinations
                if random.random() < 0.15:
                    continue
                
                # Generate employment metrics
                # Employment grows over time with fluctuations
                base_employed = int(commune_labor_force * random.uniform(0.5, 0.7))
                employed = int(base_employed * (1 + (year - 2010) * 0.02 + random.gauss(0, 0.05)))
                employed = max(10, employed)
                
                # Unemployment rate (declining trend)
                base_unemployment = random.uniform(8, 15)
                unemployment_rate = max(3, base_unemployment - (year - 2010) * 0.3 + random.gauss(0, 2))
                
                unemployed = int(employed * (unemployment_rate / 100))
                labor_force = employed + unemployed
                
                # Informal rate (high in African context, slowly declining)
                informal_rate = max(20, 70 - (year - 2010) * 2 + random.gauss(0, 5))
                informal_employed = int(employed * (informal_rate / 100))
                
                # Salary metrics (growing with inflation)
                base_median_salary = 80000  # XOF per month
                salary_growth = (1 + (year - 2010) * 0.03) ** 1.5
                median_salary = base_median_salary * salary_growth * random.uniform(0.8, 1.2)
                
                # Demographics
                youth_pct = random.uniform(0.3, 0.5)
                youth_employment = int(employed * youth_pct)
                female_pct = random.uniform(0.35, 0.45)
                female_employment = int(employed * female_pct)
                
                # Data quality
                data_quality = min(1.0, 0.5 + (year - 2010) * 0.02 + random.uniform(-0.05, 0.05))
                
                # Skill level index (varies by job category)
                skill_map = {
                    'Agriculture': 30,
                    'Manufacturing': 50,
                    'Retail & Trade': 40,
                    'Services': 45,
                    'Education': 80,
                    'Healthcare': 75,
                    'Construction': 35,
                    'Public Administration': 60,
                }
                skill_level = skill_map.get(job_cat.name, 50) + random.gauss(0, 10)
                skill_level = max(0, min(100, skill_level))
                
                # Employment pressure (inverse: high = scarce jobs)
                if unemployment_rate > 12:
                    employment_pressure = random.gauss(70, 10)
                elif unemployment_rate > 8:
                    employment_pressure = random.gauss(50, 15)
                else:
                    employment_pressure = random.gauss(30, 10)
                employment_pressure = max(0, min(100, employment_pressure))
                
                # Salary range estimation
                if median_salary < 100000:
                    salary_range = 'low'
                elif median_salary < 200000:
                    salary_range = 'medium'
                elif median_salary < 400000:
                    salary_range = 'high'
                else:
                    salary_range = 'very_high'
                
                # Create record
                stat = EmploymentStats(
                    commune_id=commune.id,
                    job_category_id=job_cat.id,
                    year=year,
                    total_employed=employed,
                    total_unemployed=unemployed,
                    labor_force=labor_force,
                    unemployment_rate=unemployment_rate,
                    participation_rate=(labor_force / commune_labor_force) * 100 if commune_labor_force > 0 else 0,
                    informal_employed=informal_employed,
                    informal_rate=informal_rate,
                    median_salary=median_salary,
                    min_salary=median_salary * 0.6,
                    max_salary=median_salary * 2.5,
                    youth_employment=youth_employment,
                    female_employment=female_employment,
                    data_quality_score=data_quality,
                    job_category_label=job_cat.name,
                    skill_level_index=skill_level,
                    employment_pressure_index=employment_pressure,
                    informality_rate_index=informal_rate,
                    salary_range_estimation=salary_range
                )
                
                db.session.add(stat)
                records += 1
                
                if records % 500 == 0:
                    print(f"  → {records} records generated...")
    
    db.session.commit()
    print(f"✓ Employment: {records} records created")


def generate_business_data(business_sectors, communes):
    """Generate business statistics 2010-2024"""
    print("\n🏢 Generating Business Data (2010-2024)...")
    
    records = 0
    for commune in communes:
        # Base business count estimate (1 business per 50 inhabitants)
        base_business_count = max(20, (commune.population or 5000) // 50)
        
        for sector in business_sectors:
            for year in range(2010, 2025):
                # Skip some combinations
                if random.random() < 0.2:
                    continue
                
                # Generate business metrics
                # Growth trend with fluctuations
                growth_rate = 1 + (year - 2010) * 0.05
                num_businesses = int(base_business_count * growth_rate * random.uniform(0.8, 1.2))
                num_businesses = max(5, num_businesses)
                
                # Business dynamics
                new_businesses = int(num_businesses * random.uniform(0.05, 0.15))
                closed_businesses = int(num_businesses * random.uniform(0.02, 0.08))
                birth_rate = (new_businesses / num_businesses * 100) if num_businesses > 0 else 0
                death_rate = (closed_businesses / num_businesses * 100) if num_businesses > 0 else 0
                
                # Revenue metrics (growing over time)
                avg_revenue_base = 5000000 * (1.06 ** (year - 2010))  # XOF
                avg_revenue = avg_revenue_base * random.uniform(0.7, 1.3)
                total_revenue = avg_revenue * num_businesses
                
                # Employment in sector
                employees_per_business = random.uniform(1.5, 8)
                total_employees = int(num_businesses * employees_per_business)
                
                # Business size distribution (Pareto-like)
                micro = int(num_businesses * 0.70)
                small = int(num_businesses * 0.20)
                medium = int(num_businesses * 0.08)
                large = int(num_businesses * 0.02)
                
                # Formality rate (improving over time)
                formality_rate = min(90, 20 + (year - 2010) * 3 + random.gauss(0, 5))
                formal_businesses = int(num_businesses * formality_rate / 100)
                informal_businesses = num_businesses - formal_businesses
                
                # Data quality
                data_quality = min(1.0, 0.55 + (year - 2010) * 0.02 + random.uniform(-0.05, 0.05))
                
                # KPIs
                business_density = (num_businesses / max(1, (commune.population or 1000) / 1000)) * 100
                business_density = max(0, min(100, business_density))
                
                # Sector growth score
                growth_score = min(100, 30 + birth_rate * 2 + random.gauss(0, 10))
                growth_score = max(0, growth_score)
                
                # Economic resilience (inverse of death rate, influenced by formality)
                resilience = min(100, 70 - death_rate * 3 + formality_rate * 0.2 + random.gauss(0, 5))
                resilience = max(0, resilience)
                
                # Market gap indicator
                if num_businesses < base_business_count * 0.5:
                    market_gap = random.gauss(70, 10)
                elif num_businesses > base_business_count * 1.5:
                    market_gap = random.gauss(30, 15)
                else:
                    market_gap = random.gauss(50, 15)
                market_gap = max(0, min(100, market_gap))
                
                # Competition intensity
                if num_businesses < base_business_count:
                    competition = 'low'
                elif num_businesses < base_business_count * 1.5:
                    competition = 'medium'
                else:
                    competition = 'high'
                
                # Market saturation
                saturation_ratio = num_businesses / base_business_count if base_business_count > 0 else 1
                if saturation_ratio < 0.7:
                    market_saturation = 'undersaturated'
                elif saturation_ratio < 1.2:
                    market_saturation = 'balanced'
                elif saturation_ratio < 1.7:
                    market_saturation = 'saturated'
                else:
                    market_saturation = 'oversaturated'
                
                # Innovation score (higher in tech-heavy sectors)
                if sector.name in ['Technology & IT', 'Services']:
                    innovation = random.gauss(60, 15)
                else:
                    innovation = random.gauss(40, 15)
                innovation = max(0, min(100, innovation))
                
                # Digital adoption (increasing over time)
                digital_adoption = min(90, 10 + (year - 2010) * 5 + random.gauss(0, 10))
                digital_adoption = max(0, digital_adoption)
                
                # Create record
                stat = BusinessStats(
                    commune_id=commune.id,
                    sector_id=sector.id,
                    year=year,
                    num_businesses=num_businesses,
                    num_new_businesses=new_businesses,
                    num_closed_businesses=closed_businesses,
                    business_birth_rate=birth_rate,
                    business_death_rate=death_rate,
                    total_revenue=total_revenue,
                    avg_revenue_per_business=avg_revenue,
                    total_employees=total_employees,
                    avg_employees_per_business=employees_per_business,
                    micro_businesses=micro,
                    small_businesses=small,
                    medium_businesses=medium,
                    large_businesses=large,
                    formal_businesses=formal_businesses,
                    informal_businesses=informal_businesses,
                    formality_rate=formality_rate,
                    data_quality_score=data_quality,
                    business_density_index=business_density,
                    sector_growth_score=growth_score,
                    economic_resilience_index=resilience,
                    market_gap_indicator=market_gap,
                    competition_intensity=competition,
                    market_saturation=market_saturation,
                    innovation_score=innovation,
                    digital_adoption_rate=digital_adoption
                )
                
                db.session.add(stat)
                records += 1
                
                if records % 500 == 0:
                    print(f"  → {records} records generated...")
    
    db.session.commit()
    print(f"✓ Business: {records} records created")


def main():
    """Main execution"""
    print("=" * 60)
    print("TEDI MULTI-SECTOR DATA LOADER (2010-2024)")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        # Get communes (should already exist from seed)
        communes = Commune.query.all()
        if not communes:
            print("❌ ERROR: No communes found. Run seed database first.")
            sys.exit(1)
        
        print(f"\n📊 Found {len(communes)} communes")
        
        # Create property types and related data
        property_types = create_property_types()
        job_categories = create_job_categories()
        business_sectors = create_business_sectors()
        
        # Generate data for each sector
        generate_realestate_data(property_types, communes)
        generate_employment_data(job_categories, communes)
        generate_business_data(business_sectors, communes)
        
        print("\n" + "=" * 60)
        print("✓ ALL MULTI-SECTOR DATA LOADED SUCCESSFULLY!")
        print("=" * 60)
        print("\nData Summary:")
        print(f"  • Property Types: {len(property_types)}")
        print(f"  • Job Categories: {len(job_categories)}")
        print(f"  • Business Sectors: {len(business_sectors)}")
        print(f"  • Communes: {len(communes)}")
        print("\nYou can now start the backend and access the APIs:")
        print("  - GET /api/v1/realestate/stats/aggregated")
        print("  - GET /api/v1/employment/stats/aggregated")
        print("  - GET /api/v1/business/stats/aggregated")


if __name__ == '__main__':
    main()
