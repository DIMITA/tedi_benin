
# DATABASE SCHEMA (SIMPLIFIED)

## Core Tables
- countries(id, name, iso_code)
- regions(id, country_id, name)
- communes(id, region_id, name, geo)

## Agriculture
- crops(id, name)
- agri_stats(id, commune_id, crop_id, year, production, yield, price)

## Real Estate
- real_estate_index(id, commune_id, year, price_sqm, risk_score)

## Employment
- employment_index(id, commune_id, year, unemployment_rate, informality_rate)

## Business
- business_index(id, commune_id, year, business_density, growth_score)

## Metadata
- data_sources(id, name, url, license)
- dataset_versions(id, source_id, date, checksum)
