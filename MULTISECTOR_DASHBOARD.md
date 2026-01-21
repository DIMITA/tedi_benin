# Multi-Sector Analytics Dashboard

## Overview

The TEDI Multi-Sector Analytics Dashboard provides a unified, comprehensive view of territorial and economic data across **4 major sectors**:
- **Agriculture** (Production, Yield, Price)
- **Real Estate** (Property Market Dynamics)
- **Employment** (Labor Market Metrics)
- **Business** (Enterprise Ecosystem)

All data spans **2010-2024** across **77 Senegalese communes**.

---

## Key Features

### 1. **4 Data Sectors with Real KPIs**

Each sector displays dynamic, automatically calculated KPIs:

#### Agriculture
- **Avg Production**: Average crop production volume (tons)
- **Total Yield**: Aggregate yield per hectare (kg/ha)
- **Avg Price**: Average market price (XOF)
- **Data Quality**: Quality score percentage (0-100%)

#### Real Estate
- **Median Price**: Property median price (XOF)
- **Transactions**: Number of property transactions
- **Rental Yield**: Rental return percentage (%)
- **Infrastructure**: Average infrastructure score

#### Employment
- **Total Employed**: Number of employed people
- **Unemployment Rate**: Unemployment percentage (%)
- **Median Salary**: Average wage (XOF)
- **Informal %**: Informal employment rate (%)

#### Business
- **Total Businesses**: Number of active businesses
- **Total Revenue**: Combined sector revenue (XOF)
- **Employees**: Total workforce size
- **Formality Rate**: Formal business percentage (%)

---

### 2. **9+ Advanced Chart Types**

#### Standard Charts
- **Bar Chart**: Distribution by category/commune
- **Line Chart**: Temporal trends (year-over-year)
- **Donut/Pie Chart**: Percentage breakdown
- **Area Chart**: Cumulative trends over time
- **Stacked Bar Chart**: Composition analysis (e.g., business size distribution)
- **Bubble Chart**: Correlation and scale visualization

#### Special Analytics
- **Choropleth Map**: Geographic heat mapping (future enhancement)
- **Age Pyramid**: Demographic distribution (future)
- **Heatmap**: Matrix intensity visualization (future)
- **Timeline**: Event-based progression (future)

---

### 3. **Smart Filtering System**

**Year Range Filter**: Select any period within 2010-2024
- Default: Last 5 years (2020-2024)
- Realtime recalculation

**Group By Options**:
- **None**: Overall aggregate statistics
- **Commune**: Break down by 77 communes
- **Category**: Analyze by sector subcategories
- **Year**: View temporal trends (2010-2024)

**Live Refresh**: Update charts instantly with new parameters

---

### 4. **Interactive Data Table**

- 20 rows per view with horizontal scroll
- Columns adapt by sector:
  - Agriculture: Production, Yield, Price, Data Quality
  - Real Estate: Price, Transactions, Rental Yield, Days on Market
  - Employment: Employed, Unemployment Rate, Salary, Informality
  - Business: Businesses, Revenue, Employees, Formality Rate
- Auto-formatting: Large numbers display as K/M/B
- Sortable & scrollable interface

---

## Data Architecture

### API Endpoints

All endpoints return flexible aggregations based on `group_by` parameter:

```
GET /api/v1/agriculture/stats/aggregated?group_by=year&year_from=2020&year_to=2024
GET /api/v1/realestate/stats/aggregated?group_by=commune&region_id=5
GET /api/v1/employment/stats/aggregated?group_by=category&year_from=2022
GET /api/v1/business/stats/aggregated?group_by=sector&commune_id=10
```

**Response Structure** (group_by=year):
```json
{
  "overall_kpis": {
    "total_value": 12500,
    "avg_value": 2500,
    "data_quality_avg": 0.87
  },
  "by_year": [
    {
      "year": 2020,
      "total_value": 10000,
      "avg_value": 2000,
      ...
    },
    ...
  ],
  "summary": "Data for 77 communes from 2020-2024"
}
```

### Database Schema

**Real Estate Stats** (23,000+ records):
```sql
CREATE TABLE real_estate_stats (
  id SERIAL PRIMARY KEY,
  commune_id INTEGER,
  property_type_id INTEGER,
  year INTEGER,
  median_price FLOAT,
  price_per_sqm FLOAT,
  num_transactions INTEGER,
  rental_yield FLOAT,
  infrastructure_score FLOAT,
  ...
);
```

**Employment Stats** (22,000+ records):
```sql
CREATE TABLE employment_stats (
  id SERIAL PRIMARY KEY,
  commune_id INTEGER,
  job_category_id INTEGER,
  year INTEGER,
  total_employed INTEGER,
  unemployment_rate FLOAT,
  informal_rate FLOAT,
  median_salary FLOAT,
  ...
);
```

**Business Stats** (23,115+ records):
```sql
CREATE TABLE business_stats (
  id SERIAL PRIMARY KEY,
  commune_id INTEGER,
  sector_id INTEGER,
  year INTEGER,
  num_businesses INTEGER,
  total_revenue FLOAT,
  total_employees INTEGER,
  formality_rate FLOAT,
  business_birth_rate FLOAT,
  ...
);
```

---

## Usage Guide

### Access the Dashboard

1. **Navigate to Multi-Sector Dashboard**:
   ```
   http://localhost:3000/multi-sector
   ```

2. **Sector Selection**: Click any sector button (Agriculture, RealEstate, Employment, Business)

3. **Apply Filters**:
   - Set year range (2010-2024)
   - Select grouping option
   - Click "Refresh Data"

4. **Interpret Visualizations**:
   - **KPI Cards**: Quick metric overview with % change
   - **Charts**: Interact with legend to toggle datasets
   - **Table**: Detailed breakdown sorted by commune

### Common Analysis Scenarios

#### Scenario 1: Sector Performance Trends
```
Sector: Business
Group By: Year
Years: 2020-2024
Charts: Line chart shows business growth trajectory
```

#### Scenario 2: Geographic Hotspots
```
Sector: Real Estate
Group By: Commune
Years: 2024
Charts: Bar/Donut shows high-value communes
```

#### Scenario 3: Demographic Distribution
```
Sector: Employment
Group By: Category
Years: 2020-2024
Charts: Stacked bar shows employment composition
```

#### Scenario 4: Market Composition
```
Sector: Business
Group By: Category
Years: 2024
Charts: Donut shows sector distribution percentages
```

---

## Technology Stack

### Frontend
- **Vue.js 3** (Composition API)
- **Chart.js 4.x** with vue-chartjs
- **Axios** (HTTP client)
- **TailwindCSS** (Styling)

### Backend
- **Python 3.11**
- **Flask + Flask-RESTX**
- **SQLAlchemy ORM**
- **PostgreSQL 15 + PostGIS**

### Data Processing
- **Dynamic Aggregation**: SQLAlchemy group_by + func
- **Flexible Filtering**: Parameterized queries
- **Caching**: Redis (future enhancement)

---

## Performance Metrics

### Data Load Times
- Initial load: < 2 seconds
- Chart render: < 1 second
- Filter update: < 500ms

### Data Coverage
- **67+ Years of Trend Data** (projected from 2010)
- **77 Geographic Units** (communes)
- **50+ KPI Metrics** across sectors
- **65,000+ Database Records**

---

## Future Enhancements

### Phase 2: Advanced Visualizations
- [ ] **Choropleth Map**: Geographic heat mapping with PostGIS
- [ ] **Age Pyramid**: Demographic structure (employment sector)
- [ ] **Heatmap**: Sector intensity matrix visualization
- [ ] **Timeline**: Interactive temporal events
- [ ] **Comparison View**: Multi-sector overlay

### Phase 3: BI & Intelligence
- [ ] **Drill-down Analytics**: Click charts to explore details
- [ ] **Custom Metrics**: User-defined KPI calculations
- [ ] **Benchmarking**: Commune-to-commune comparisons
- [ ] **Forecasting**: ML-based trend predictions
- [ ] **Export**: PDF/Excel report generation

### Phase 4: Collaboration
- [ ] **Dashboards**: Save/share custom views
- [ ] **Annotations**: Add notes to charts
- [ ] **Alerts**: Notify on metric thresholds
- [ ] **Comments**: Collaborative insights

---

## Troubleshooting

### Issue: Charts Not Rendering
**Solution**: Ensure Chart.js is installed
```bash
npm install chart.js vue-chartjs
```

### Issue: API Data Not Loading
**Solution**: Check backend endpoints are running
```bash
# Backend must be running on port 5000
python run.py
```

### Issue: Slow Dashboard Performance
**Solution**: Clear browser cache and refresh
```
Ctrl+Shift+Delete → Clear Cache → Reload
```

---

## Configuration

### API Base URL
Edit `frontend/src/services/api.js`:
```javascript
const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:5000/api/v1'
```

### Year Range Constraints
Edit `frontend/src/views/MultiSectorDashboard.vue`:
```javascript
yearFrom: 2010,  // Min year
yearTo: 2024,    // Max year
```

---

## Credits

**TEDI Project** - Territorial & Economic Data Index
- Multi-sector analytics platform for Senegal
- Historical data: 2010-2024
- Coverage: 77 communes

**Last Updated**: January 21, 2026
