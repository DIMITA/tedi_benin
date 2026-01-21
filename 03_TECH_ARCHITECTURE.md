
# TECHNICAL ARCHITECTURE

## Backend
- Python 3.11
- Flask + Flask-RESTX
- SQLAlchemy ORM
- PostgreSQL + PostGIS
- Celery + Redis (async jobs)

## Frontend
- Vue.js 3
- Vite
- TailwindCSS
- Pinia (state)
- Axios

## Infrastructure
- Docker & Docker Compose
- Nginx
- VPS (Hetzner / OVH / Hostinger)

## Data Pipeline
1. Fetch raw datasets (API / CSV)
2. Validate schema
3. Normalize values
4. Enrich with geo & indices
5. Store versioned data
