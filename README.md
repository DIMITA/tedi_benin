# TEDI - Territorial & Economic Data Index

![TEDI Logo](https://via.placeholder.com/150x50/2563eb/ffffff?text=TEDI)

> The reference data infrastructure for territorial, economic and social intelligence in Africa, starting with Benin.

## Overview

TEDI provides **structured, enriched, AI-ready datasets** across multiple sectors:
- Agriculture
- Real Estate
- Employment
- Business

### MVP Focus
This MVP implementation focuses on the **Agriculture Data Index (ADI)** for Benin with:
- Commune-level aggregation
- 3+ strategic crops (Maize, Rice, Cassava)
- REST API with API Key authentication
- Admin dashboard
- Data ingestion pipeline

## Architecture

### Backend
- **Python 3.11** - Core language
- **Flask + Flask-RESTX** - API framework with auto-documentation
- **SQLAlchemy ORM** - Database abstraction
- **PostgreSQL + PostGIS** - Database with geospatial support
- **Celery + Redis** - Asynchronous job processing
- **Alembic** - Database migrations

### Frontend
- **Vue.js 3** - Progressive JavaScript framework
- **Vite** - Fast build tool
- **TailwindCSS** - Utility-first CSS
- **Pinia** - State management
- **Axios** - HTTP client
- **Leaflet** - Interactive maps

### Infrastructure
- **Docker + Docker Compose** - Containerization
- **Nginx** - Reverse proxy (production)
- **VPS** - Deployment target (Hetzner/OVH/Hostinger)

## Project Structure

```
TEDI_data/
├── backend/                # Flask backend API
│   ├── app/
│   │   ├── models/        # SQLAlchemy models
│   │   ├── routes/        # API endpoints
│   │   ├── services/      # Business logic
│   │   └── utils/         # Utilities
│   ├── migrations/        # Alembic migrations
│   ├── scripts/           # Utility scripts
│   ├── tests/             # Unit tests
│   ├── config.py          # Configuration
│   ├── requirements.txt   # Python dependencies
│   └── run.py             # Application entry point
├── frontend/              # Vue.js frontend
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── views/         # Page components
│   │   ├── stores/        # Pinia stores
│   │   ├── services/      # API services
│   │   ├── router/        # Vue Router
│   │   └── assets/        # Static assets
│   ├── package.json       # Node dependencies
│   └── vite.config.js     # Vite configuration
├── docker/                # Docker configurations
│   ├── init-db.sql        # PostgreSQL init script
│   └── nginx.conf         # Nginx configuration
├── data/                  # Data directory
│   ├── raw/               # Raw datasets
│   ├── processed/         # Processed datasets
│   └── seeds/             # Seed data
├── docs/                  # Documentation
├── docker-compose.yml     # Docker Compose configuration
└── README.md              # This file
```

## Prerequisites

- **Docker** and **Docker Compose** (v2.0+)
- **Git**
- **Node.js 20+** (for local development)
- **Python 3.11+** (for local development)

## Quick Start with Docker

### 1. Clone the Repository
```bash
git clone <repository-url>
cd TEDI_data
```

### 2. Start All Services
```bash
docker-compose up -d
```

This will start:
- PostgreSQL with PostGIS (port 5432)
- Redis (port 6379)
- Backend API (port 5000)
- Celery Worker
- Frontend (port 3000)

### 3. Initialize Database
```bash
# Enter backend container
docker exec -it tedi_backend bash

# Run database migrations
flask db upgrade

# Seed initial data
python scripts/seed_database.py

# Exit container
exit
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Documentation**: http://localhost:5000/api/docs

### 5. Get Demo API Key
After seeding, a demo API key is created:
- Email: `demo@tedi.africa`
- Check console output after running seed script for the API key

## Local Development (Without Docker)

### Backend Setup

1. **Create Virtual Environment**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. **Setup PostgreSQL with PostGIS**
```bash
# Install PostgreSQL and PostGIS
sudo apt-get install postgresql-15 postgresql-15-postgis-3

# Create database
sudo -u postgres psql
CREATE DATABASE tedi_db;
CREATE USER tedi_user WITH PASSWORD 'tedi_password';
GRANT ALL PRIVILEGES ON DATABASE tedi_db TO tedi_user;
\c tedi_db
CREATE EXTENSION postgis;
\q
```

5. **Run Migrations**
```bash
flask db upgrade
```

6. **Seed Database**
```bash
python scripts/seed_database.py
```

7. **Start Backend**
```bash
python run.py
```

### Frontend Setup

1. **Install Dependencies**
```bash
cd frontend
npm install
```

2. **Configure Environment**
```bash
# Create .env file
echo "VITE_API_URL=http://localhost:5000/api/v1" > .env
```

3. **Start Development Server**
```bash
npm run dev
```

## API Documentation

### Authentication
All API requests require an API key in the header:
```bash
curl -H "X-API-KEY: your-api-key" http://localhost:5000/api/v1/agriculture/communes
```

### Key Endpoints

#### Agriculture
```bash
# List all communes
GET /api/v1/agriculture/communes

# List all crops
GET /api/v1/agriculture/crops

# Get agriculture index with filters
GET /api/v1/agriculture/index?commune_id=1&year=2023

# Get specific statistic
GET /api/v1/agriculture/index/{commune_id}/{crop_id}/{year}
```

#### API Keys Management
```bash
# Create new API key
POST /api/v1/auth/keys
{
  "name": "My API Key",
  "owner_name": "John Doe",
  "owner_email": "john@example.com",
  "scopes": ["agriculture:read"]
}

# Validate API key
GET /api/v1/auth/validate?key=your-key

# List keys by email
GET /api/v1/auth/keys?email=john@example.com
```

### Interactive API Documentation
Visit http://localhost:5000/api/docs for the full Swagger/OpenAPI documentation.

## Database Schema

### Core Tables
- `countries` - Countries data
- `regions` - Regions/Departments
- `communes` - Communes with PostGIS geometry
- `crops` - Crop types
- `agri_stats` - Agriculture statistics (production, yield, prices)
- `data_sources` - Data source metadata
- `dataset_versions` - Dataset version tracking
- `api_keys` - API key management

## Data Sources

### Agriculture
- **FAOSTAT**: https://www.fao.org/faostat/en/
- **World Bank Agriculture**: https://data.worldbank.org/topic/agriculture
- **INStaD Benin**: https://instad.bj/
- **data.gouv.bj**: https://data.gouv.bj/

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## Deployment

### Production with Docker Compose

1. **Update Environment Variables**
```bash
# Edit docker-compose.yml for production
# Change FLASK_ENV to production
# Set strong passwords and secret keys
```

2. **Enable Nginx**
```bash
docker-compose --profile production up -d
```

3. **SSL/TLS Certificate**
```bash
# Use Let's Encrypt or your certificate provider
# Update nginx.conf with SSL configuration
```

### VPS Deployment Guide
See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed VPS deployment instructions.

## Common Commands

### Docker
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart backend

# Rebuild containers
docker-compose up -d --build
```

### Database
```bash
# Create migration
docker exec -it tedi_backend flask db migrate -m "description"

# Apply migrations
docker exec -it tedi_backend flask db upgrade

# Rollback migration
docker exec -it tedi_backend flask db downgrade
```

### Backend
```bash
# Enter backend container
docker exec -it tedi_backend bash

# Run Python shell
docker exec -it tedi_backend flask shell

# Seed database
docker exec -it tedi_backend python scripts/seed_database.py
```

## Troubleshooting

### Port Conflicts
If ports 5000, 3000, or 5432 are already in use:
```bash
# Check what's using the port
sudo lsof -i :5000

# Kill the process or change ports in docker-compose.yml
```

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Test connection
docker exec -it tedi_postgres psql -U tedi_user -d tedi_db
```

### Frontend Build Issues
```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

- **Website**: https://tedi.africa
- **Email**: contact@tedi.africa
- **GitHub**: https://github.com/tedi-africa

## Roadmap

- [x] Phase 1: Agriculture MVP (Benin)
- [ ] Phase 2: Real Estate Index
- [ ] Phase 3: Employment Index
- [ ] Phase 4: Business Index
- [ ] Phase 5: Cross-index correlations & AI licensing

---

Made with ❤️ by the TEDI Team
