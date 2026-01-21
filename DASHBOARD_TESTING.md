# Dashboard Implementation - Testing Guide

## Test Execution Plan

### Phase 1: Backend Data Loading Tests

#### Test 1.1: Data Loader Execution
```bash
cd backend
python scripts/load_historical_agriculture_data.py
```

**Expected Results**:
- ✅ Script starts without errors
- ✅ Processes all 77 communes
- ✅ Creates 15,000+ statistics entries
- ✅ Completes in 1-2 minutes
- ✅ Shows database summary

#### Test 1.2: Data Integrity
```bash
python -c "
from app import create_app, db
from app.models.agriculture import AgriStats
from app.models.geo import Commune
from app.models.agriculture import Crop

app = create_app('development')
with app.app_context():
    # Count records
    total = AgriStats.query.count()
    communes_with_data = db.session.query(AgriStats.commune_id).distinct().count()
    crops_with_data = db.session.query(AgriStats.crop_id).distinct().count()
    years = sorted(set(s.year for s in AgriStats.query.all()))
    
    print(f'Total Records: {total}')
    print(f'Communes with data: {communes_with_data}')
    print(f'Crops with data: {crops_with_data}')
    print(f'Years: {min(years)}-{max(years)}')
    
    # Verify some data
    sample = AgriStats.query.first()
    if sample:
        print(f'Sample: {sample.commune.name} / {sample.crop.name} / {sample.year}')
        print(f'  Production: {sample.production_tonnes}t')
        print(f'  Yield: {sample.yield_tonnes_per_ha}t/ha')
        print(f'  Price: {sample.price_per_kg}XOF/kg')
"
```

**Expected Results**:
- ✅ Total Records: 15,000+ (77 communes × 10+ crops × 15 years)
- ✅ Communes with data: 77
- ✅ Crops with data: 10+
- ✅ Years: 2010-2024
- ✅ Sample data has all metrics

### Phase 2: API Tests

#### Test 2.1: Health Check
```bash
curl http://localhost:5000/api/v1/agriculture/health
```

**Expected**: 200 OK

#### Test 2.2: Test Aggregated Endpoint - All Data
```bash
curl -H "X-API-KEY: your-key" \
  "http://localhost:5000/api/v1/agriculture/stats/aggregated?year_from=2010&year_to=2024"
```

**Expected Results**:
```json
{
  "data": {
    "summary": {
      "total_production_tonnes": > 1000000,
      "average_yield_t_ha": > 0,
      "average_price_xof_kg": > 0,
      "average_quality_score": 0.7-1.0,
      "data_points": 15000+
    },
    "by_commune": [...],  // 77 communes
    "by_crop": [...],     // 10+ crops
    "by_year": [...],     // 15 years
    "trends": {
      "production_change_pct": not null
    }
  }
}
```

#### Test 2.3: Filter by Commune
```bash
# Get commune ID first
curl -H "X-API-KEY: your-key" \
  "http://localhost:5000/api/v1/agriculture/communes" | jq '.[0].id'

# Then use it
curl -H "X-API-KEY: your-key" \
  "http://localhost:5000/api/v1/agriculture/stats/aggregated?commune_id=1&year_from=2010&year_to=2024"
```

**Expected Results**:
- ✅ Returns data for specific commune
- ✅ Total production is lower than all communes
- ✅ Same year range coverage

#### Test 2.4: Filter by Crop
```bash
curl -H "X-API-KEY: your-key" \
  "http://localhost:5000/api/v1/agriculture/stats/aggregated?crop_id=1&year_from=2010&year_to=2024"
```

**Expected Results**:
- ✅ Returns data for specific crop
- ✅ Production is crop-specific value
- ✅ Data from all communes for that crop

#### Test 2.5: Filter by Year Range
```bash
# Recent years only
curl -H "X-API-KEY: your-key" \
  "http://localhost:5000/api/v1/agriculture/stats/aggregated?year_from=2020&year_to=2024"
```

**Expected Results**:
- ✅ by_year contains only 5 entries (2020-2024)
- ✅ Production values are lower than full range

#### Test 2.6: Filter by Region
```bash
curl -H "X-API-KEY: your-key" \
  "http://localhost:5000/api/v1/agriculture/stats/aggregated?region_id=1&year_from=2010&year_to=2024"
```

**Expected Results**:
- ✅ Returns data for communes in region
- ✅ Production is regional aggregate

### Phase 3: Frontend Tests

#### Test 3.1: Dashboard Page Loads
1. Open http://localhost:8080/dashboard
2. Wait 3-5 seconds for data to load

**Expected Results**:
- ✅ Page renders without JavaScript errors
- ✅ 4 KPI cards display with values
- ✅ Filters are visible and editable
- ✅ Charts area shows (may be loading)

#### Test 3.2: KPI Cards Display
After page loads:
- ✅ "Total Production" shows number in format "1,234,567.89"
- ✅ "Average Yield" shows number > 0
- ✅ "Average Price" shows number > 100
- ✅ "Data Quality" shows percentage > 80%
- ✅ Each card has trend indicator (↑ or ↓)
- ✅ Each trend shows percentage change

#### Test 3.3: Charts Render
Wait 5 seconds for charts to render:
- ✅ Production Trend: Line chart with upward trend
- ✅ Yield Evolution: Line chart with improvement
- ✅ Price Trend: Line chart showing price changes
- ✅ Top Crops: Horizontal bar chart with 10 crops

#### Test 3.4: Year Filter
1. Change "Start Year" to 2015
2. Wait 2-3 seconds

**Expected Results**:
- ✅ KPI cards update with new values
- ✅ Charts update to show 2015-2024 only
- ✅ Production trends shift upward (different baseline)

#### Test 3.5: Commune Filter
1. Select "Abomey-Calavi" from Commune dropdown
2. Wait 2-3 seconds

**Expected Results**:
- ✅ KPI cards show commune-specific values (much smaller)
- ✅ Charts update to show only this commune
- ✅ Top communes table shows this commune at top

#### Test 3.6: Crop Filter
1. Select "Maize" from Crop dropdown
2. Wait 2-3 seconds

**Expected Results**:
- ✅ KPI cards show maize-only statistics
- ✅ Charts show maize production trends
- ✅ Top crops table shows maize at top

#### Test 3.7: Multi-Filter Combination
1. Year: 2015-2024
2. Commune: Parakou
3. Crop: Rice
4. Wait 2-3 seconds

**Expected Results**:
- ✅ All filters applied simultaneously
- ✅ Data is intersection of all filters
- ✅ Values are specific to this combination

#### Test 3.8: Reset Filters
1. Set all filters to "All"
2. Year: 2010-2024
3. Wait 2-3 seconds

**Expected Results**:
- ✅ Back to full dataset view
- ✅ KPI cards show largest values
- ✅ All 77 communes in table

#### Test 3.9: Tables Display Correctly
Check "Top Communes by Production" table:
- ✅ Shows 10 communes with highest production
- ✅ Each row has: Name, Production, Area, Yield, Records
- ✅ Numbers are formatted with commas
- ✅ Abomey-Calavi or similar is at top

Check "Top Crops by Production" table:
- ✅ Shows 10 crops with highest production
- ✅ Each row has: Name, Production, Area, Yield, Price
- ✅ Maize or similar is at top

#### Test 3.10: Responsive Design
1. Resize browser window to mobile size (< 640px)
2. Open Dashboard

**Expected Results**:
- ✅ KPI cards stack vertically (1 column)
- ✅ Charts adapt to container
- ✅ Filters still accessible
- ✅ Tables scroll horizontally

### Phase 4: Integration Tests

#### Test 4.1: API to Dashboard Flow
1. Load dashboard
2. Open browser DevTools → Network tab
3. Filter by Commune
4. Observe network requests

**Expected Results**:
- ✅ Request to `/api/v1/agriculture/stats/aggregated`
- ✅ Response includes all summary data
- ✅ Frontend updates without page reload
- ✅ No console errors

#### Test 4.2: Performance Test
1. Dashboard with all data (2010-2024, all communes, all crops)
2. Observe load time

**Expected Results**:
- ✅ Initial load: < 5 seconds
- ✅ Filter change: < 2 seconds
- ✅ Charts render within 3 seconds
- ✅ No lag or freezing

#### Test 4.3: Error Handling
1. Simulate bad API key:
   - Open localStorage in DevTools
   - Change `tedi_api_key` to invalid value
   - Refresh dashboard

**Expected Results**:
- ✅ Shows error message
- ✅ Redirects to login or shows API key input

#### Test 4.4: Data Consistency
1. Load dashboard with filters
2. Call same API directly in curl
3. Compare results

**Expected Results**:
- ✅ Dashboard shows same numbers as API
- ✅ No data transformation discrepancies
- ✅ Formatting matches

---

## Test Checklist

### Data Loading
- [ ] Script runs without errors
- [ ] 15,000+ records created
- [ ] All 77 communes covered
- [ ] All 10+ crops covered
- [ ] Years 2010-2024 complete

### API Functionality
- [ ] Aggregated endpoint returns valid JSON
- [ ] All query parameters work
- [ ] Summary KPIs are calculated correctly
- [ ] by_commune list is sorted
- [ ] by_crop list is sorted
- [ ] by_year list is chronological
- [ ] Trends are calculated correctly

### Dashboard UI
- [ ] Page loads without errors
- [ ] KPI cards display with values
- [ ] Charts render correctly
- [ ] Filters are functional
- [ ] Filters update data in real-time
- [ ] Tables populate and sort
- [ ] Mobile responsive design works

### Data Accuracy
- [ ] KPI values match API directly
- [ ] Trend percentages are correct
- [ ] Top items are actually top by metric
- [ ] No negative or impossible values
- [ ] French number formatting applied

---

## Performance Metrics Target

| Metric | Target | Actual |
|--------|--------|--------|
| Initial page load | < 5s | _____ |
| Filter change | < 2s | _____ |
| Chart render | < 3s | _____ |
| API response time | < 1s | _____ |
| Database query | < 500ms | _____ |

---

## Sign-Off

- [ ] All tests passed
- [ ] No critical bugs found
- [ ] Performance acceptable
- [ ] Ready for production

**Tested by**: _________________  
**Date**: _________________  
**Notes**: 

---

## Quick Commands for Testing

```bash
# 1. Load data
cd backend && python scripts/load_historical_agriculture_data.py

# 2. Start backend
python run.py

# 3. Start frontend (in new terminal)
cd frontend && npm run dev

# 4. Test API
curl -H "X-API-KEY: OHIMu02lxux9uDd0__lKMlR5fNtkMQ35-S8bHWm2l2OMDSzbufMJNf3QufujFlAW" \
  "http://localhost:5000/api/v1/agriculture/stats/aggregated?year_from=2010&year_to=2024" | jq '.'

# 5. Open browser
open http://localhost:8080/dashboard

# 6. Check database
python -c "from app import create_app, db; from app.models.agriculture import AgriStats; app=create_app('development'); 
with app.app_context(): print(f'Records: {AgriStats.query.count()}')"
```

---

**Last Updated**: January 21, 2026
**Test Version**: 1.0
