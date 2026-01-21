# Dashboard Page Documentation

## Overview

The Dashboard page (`DashboardView.vue`) serves as the landing page and central hub for the TEDI platform. It provides a high-level overview of available data, quick statistics, and navigation to key features.

**Route**: `/dashboard` (default route `/`)

---

## Purpose

The Dashboard serves multiple functions:

1. **Entry Point**: First page users see after login/authentication
2. **Data Overview**: Quick statistics on available data (communes, crops, data points)
3. **Navigation Hub**: Quick links to main features (Agriculture Data, Map, API Keys)
4. **System Health Indicator**: Shows real-time data availability from the ingestion system

---

## Features

### 1. Statistics Cards

The dashboard displays three key metrics in visually distinct cards:

#### Total Communes
- **Description**: Number of communes (municipalities) in the database
- **Data Source**: Loaded from `/api/v1/agriculture/communes`
- **Color**: Primary (green) - `text-tedi-primary`
- **Updates**: Real-time on page load

#### Total Crops
- **Description**: Number of different crop types tracked in the system
- **Data Source**: Loaded from `/api/v1/agriculture/crops`
- **Color**: Secondary (blue) - `text-tedi-secondary`
- **Updates**: Real-time on page load

#### Data Points
- **Description**: Total number of potential data combinations (communes × crops)
- **Calculation**: `communes.length * crops.length`
- **Color**: Accent (amber) - `text-tedi-accent`
- **Significance**: Represents the scale of the dataset

**Example Display**:
```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Total Communes  │  │  Total Crops    │  │  Data Points    │
│                 │  │                 │  │                 │
│      77         │  │       45        │  │     3,465       │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### 2. Welcome Section

Provides:
- Brief introduction to TEDI
- Platform tagline: "Comprehensive platform for territorial and economic data across Africa"
- Starting point: Currently focused on Benin, with plans for continental expansion

### 3. Quick Navigation

Three prominent links to main features:
1. **Explore Agriculture Data** (`/agriculture`) - View crop statistics by commune
2. **View Interactive Map** (`/map`) - Geographic visualization of commune data
3. **Manage API Keys** (`/api-keys`) - Create and manage API authentication

---

## Integration with Backend Data Ingestion System

### How the Dashboard Reflects Scheduler Activity

The Dashboard is the first place users see the results of the automated data ingestion scheduler. Here's how they connect:

#### 1. Real-Time Data Availability

When the scheduler successfully ingests data:
- **Communes**: Updated when OSM connector adds new commune boundaries
- **Crops**: Updated when FAOSTAT or World Bank add new crop types to tracking
- **Data Points**: Automatically recalculated based on current communes × crops

#### 2. Data Freshness

The statistics displayed come directly from tables populated by the scheduler:
```
Scheduler Runs → Data Ingested → Tables Updated → Dashboard Queries Tables → Stats Displayed
```

**Data Sources for Dashboard Stats**:
```javascript
// Dashboard fetches from these endpoints:
api.agriculture.getCommunes()  // → communes table (from OSM ingestion)
api.agriculture.getCrops()      // → crops table (from FAOSTAT/World Bank)

// These tables are populated by:
// - tasks.realestate.ingest_osm → communes
// - tasks.agriculture.ingest_faostat → crops
// - tasks.agriculture.ingest_worldbank → crops + agri_stats
```

#### 3. Ingestion System Health Indicator

While not explicitly shown yet, the Dashboard can be extended to show ingestion system health:

**Planned Enhancement - System Status Card**:
```vue
<div class="card border-l-4 border-green-500">
  <h3>Data Ingestion Status</h3>
  <div>
    <span>✅ Last successful update: 2 hours ago</span>
    <span>📊 Next scheduled check: in 4 hours</span>
    <span>🔄 Active sources: FAOSTAT, World Bank, ILOSTAT, OSM</span>
  </div>
</div>
```

This would query `/api/v1/dataset-versions` to show:
- Last successful ingestion timestamps
- Next scheduled checks
- Source reliability scores
- Recent ingestion logs

#### 4. Data Quality Tracking

Each data point displayed has an associated quality score from the ingestion system:

**In AgriStats table**:
```sql
SELECT
  COUNT(*) as data_points,
  AVG(data_quality_score) as avg_quality
FROM agri_stats
WHERE data_quality_score IS NOT NULL;
```

**Current Implementation**: Not displayed on dashboard (future enhancement)
**Backend Source**: `data_quality_score` field populated by connectors during ingestion

---

## Technical Implementation

### Frontend Component Structure

```vue
DashboardView.vue
├── Statistics Cards Section
│   ├── Total Communes Card
│   ├── Total Crops Card
│   └── Data Points Card (computed)
├── Welcome Section
│   ├── Platform Description
│   └── Quick Links
└── Script Setup (Composition API)
    ├── State Management (ref)
    ├── Lifecycle Hooks (onMounted)
    └── API Calls
```

### State Management

```javascript
const stats = ref({
  communes: 0,      // Loaded from API
  crops: 0,         // Loaded from API
  dataPoints: 0     // Calculated: communes * crops
})
```

### Data Loading Flow

```javascript
onMounted(async () => {
  try {
    // Parallel API calls for performance
    const [communesRes, cropsRes] = await Promise.all([
      api.agriculture.getCommunes(),
      api.agriculture.getCrops(),
    ])

    // Update state
    stats.value.communes = communesRes.data.length
    stats.value.crops = cropsRes.data.length
    stats.value.dataPoints = stats.value.communes * stats.value.crops
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
})
```

**Performance Optimization**: Uses `Promise.all()` to fetch both endpoints simultaneously instead of sequentially.

### API Integration

The Dashboard calls these backend endpoints:

#### GET `/api/v1/agriculture/communes`
**Returns**:
```json
[
  {
    "id": 1,
    "name": "Cotonou",
    "region_id": 6,
    "region": {
      "id": 6,
      "name": "Littoral",
      "country_id": 1
    },
    "center_lat": 6.3654,
    "center_lon": 2.4183,
    "population": 679012,
    "area_km2": 79.0
  },
  ...
]
```

#### GET `/api/v1/agriculture/crops`
**Returns**:
```json
[
  {
    "id": 1,
    "name": "Maize",
    "category": "Cereals",
    "scientific_name": "Zea mays"
  },
  {
    "id": 2,
    "name": "Cassava",
    "category": "Roots and Tubers",
    "scientific_name": "Manihot esculenta"
  },
  ...
]
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│              Scheduler → Dashboard Data Flow                │
└─────────────────────────────────────────────────────────────┘

STEP 1: Scheduler Runs (Every 6 Hours)
   ├─→ tasks.realestate.ingest_osm
   │   └─→ Fetches commune boundaries from OpenStreetMap
   │       └─→ Inserts into osm_buildings, osm_amenities tables
   │           └─→ Updates communes table with new data
   │
   ├─→ tasks.agriculture.ingest_faostat
   │   └─→ Fetches crop production data from FAOSTAT
   │       └─→ Creates crop records if new crops discovered
   │           └─→ Inserts into agri_stats table
   │
   └─→ tasks.agriculture.ingest_worldbank
       └─→ Fetches agricultural indicators
           └─→ Updates crops and agri_stats tables

STEP 2: Dashboard Page Loads
   ├─→ User navigates to /dashboard
   │
   ├─→ onMounted() lifecycle hook fires
   │   ├─→ Calls GET /api/v1/agriculture/communes
   │   │   └─→ Backend queries communes table
   │   │       └─→ Returns array of commune objects
   │   │
   │   └─→ Calls GET /api/v1/agriculture/crops
   │       └─→ Backend queries crops table
   │           └─→ Returns array of crop objects
   │
   └─→ Stats computed and displayed
       ├─→ communes: communesRes.data.length
       ├─→ crops: cropsRes.data.length
       └─→ dataPoints: communes * crops

RESULT: User sees up-to-date statistics from latest ingestion
```

---

## Usage Scenarios

### Scenario 1: First-Time User

**Experience**:
1. User logs in / lands on dashboard
2. Sees statistics cards load (animated counting effect could be added)
3. Reads welcome text to understand TEDI's purpose
4. Clicks "Explore Agriculture Data" to start exploring

**What They See**:
- Real-time data count (e.g., "77 communes available")
- System appears active and populated with data
- Clear next steps for navigation

### Scenario 2: Regular User Checking for Updates

**Experience**:
1. User returns to dashboard daily/weekly
2. Notices "Total Communes" increased from 77 to 79
3. Indicates new data was ingested from OSM
4. Clicks through to explore new commune data

**Behind the Scenes**:
- OSM ingestion task ran overnight
- Added 2 new communes to the database
- Dashboard automatically reflects the change
- No manual update needed

### Scenario 3: Developer Monitoring System Health

**Current State**: Limited visibility
**Desired State** (Future Enhancement):

```vue
<div class="card">
  <h3>System Health</h3>
  <div class="space-y-2">
    <div class="flex items-center">
      <span class="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
      <span>FAOSTAT: Last updated 2h ago (Reliability: 92%)</span>
    </div>
    <div class="flex items-center">
      <span class="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
      <span>World Bank: Last updated 3h ago (Reliability: 85%)</span>
    </div>
    <div class="flex items-center">
      <span class="w-3 h-3 bg-yellow-500 rounded-full mr-2"></span>
      <span>ILOSTAT: Last checked 6h ago, no new data</span>
    </div>
    <div class="flex items-center">
      <span class="w-3 h-3 bg-red-500 rounded-full mr-2"></span>
      <span>OSM: Last attempt failed (checking again in 4h)</span>
    </div>
  </div>
</div>
```

This would query the `IngestionLog` and `DatasetVersion` tables to show system health.

---

## Extending the Dashboard

### Recommended Enhancements

#### 1. Data Freshness Indicators

Show when data was last updated:

```vue
<div class="card">
  <h3>Data Freshness</h3>
  <div>
    <p>Agriculture Data: Updated 2 hours ago</p>
    <p>Employment Data: Updated 5 hours ago</p>
    <p>Real Estate Data: Updated 1 day ago</p>
  </div>
</div>
```

**Implementation**:
```javascript
// Query dataset versions
const freshness = await api.meta.getDataFreshness()
// Returns last_checked_at for each vertical
```

#### 2. Recent Ingestion Activity

Show recent ingestion logs:

```vue
<div class="card">
  <h3>Recent Updates</h3>
  <ul>
    <li>✅ FAOSTAT: Added 150 new crop records (2h ago)</li>
    <li>✅ World Bank: Updated economic indicators (3h ago)</li>
    <li>⏭️ ILOSTAT: No changes detected (6h ago)</li>
    <li>❌ OSM: Connection timeout, retrying (8h ago)</li>
  </ul>
</div>
```

**Implementation**:
```javascript
// Query recent ingestion logs
const logs = await api.meta.getIngestionLogs({ limit: 10 })
```

#### 3. Data Coverage Heatmap

Visual representation of data availability:

```vue
<div class="card">
  <h3>Data Coverage</h3>
  <div class="grid grid-cols-12 gap-1">
    <!-- Each cell represents one commune -->
    <div
      v-for="commune in communes"
      :class="{
        'bg-green-500': commune.data_completeness > 0.8,
        'bg-yellow-500': commune.data_completeness > 0.5,
        'bg-red-500': commune.data_completeness < 0.5
      }"
      class="h-4 rounded"
    />
  </div>
</div>
```

#### 4. Trend Charts

Show data growth over time:

```javascript
// Chart showing commune count over time
const communeGrowth = await api.meta.getCommuneGrowth()
// Returns: [{ date: '2026-01-01', count: 70 }, ...]

// Render with Chart.js or similar
```

#### 5. Quick Search

Add a search bar to quickly find communes or crops:

```vue
<div class="card">
  <input
    v-model="searchQuery"
    placeholder="Search communes or crops..."
    class="input-field"
  />
</div>
```

---

## Performance Considerations

### Current Implementation

- **API Calls**: 2 parallel requests on page load
- **Data Size**: Minimal (just counts, not full datasets)
- **Caching**: None (fetches fresh on every visit)

### Optimization Opportunities

#### 1. Add Caching

```javascript
// Cache stats for 5 minutes to reduce API calls
const CACHE_TTL = 5 * 60 * 1000 // 5 minutes
const cachedStats = localStorage.getItem('dashboard_stats')
const cacheTime = localStorage.getItem('dashboard_stats_time')

if (cachedStats && Date.now() - cacheTime < CACHE_TTL) {
  stats.value = JSON.parse(cachedStats)
} else {
  // Fetch from API and update cache
  const freshStats = await fetchStats()
  localStorage.setItem('dashboard_stats', JSON.stringify(freshStats))
  localStorage.setItem('dashboard_stats_time', Date.now())
}
```

#### 2. Lazy Loading for Future Enhancements

When adding charts/graphs:

```javascript
// Only load heavy chart library if needed
const showChart = ref(false)

const loadChart = async () => {
  const Chart = await import('chart.js')
  // Initialize chart
}
```

#### 3. Server-Side Aggregation

Instead of counting on frontend:

```javascript
// Current (client-side):
stats.value.communes = communesRes.data.length

// Optimized (server-side):
const statsRes = await api.meta.getStats()
// Backend returns: { communes: 77, crops: 45, dataPoints: 3465 }
// Faster, especially as dataset grows
```

---

## Error Handling

### Current Implementation

```javascript
try {
  const [communesRes, cropsRes] = await Promise.all([...])
  // Update stats
} catch (error) {
  console.error('Failed to load stats:', error)
  // No user-facing error message
}
```

### Recommended Enhancement

```vue
<template>
  <!-- Add error state -->
  <div v-if="error" class="card bg-red-50 border-red-200">
    <p class="text-red-800">
      ⚠️ Failed to load dashboard statistics.
      <button @click="retryLoad" class="text-red-600 underline">
        Retry
      </button>
    </p>
  </div>

  <!-- Add loading state -->
  <div v-if="loading" class="card">
    <p>Loading statistics...</p>
    <!-- Or skeleton loaders -->
  </div>

  <!-- Existing stats cards -->
  <div v-else-if="!error" class="grid...">
    <!-- Stats -->
  </div>
</template>

<script setup>
const loading = ref(true)
const error = ref(null)

const loadStats = async () => {
  loading.value = true
  error.value = null

  try {
    // Fetch data
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const retryLoad = () => loadStats()
</script>
```

---

## Testing

### Manual Testing Checklist

- [ ] Dashboard loads without errors
- [ ] Statistics display correct numbers
- [ ] Numbers update after data ingestion
- [ ] Quick links navigate correctly
- [ ] Responsive design works on mobile
- [ ] Loading state appears briefly
- [ ] Error handling works when API is down

### Automated Testing

**Unit Tests** (recommended):
```javascript
import { mount } from '@vue/test-utils'
import DashboardView from '@/views/DashboardView.vue'

describe('DashboardView', () => {
  it('displays statistics after loading', async () => {
    const wrapper = mount(DashboardView)
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Total Communes')
    expect(wrapper.text()).toContain('Total Crops')
    expect(wrapper.text()).toContain('Data Points')
  })

  it('calculates data points correctly', () => {
    const communes = 77
    const crops = 45
    const expected = 77 * 45 // 3465

    expect(wrapper.vm.stats.dataPoints).toBe(expected)
  })
})
```

---

## Related Documentation

- [API_KEYS.md](./API_KEYS.md) - API authentication and usage
- [MAP_PAGE.md](./MAP_PAGE.md) - Geographic visualization of commune data
- [Backend Scheduler Guide](../../backend/QUICKSTART_TESTING.md) - Data ingestion system
- [Backend API Documentation](http://localhost:5000/api/docs) - Full API reference

---

## Troubleshooting

### Issue: Statistics Show Zero

**Symptoms**: All stats display as "0"

**Possible Causes**:
1. Database is empty (no data ingested yet)
2. API endpoints returning empty arrays
3. Backend not running

**Solution**:
```bash
# Check if backend is running
docker ps | grep tedi_backend

# Check database has data
docker exec tedi_backend python -c "
from app import create_app, db
from app.models import Commune, Crop

app = create_app()
with app.app_context():
    print(f'Communes: {Commune.query.count()}')
    print(f'Crops: {Crop.query.count()}')
"

# Run data ingestion if needed
docker exec tedi_backend python setup_scheduler_data.py
```

### Issue: Dashboard Not Updating After Ingestion

**Symptoms**: Stats don't reflect new data after scheduler runs

**Causes**:
- Frontend caching
- Browser cache
- Old API responses

**Solution**:
1. Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
2. Clear browser cache
3. Add cache-busting to API calls (if persistent issue)

---

**Last Updated**: 2026-01-13
**Component**: `/frontend/src/views/DashboardView.vue`
**Related Backend**: `/backend/app/routes/agriculture.py`, `/backend/app/tasks/scheduler.py`
