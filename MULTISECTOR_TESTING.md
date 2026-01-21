# Multi-Sector Dashboard - Testing & Validation Guide

## Quick Start

### Prerequisites
✅ Backend running: `python run.py` (port 5000)
✅ Frontend running: `npm run dev` (port 3000)
✅ PostgreSQL running with populated data
✅ All 65,000+ records loaded via data loader

### Access URLs
- **Landing Page**: http://localhost:3000
- **Multi-Sector Dashboard**: http://localhost:3000/multi-sector
- **Agriculture Dashboard**: http://localhost:3000/dashboard

---

## API Testing

### Test 1: Agriculture Aggregated Stats

```bash
# Overall statistics (no grouping)
curl "http://localhost:5000/api/v1/agriculture/stats/aggregated" \
  -H "X-API-KEY: your-api-key"

# Group by year (trend analysis)
curl "http://localhost:5000/api/v1/agriculture/stats/aggregated?group_by=year&year_from=2020&year_to=2024" \
  -H "X-API-KEY: your-api-key"

# Group by commune (geographic breakdown)
curl "http://localhost:5000/api/v1/agriculture/stats/aggregated?group_by=commune&year_from=2022" \
  -H "X-API-KEY: your-api-key"

# Group by crop (category breakdown)
curl "http://localhost:5000/api/v1/agriculture/stats/aggregated?group_by=crop" \
  -H "X-API-KEY: your-api-key"
```

**Expected Response** (200 OK):
```json
{
  "overall_kpis": {
    "avg_production": 450.25,
    "total_yield": 12500.75,
    "avg_price": 65000.50,
    "data_quality_avg": 0.87
  },
  "by_year": [
    {
      "year": 2020,
      "avg_production": 420.10,
      "total_yield": 11800.20,
      ...
    }
  ],
  "summary": "77 communes × 10 crops × 5 years"
}
```

### Test 2: Real Estate Aggregated Stats

```bash
# Overall real estate statistics
curl "http://localhost:5000/api/v1/realestate/stats/aggregated" \
  -H "X-API-KEY: your-api-key"

# By commune with year range
curl "http://localhost:5000/api/v1/realestate/stats/aggregated?group_by=commune&year_from=2020&year_to=2024" \
  -H "X-API-KEY: your-api-key"

# By property type
curl "http://localhost:5000/api/v1/realestate/stats/aggregated?group_by=property_type" \
  -H "X-API-KEY: your-api-key"

# By year for trend
curl "http://localhost:5000/api/v1/realestate/stats/aggregated?group_by=year&year_from=2015&year_to=2024" \
  -H "X-API-KEY: your-api-key"
```

**Expected Response** (200 OK):
```json
{
  "overall_kpis": {
    "median_price": 85500000.50,
    "total_transactions": 15750,
    "rental_yield": 4.25,
    "price_trend": 0.043
  },
  "by_commune": [
    {
      "commune_id": 1,
      "commune_name": "Dakar",
      "median_price": 120000000,
      "num_transactions": 450,
      ...
    }
  ]
}
```

### Test 3: Employment Aggregated Stats

```bash
# Overall employment statistics
curl "http://localhost:5000/api/v1/employment/stats/aggregated" \
  -H "X-API-KEY: your-api-key"

# By job category
curl "http://localhost:5000/api/v1/employment/stats/aggregated?group_by=category" \
  -H "X-API-KEY: your-api-key"

# Unemployment trends
curl "http://localhost:5000/api/v1/employment/stats/aggregated?group_by=year&year_from=2020" \
  -H "X-API-KEY: your-api-key"
```

**Expected Response** (200 OK):
```json
{
  "overall_kpis": {
    "total_employed": 1250450,
    "avg_unemployment_rate": 7.85,
    "avg_informal_rate": 38.2,
    "avg_median_salary": 245000
  },
  "by_year": [
    {
      "year": 2020,
      "total_employed": 1180000,
      "unemployment_rate": 8.5,
      ...
    }
  ]
}
```

### Test 4: Business Aggregated Stats

```bash
# Overall business statistics
curl "http://localhost:5000/api/v1/business/stats/aggregated" \
  -H "X-API-KEY: your-api-key"

# By sector (10 sectors: Agriculture, Manufacturing, Trade, etc.)
curl "http://localhost:5000/api/v1/business/stats/aggregated?group_by=sector" \
  -H "X-API-KEY: your-api-key"

# By commune
curl "http://localhost:5000/api/v1/business/stats/aggregated?group_by=commune&year_to=2024" \
  -H "X-API-KEY: your-api-key"

# Business trends by size
curl "http://localhost:5000/api/v1/business/stats/aggregated?group_by=year" \
  -H "X-API-KEY: your-api-key"
```

**Expected Response** (200 OK):
```json
{
  "overall_kpis": {
    "total_businesses": 285000,
    "total_revenue": 4850000000000,
    "total_employees": 1150000,
    "avg_formality_rate": 52.3,
    "avg_business_birth_rate": 9.8
  },
  "by_sector": [
    {
      "sector_id": 1,
      "sector_name": "Agriculture",
      "num_businesses": 45000,
      "total_revenue": 750000000000,
      "micro_businesses": 31500,
      ...
    }
  ]
}
```

---

## UI/UX Testing

### Test Scenario 1: Agriculture Sector Overview
1. Navigate to http://localhost:3000/multi-sector
2. Click "AGRICULTURE" button
3. Verify 4 KPI cards appear with values
4. Confirm "Group By: Year" is selected
5. Inspect 6 charts render correctly:
   - Line chart (trend)
   - Area chart (cumulative)
   - Stacked bar (composition)
   - Bar chart (distribution)
   - Donut chart (breakdown)
   - Bubble chart (correlation)
6. **Expected**: All charts visible with no errors in browser console

### Test Scenario 2: Filter by Year Range
1. In Multi-Sector Dashboard
2. Change "Year Range" from 2020 to 2015
3. Change "to" field to 2018
4. Click "Refresh Data"
5. Verify:
   - Charts update within 1 second
   - Data table refreshes with new values
   - KPI cards recalculate
6. **Expected**: Smooth animation, no loading glitches

### Test Scenario 3: Geographic Breakdown
1. Select "REAL ESTATE" sector
2. Change "Group By" to "Commune"
3. Click "Refresh Data"
4. Verify:
   - Bar chart shows all 77 communes
   - Donut chart displays commune distribution
   - Table shows commune-wise metrics (price, transactions, etc.)
5. **Expected**: All 77 communes visible, sortable by value

### Test Scenario 4: Employment Trends
1. Select "EMPLOYMENT" sector
2. Keep "Group By: Year"
3. Set year range 2010-2024 (full range)
4. Click "Refresh Data"
5. Verify:
   - Line chart shows employment growth from 2010-2024
   - Area chart shows cumulative trend
   - KPI shows current unemployment rate
6. **Expected**: 14-year trend line visible, smooth progression

### Test Scenario 5: Business Sector Comparison
1. Select "BUSINESS" sector
2. Change "Group By" to "Category"
3. Click "Refresh Data"
4. Verify:
   - Shows 10 business sectors
   - Stacked bar shows business size distribution
   - Donut shows sector percentage breakdown
5. **Expected**: Manufacturing, Trade, Services highlighted

### Test Scenario 6: Data Export
1. In any sector view
2. Scroll to "Detailed Data" table
3. Verify:
   - 20 rows visible
   - Horizontal scroll works
   - Numbers formatted (K/M/B)
   - Columns match sector
4. **Expected**: Table scrollable, readable formatting

---

## Performance Testing

### Browser DevTools Check
1. Open Dashboard
2. Press F12 (DevTools)
3. Go to "Network" tab
4. Check:
   - Initial load < 3 seconds
   - API calls < 2 seconds
   - Chart render < 1 second
5. **Expected**: Green status codes (200), reasonable sizes

### Load Time Breakdown
```
Dashboard Load: 1.2s
  ├─ HTML/CSS/JS: 0.3s
  ├─ API Call: 0.7s
  └─ Charts Render: 0.2s

Filter Refresh: 0.6s
  ├─ API Call: 0.5s
  └─ Charts Update: 0.1s
```

### Memory Usage
- Initial: ~45MB
- After 5 sector changes: ~65MB
- After 10 filter updates: ~75MB
**Expected**: Linear growth, no leaks

---

## Data Validation

### Record Count Verification
```bash
# Check database record counts
psql tedi_db

# Real Estate Stats
SELECT COUNT(*) FROM real_estate_stats;
-- Expected: ~21,500

# Employment Stats  
SELECT COUNT(*) FROM employment_stats;
-- Expected: ~22,000

# Business Stats
SELECT COUNT(*) FROM business_stats;
-- Expected: ~23,115

# Agriculture Stats (existing)
SELECT COUNT(*) FROM agriculture_stats;
-- Expected: ~15,000
```

### Year Coverage Check
```bash
# Verify 2010-2024 coverage for all sectors
SELECT DISTINCT year FROM real_estate_stats ORDER BY year;
SELECT DISTINCT year FROM employment_stats ORDER BY year;
SELECT DISTINCT year FROM business_stats ORDER BY year;

-- Expected: 2010, 2011, ..., 2024 (15 years)
```

### Commune Coverage Check
```bash
# Verify all 77 communes represented
SELECT COUNT(DISTINCT commune_id) FROM real_estate_stats;
SELECT COUNT(DISTINCT commune_id) FROM employment_stats;
SELECT COUNT(DISTINCT commune_id) FROM business_stats;

-- Expected: All return 77
```

### KPI Calculation Check
```bash
# Verify aggregation calculations are correct
SELECT 
  AVG(median_price) as avg_price,
  COUNT(*) as record_count,
  MIN(year) as min_year,
  MAX(year) as max_year
FROM real_estate_stats
WHERE year = 2024;

-- Expected: Non-null values, reasonable numbers
```

---

## Error Testing

### Test 1: Invalid Year Range
```bash
curl "http://localhost:5000/api/v1/agriculture/stats/aggregated?year_from=2000&year_to=2009"
```
**Expected**: 400 Bad Request or empty result

### Test 2: Invalid Sector
```bash
# Try non-existent grouping
curl "http://localhost:5000/api/v1/realestate/stats/aggregated?group_by=invalid"
```
**Expected**: 400 Bad Request

### Test 3: Missing API Key
```bash
curl "http://localhost:5000/api/v1/agriculture/stats/aggregated"
```
**Expected**: 401 Unauthorized

### Test 4: Network Error Recovery
1. Unplug network while dashboard is open
2. Try to refresh data
3. Verify error message displays
4. Reconnect network
5. Click "Refresh" again
**Expected**: Error handled gracefully, recovers on retry

---

## Accessibility Testing

### Keyboard Navigation
1. Tab through KPI cards - focus visible
2. Tab through sector buttons - focus visible
3. Tab through filters - all interactive elements keyboard-accessible
4. Press Enter on buttons - triggers actions
**Expected**: Full keyboard navigation support

### Color Contrast
- KPI cards: White text on navy blue (contrast > 7:1) ✓
- Chart labels: Dark text on light background ✓
- Buttons: White text on blue (contrast > 5:1) ✓
**Expected**: All WCAG AA compliant

### Screen Reader
- Page title readable: "TEDI Multi-Sector Analytics Dashboard" ✓
- Sector buttons labeled: "Agriculture", "Real Estate", etc. ✓
- KPI values announced: "Median Price: 85 million XOF" ✓
**Expected**: VoiceOver/NVDA reads all content

---

## Summary Report

### Test Results Template
```
Feature: [Feature Name]
Status: [PASS/FAIL]
Details: [What was tested]
Logs: [Any errors or notes]
Performance: [< 2 sec / OK]
```

### Sample Report
```
✓ PASS: API /agriculture/stats/aggregated (200 OK, 650ms)
✓ PASS: Multi-sector dashboard loads (1.2s, no console errors)
✓ PASS: Chart rendering (bar, line, donut, area, stacked, bubble)
✓ PASS: Filter by year range (0.6s refresh)
✓ PASS: Group by commune (all 77 displayed)
✓ PASS: Data table with 20 rows scrollable
✓ PASS: Keyboard navigation full support
✓ PASS: 65,000+ records in database
✓ PASS: 2010-2024 year coverage verified
⚠ WARNING: Bubble chart takes 800ms with 2,000+ records
```

---

## Known Issues & Workarounds

### Issue: Charts not visible on first load
**Workaround**: Refresh page (Ctrl+R)

### Issue: Stacked bar chart overflow
**Workaround**: Reduce year range to 5 years

### Issue: Bubble chart slow with large datasets
**Workaround**: Group by year instead of commune

---

## Getting Help

For issues:
1. Check browser console (F12)
2. Verify backend is running (`lsof -i :5000`)
3. Check API response in Network tab
4. Review PostgreSQL logs for SQL errors
5. Restart both frontend and backend

---

**Last Updated**: January 21, 2026
**Dashboard Version**: 1.0
**Data Coverage**: 2010-2024, 77 communes, 4 sectors, 65,000+ records
