# Quick Start Guide - New Dashboard with Historical Data

## 🚀 Get Started in 5 Minutes

### Step 1: Load Historical Data
```bash
cd backend
python scripts/load_historical_agriculture_data.py
```

Wait for the script to complete (~1-2 minutes). You'll see:
```
✓ Found 77 communes
✓ Found 10+ crops
✓ Years to cover: 2010-2024 (15 years)
...
✓ Historical data loading complete!
📊 Database Summary:
  • Total statistics entries: 15,XXX
```

### Step 2: Start Backend
```bash
python run.py
# Backend will be running at http://localhost:5000
```

### Step 3: Start Frontend
In another terminal:
```bash
cd frontend
npm run dev
# Frontend will be running at http://localhost:8080
```

### Step 4: Access Dashboard
1. Open http://localhost:8080
2. Login (if needed)
3. Navigate to Dashboard
4. See real KPIs with historical data!

---

## 📊 What's New

### 4 Real KPI Cards
- **Total Production** - All crops combined (tonnes)
- **Average Yield** - How productive the land is (t/ha)
- **Average Price** - Market prices in XOF/kg
- **Data Quality** - Percentage of quality data

### 4 Interactive Charts
- **Production Trend** - See how production changed 2010-2024
- **Yield Evolution** - See productivity improvements
- **Price Trend** - Market price movements
- **Top 10 Crops** - Which crops produce most

### 2 Data Tables
- **Top Communes** - Which areas produce most
- **Top Crops** - Which crops are most important

### Smart Filters
- Select start/end year (2010-2024)
- Filter by commune
- Filter by crop
- All changes apply instantly!

---

## 🔥 Try This

### Example 1: View All Data (2010-2024)
1. Keep "Start Year" = 2010
2. Keep "End Year" = 2024
3. Keep "Commune" = All Communes
4. Keep "Crop" = All Crops
5. See overall trends!

### Example 2: Single Commune Analysis
1. Select "Abomey-Calavi" in Commune dropdown
2. Keep year range 2015-2024
3. See production for just this commune
4. Compare with national average

### Example 3: Crop Comparison
1. Select "Maize" in Crop dropdown
2. Keep all communes
3. Year range 2010-2024
4. Watch maize trends!

### Example 4: Recent Years Focus
1. Start Year = 2020
2. End Year = 2024
3. Watch what's happened recently
4. Compare with earlier trends

---

## 📱 API Usage

### Test in curl/Postman
```bash
# Get all data 2010-2024
curl -H "X-API-KEY: your-api-key" \
  "http://localhost:5000/api/v1/agriculture/stats/aggregated?year_from=2010&year_to=2024"

# Just Abomey-Calavi
curl -H "X-API-KEY: your-api-key" \
  "http://localhost:5000/api/v1/agriculture/stats/aggregated?commune_id=1&year_from=2010&year_to=2024"

# Just Maize crop
curl -H "X-API-KEY: your-api-key" \
  "http://localhost:5000/api/v1/agriculture/stats/aggregated?crop_id=1&year_from=2010&year_to=2024"

# Last 5 years by region
curl -H "X-API-KEY: your-api-key" \
  "http://localhost:5000/api/v1/agriculture/stats/aggregated?region_id=1&year_from=2020"
```

---

## ✅ Verification Checklist

After loading data, verify:
1. [ ] Dashboard loads without errors
2. [ ] KPI cards show numbers (not 0)
3. [ ] Charts render and show lines/bars
4. [ ] Filters respond when changed
5. [ ] Tables populate with commune/crop data
6. [ ] Year dropdown works 2010-2024
7. [ ] Commune dropdown shows all communes
8. [ ] Trends show ↑↓ with percentages
9. [ ] Data quality shows > 80%

---

## 🛠️ Troubleshooting

**Dashboard shows no data?**
- [ ] Did you run `load_historical_agriculture_data.py`?
- [ ] Is backend running on port 5000?
- [ ] Check browser console for errors

**Charts are blank?**
- [ ] Wait 2-3 seconds for data to load
- [ ] Check year range has data (2010-2024)
- [ ] Try different commune/crop filters

**Filters not working?**
- [ ] Refresh the page
- [ ] Check API key in localStorage
- [ ] Try smaller year range first

**API returns error?**
- [ ] Verify API key is correct
- [ ] Check year range format (integers)
- [ ] Make sure commune_id and crop_id exist

---

## 📞 Need Help?

Check these files:
- [DASHBOARD_IMPLEMENTATION.md](./DASHBOARD_IMPLEMENTATION.md) - Full technical details
- [API_SPECIFICATION.md](./06_API_SPECIFICATION.md) - API docs
- [backend/app/routes/agriculture.py](./backend/app/routes/agriculture.py) - Code details

---

**Ready to go!** 🎉
