# TEDI - Quick Start Guide

## 🚀 Launch in 5 Minutes

### Prerequisites
- Docker & Docker Compose installed
- Ports 5000, 3000, 5432, 6379 available

### Step 1: Start Services
```bash
cd TEDI_data
docker-compose up -d
```

Wait ~30 seconds for all services to start.

### Step 2: Initialize Database
```bash
docker exec -it tedi_backend python scripts/seed_database.py
```

**Save the demo API key shown in the output!**

### Step 3: Access the Application

**Frontend**: http://localhost:3000
- Login with the demo API key

**Backend API**: http://localhost:5000
- Health check: http://localhost:5000/health
- API Docs: http://localhost:5000/api/docs

### Step 4: Test the API

```bash
# Replace YOUR_API_KEY with the demo key from Step 2
export API_KEY="your-demo-api-key-here"

# List communes
curl -H "X-API-KEY: $API_KEY" http://localhost:5000/api/v1/agriculture/communes

# List crops
curl -H "X-API-KEY: $API_KEY" http://localhost:5000/api/v1/agriculture/crops

# Get agriculture index
curl -H "X-API-KEY: $API_KEY" http://localhost:5000/api/v1/agriculture/index
```

## 📊 What You Have

- ✅ 1 country (Bénin)
- ✅ 12 regions/departments
- ✅ 77 communes
- ✅ 10 crops (including Maize, Rice, Cassava)
- ✅ API with authentication
- ✅ Dashboard interface

## 🛠️ Common Commands

### View Logs
```bash
docker-compose logs -f
```

### Stop Services
```bash
docker-compose down
```

### Restart a Service
```bash
docker-compose restart backend
```

### Access Database
```bash
docker exec -it tedi_postgres psql -U tedi_user -d tedi_db
```

### Enter Backend Shell
```bash
docker exec -it tedi_backend bash
```

## ❌ Troubleshooting

### Services won't start
```bash
# Check what's using the ports
sudo lsof -i :5000
sudo lsof -i :3000

# Or change ports in docker-compose.yml
```

### Database connection error
```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Frontend not loading
```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose up -d --build frontend
```

## 📝 Next Steps

1. **Explore the API**: Visit http://localhost:5000/api/docs
2. **Check the Dashboard**: Login at http://localhost:3000
3. **Add Sample Data**: Create agriculture statistics entries
4. **Read Full Docs**: See README.md for detailed documentation

## 🎯 MVP Features

Currently implemented:
- ✅ PostgreSQL + PostGIS database
- ✅ Flask REST API with authentication
- ✅ Vue.js dashboard
- ✅ Geographic data (communes with coordinates)
- ✅ Crop database
- ✅ API documentation (Swagger)

Ready to add:
- [ ] Real agriculture production data
- [ ] Interactive map with Leaflet
- [ ] Data visualization charts
- [ ] Data export (CSV, JSON)

## 🆘 Need Help?

1. Check PROJECT_STATUS.md for implementation details
2. See README.md for full documentation
3. Review CLAUDE.md for technical context
4. Open an issue on GitHub

---

**Happy Coding! 🚀**
