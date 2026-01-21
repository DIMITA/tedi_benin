# Map Page Documentation

## Overview

The Map Page (`MapView.vue`) provides an interactive geographic visualization of Benin's communes using Leaflet.js. It displays commune locations, boundaries, and associated data collected by the backend data ingestion system.

**Route**: `/map`

---

## Purpose

The Map Page serves multiple functions:

1. **Geographic Exploration**: Visual representation of communes across Benin
2. **Data Discovery**: Interactive way to explore which communes have available data
3. **Spatial Context**: Understand geographic relationships between communes
4. **Entry Point to Data**: Click on communes to view detailed agricultural and economic data

---

## Features

### 1. Interactive Map (Leaflet.js)

**Map Configuration**:
- **Center**: Benin (coordinates: 9.30769°N, 2.315834°E)
- **Initial Zoom**: Level 7 (country view)
- **Tile Layer**: OpenStreetMap standard tiles
- **Max Zoom**: 19 (street-level detail)
- **Controls**: Zoom in/out, pan, full-screen

**Map Libraries Used**:
- Leaflet 1.9.4 (core mapping library)
- OpenStreetMap tiles (free, community-maintained)

### 2. Commune Markers

Each commune with coordinates is displayed as a custom marker:

**Marker Design**:
- **Icon**: Circular with commune's first letter
- **Color**: TEDI primary color (green)
- **Size**: 32x32 pixels
- **Shadow**: White border + drop shadow for visibility

**Marker Information**:
- Tooltip on hover: Commune name
- Click → Opens popup with basic info
- Click marker → Selects commune in sidebar

**Example Marker HTML**:
```html
<div class="w-8 h-8 bg-tedi-primary rounded-full border-2 border-white shadow-lg flex items-center justify-center text-white text-xs font-bold">
  C  <!-- First letter of "Cotonou" -->
</div>
```

### 3. Popup Windows

When clicking a marker, a popup displays:
- **Commune Name** (bold, large text)
- **Region Name** (smaller, gray text)

**Example**:
```
┌──────────────────┐
│   Cotonou        │
│   Littoral       │
└──────────────────┘
```

### 4. Sidebar Information Panel

The right sidebar displays detailed information about the selected commune:

#### Selected Commune Info Card

**Displays**:
- **Commune Name** (header)
- **Region**: Parent region name
- **Population**: Formatted with thousands separators (e.g., "679,012")
- **Area**: in km² (e.g., "79 km²")
- **Coordinates**: Latitude, Longitude (4 decimal places)

**Action Button**:
- "View Agriculture Data" → Navigates to `/agriculture?commune_id=X`
- Opens filtered view of agricultural statistics for that commune

#### Legend Card

Explains marker colors:
- **Green marker**: Commune with available data
- **Gray marker**: Commune without data (future enhancement)

#### Map Statistics Card

Displays aggregate statistics:
- **Total Communes**: Count of all communes displayed on map
- **Regions**: Number of unique regions represented

---

## Integration with Backend Data Ingestion System

### How Map Data Comes from the Scheduler

The Map Page visualizes data that originates from the automated data ingestion scheduler, particularly from OpenStreetMap and other geospatial sources.

#### 1. Data Source: OpenStreetMap Connector

**Backend Flow**:
```
1. Scheduler runs tasks.realestate.ingest_osm every month
   ↓
2. OSM Connector queries Overpass API for Benin boundaries
   ↓
3. Extracts commune boundaries, center points, areas
   ↓
4. Loads data into:
   - communes table (names, coordinates, areas)
   - osm_buildings table (building footprints)
   - osm_amenities table (points of interest)
   - osm_land_use table (land use polygons)
   ↓
5. Map fetches commune data via GET /api/v1/agriculture/communes
   ↓
6. Displays markers at center_lat, center_lon coordinates
```

#### 2. Commune Data Structure

The Map queries `/api/v1/agriculture/communes` which returns:

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
    "center_lat": 6.3654,     // ← Used for marker placement
    "center_lon": 2.4183,     // ← Used for marker placement
    "population": 679012,
    "area_km2": 79.0,
    "administrative_level": 2,
    "created_at": "2026-01-13T05:00:00Z"
  },
  ...
]
```

**Key Fields for Map**:
- `center_lat`, `center_lon`: Marker position
- `name`: Marker label, popup title
- `region.name`: Context information
- `population`, `area_km2`: Sidebar display

#### 3. Data Freshness

The communes displayed on the map are updated when:
- OSM ingestion task runs successfully
- New communes are added to OpenStreetMap
- Commune boundaries or center points are updated in OSM

**Update Frequency**: Monthly (configurable in scheduler)

**Last Update Tracking**:
```javascript
// Could be added to show data freshness
const lastUpdate = await api.meta.getDataSourceLastUpdate('OpenStreetMap')
// Displays: "Map data last updated: 3 days ago"
```

#### 4. Future Enhancement: Real-Time OSM Data

**Current State**: Monthly updates via scheduler
**Planned Enhancement**: Display real-time OSM features

```vue
<!-- Future feature: Toggle OSM layers -->
<div class="card">
  <h3>Map Layers</h3>
  <label>
    <input type="checkbox" v-model="layers.buildings" />
    Show Buildings (from OSM)
  </label>
  <label>
    <input type="checkbox" v-model="layers.amenities" />
    Show Amenities (from OSM)
  </label>
  <label>
    <input type="checkbox" v-model="layers.landUse" />
    Show Land Use (from OSM)
  </label>
</div>
```

This would query the `osm_buildings`, `osm_amenities`, and `osm_land_use` tables populated by the scheduler.

---

## Technical Implementation

### Component Structure

```vue
MapView.vue
├── Map Container (Leaflet div)
├── Sidebar
│   ├── Selected Commune Card (conditional)
│   ├── Legend Card
│   └── Statistics Card
└── Script Setup
    ├── State Management
    ├── Leaflet Initialization
    ├── Commune Loading
    ├── Marker Creation
    └── Event Handling
```

### State Management

```javascript
const map = ref(null)              // Leaflet map instance
const communes = ref([])            // Array of commune objects from API
const selectedCommune = ref(null)   // Currently selected commune
const markers = ref([])             // Array of Leaflet marker objects
```

### Leaflet Initialization

```javascript
const initMap = () => {
  // Create map instance
  map.value = L.map('map').setView([9.30769, 2.315834], 7)

  // Add OpenStreetMap tile layer
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19,
  }).addTo(map.value)

  // Fix Leaflet default marker icons (CDN issue workaround)
  delete L.Icon.Default.prototype._getIconUrl
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  })
}
```

### Commune Loading

```javascript
const loadCommunes = async () => {
  try {
    // Fetch communes from API
    const response = await api.agriculture.getCommunes()
    communes.value = response.data

    // Add markers for communes with coordinates
    communes.value.forEach(commune => {
      if (commune.center_lat && commune.center_lon) {
        addCommuneMarker(commune)
      }
    })

    // Auto-fit map to show all markers
    if (markers.value.length > 0) {
      const bounds = L.featureGroup(markers.value).getBounds()
      map.value.fitBounds(bounds, { padding: [50, 50] })
    }
  } catch (error) {
    console.error('Failed to load communes:', error)
  }
}
```

### Marker Creation with Custom Icons

```javascript
const addCommuneMarker = (commune) => {
  // Create custom div icon (HTML-based marker)
  const icon = L.divIcon({
    className: 'custom-marker',
    html: `<div class="w-8 h-8 bg-tedi-primary rounded-full border-2 border-white shadow-lg flex items-center justify-center text-white text-xs font-bold">
      ${commune.name.charAt(0)}
    </div>`,
    iconSize: [32, 32],
    iconAnchor: [16, 16],  // Center of icon
  })

  // Create marker at commune coordinates
  const marker = L.marker([commune.center_lat, commune.center_lon], { icon })
    .addTo(map.value)
    .bindPopup(`
      <div class="p-2">
        <h4 class="font-semibold text-base mb-1">${commune.name}</h4>
        <p class="text-sm text-gray-600">${commune.region?.name || 'Unknown region'}</p>
      </div>
    `)
    .on('click', () => {
      selectedCommune.value = commune
    })

  markers.value.push(marker)
}
```

### Navigation Integration

```javascript
const viewCommuneData = () => {
  router.push({
    name: 'agriculture',
    query: { commune_id: selectedCommune.value.id },
  })
}
```

This navigates to the Agriculture view with a pre-filtered commune, allowing users to immediately see that commune's crop production data.

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│           OSM Ingestion → Map Visualization Flow            │
└─────────────────────────────────────────────────────────────┘

STEP 1: Data Ingestion (Monthly Scheduler Run)
   ├─→ tasks.realestate.ingest_osm executes
   │   ├─→ Queries Overpass API for Benin data
   │   │   └─→ [out:json];area["ISO3166-1"="BJ"]->.benin;...
   │   │
   │   ├─→ OSMConnector.fetch() retrieves GeoJSON
   │   │   └─→ Buildings, amenities, land use, boundaries
   │   │
   │   ├─→ OSMConnector.transform() processes data
   │   │   └─→ Extracts commune boundaries
   │   │       └─→ Calculates center points (ST_Centroid)
   │   │           └─→ Calculates areas (ST_Area)
   │   │
   │   └─→ OSMConnector.load() inserts into database
   │       ├─→ osm_buildings table
   │       ├─→ osm_amenities table
   │       ├─→ osm_land_use table
   │       └─→ communes table (updated with coordinates, areas)
   │
   └─→ IngestionLog created with success/failure status

STEP 2: Map Page Loads (User Action)
   ├─→ User navigates to /map
   │
   ├─→ onMounted() lifecycle hook fires
   │   ├─→ initMap() creates Leaflet instance
   │   │   └─→ Centers on Benin (9.30769°N, 2.315834°E)
   │   │
   │   └─→ loadCommunes() fetches data
   │       └─→ GET /api/v1/agriculture/communes
   │           ├─→ Backend queries communes table
   │           │   └─→ SELECT id, name, center_lat, center_lon,
   │           │       population, area_km2, region_id
   │           │       FROM communes
   │           │       WHERE center_lat IS NOT NULL
   │           │
   │           └─→ Returns JSON array of commune objects
   │
   ├─→ For each commune with coordinates:
   │   └─→ addCommuneMarker(commune)
   │       ├─→ Creates custom div icon
   │       ├─→ Places marker at (center_lat, center_lon)
   │       ├─→ Binds popup with commune name + region
   │       └─→ Attaches click event listener
   │
   └─→ map.fitBounds() adjusts view to show all markers

STEP 3: User Interaction
   ├─→ User clicks marker
   │   ├─→ Marker fires 'click' event
   │   ├─→ selectedCommune.value = commune
   │   └─→ Sidebar updates with commune details
   │
   └─→ User clicks "View Agriculture Data"
       └─→ router.push({ name: 'agriculture', query: { commune_id: X } })
           └─→ Navigates to agriculture page filtered by commune

RESULT: User sees geographic context of all communes with ingested data
```

---

## Usage Scenarios

### Scenario 1: Exploring Benin's Geography

**User Flow**:
1. User clicks "View Interactive Map" from dashboard
2. Map loads showing all 77 communes across Benin
3. User zooms in on southern coast (Cotonou area)
4. Notices dense cluster of communes near the capital
5. Clicks on "Cotonou" marker
6. Sidebar shows: Population 679,012, Area 79 km²
7. User clicks "View Agriculture Data" to see Cotonou's crop statistics

### Scenario 2: Regional Comparison

**User Flow**:
1. User wants to compare northern vs. southern regions
2. Opens map, notices commune distribution
3. Clicks multiple communes in Alibori region (north)
4. Notes population and area from sidebar
5. Switches to Littoral region (south)
6. Compares population density visually and via sidebar stats

### Scenario 3: Data Availability Check

**User Flow**:
1. User wants to know which communes have data
2. Opens map
3. Sees 77 markers → Knows data exists for 77 communes
4. Can visually identify gaps where no markers appear
5. Future: Gray markers for communes without data

### Scenario 4: Mobile Field Work

**User Flow**:
1. Agricultural officer in the field uses tablet/phone
2. Opens map to see nearby communes
3. GPS or manual navigation to find current location
4. Identifies nearest commune with available data
5. Views that commune's data for comparison with field observations

---

## Responsive Design

The map adapts to different screen sizes:

### Desktop (lg and above)
- **Layout**: 2/3 map, 1/3 sidebar (side-by-side)
- **Grid**: `grid-cols-1 lg:grid-cols-3`
- **Map**: `lg:col-span-2`

### Tablet (md)
- **Layout**: Full-width map, sidebar below
- **Map Height**: 600px

### Mobile (sm)
- **Layout**: Stacked vertical layout
- **Map Height**: 400px (reduced for better UX)
- **Sidebar**: Full width cards stacked vertically

**CSS Classes Used**:
```html
<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
  <!-- Map: Full width on mobile, 2/3 on desktop -->
  <div class="lg:col-span-2">
    <div id="map" style="height: 600px;"></div>
  </div>

  <!-- Sidebar: Full width on mobile, 1/3 on desktop -->
  <div class="space-y-6">
    <!-- Sidebar cards -->
  </div>
</div>
```

---

## Performance Optimization

### Current Implementation

**API Calls**: 1 request on page load (`/api/v1/agriculture/communes`)
**Data Size**: ~77 communes × ~150 bytes = ~12 KB (minimal)
**Markers**: 77 custom div icons (lightweight HTML)

### Optimization Strategies

#### 1. Lazy Loading for Large Datasets

If commune count grows significantly (e.g., 1000+):

```javascript
// Only load communes in current viewport
const visibleCommunes = communes.value.filter(commune => {
  const bounds = map.value.getBounds()
  return bounds.contains([commune.center_lat, commune.center_lon])
})

// Load more as user pans/zooms
map.value.on('moveend', loadVisibleCommunes)
```

#### 2. Marker Clustering

For dense areas (e.g., Cotonou), group nearby markers:

```javascript
import L from 'leaflet'
import 'leaflet.markercluster'

const markerCluster = L.markerClusterGroup()
communes.value.forEach(commune => {
  const marker = L.marker([commune.center_lat, commune.center_lon])
  markerCluster.addLayer(marker)
})
map.value.addLayer(markerCluster)
```

#### 3. Caching Commune Data

```javascript
// Cache communes data to avoid repeated API calls
const CACHE_KEY = 'map_communes'
const CACHE_TTL = 24 * 60 * 60 * 1000 // 24 hours

const loadCommunes = async () => {
  const cached = localStorage.getItem(CACHE_KEY)
  const cacheTime = localStorage.getItem(`${CACHE_KEY}_time`)

  if (cached && Date.now() - cacheTime < CACHE_TTL) {
    communes.value = JSON.parse(cached)
    communes.value.forEach(addCommuneMarker)
  } else {
    const response = await api.agriculture.getCommunes()
    communes.value = response.data
    localStorage.setItem(CACHE_KEY, JSON.stringify(communes.value))
    localStorage.setItem(`${CACHE_KEY}_time`, Date.now())
    communes.value.forEach(addCommuneMarker)
  }
}
```

#### 4. GeoJSON Boundaries

**Future Enhancement**: Display commune boundaries, not just center points

```javascript
// Load GeoJSON polygon for commune boundaries
const communeLayer = L.geoJSON(boundaryData, {
  style: {
    color: '#10b981',
    weight: 2,
    fillOpacity: 0.1
  },
  onEachFeature: (feature, layer) => {
    layer.on('click', () => {
      selectedCommune.value = feature.properties
    })
  }
}).addTo(map.value)
```

**Data Source**: `osm_land_use` table with `ST_AsGeoJSON(geometry)` from PostGIS

---

## Future Enhancements

### 1. Heatmap Visualization

Display data density or crop production intensity:

```javascript
import 'leaflet.heat'

const heatmapData = communes.value.map(c => [
  c.center_lat,
  c.center_lon,
  c.total_production // intensity value
])

L.heatLayer(heatmapData, {
  radius: 25,
  blur: 15,
  maxZoom: 17
}).addTo(map.value)
```

### 2. Time Series Animation

Show how data changes over time:

```vue
<div class="card">
  <h3>Time Series</h3>
  <input
    type="range"
    v-model="selectedYear"
    min="2015"
    max="2025"
  />
  <p>Showing data for: {{ selectedYear }}</p>
</div>
```

Markers update color/size based on production data for selected year.

### 3. Filter by Crop Type

```vue
<div class="card">
  <h3>Filter by Crop</h3>
  <select v-model="selectedCrop" @change="updateMarkers">
    <option value="all">All Crops</option>
    <option v-for="crop in crops" :value="crop.id">
      {{ crop.name }}
    </option>
  </select>
</div>
```

Only show communes with production data for the selected crop.

### 4. Compare Mode

Select multiple communes for side-by-side comparison:

```vue
<div class="card">
  <h3>Compare Communes</h3>
  <div v-for="commune in compareList" :key="commune.id">
    {{ commune.name }}
    <button @click="removeFromCompare(commune)">✕</button>
  </div>
</div>
```

### 5. Export Map View

Allow users to export current map view:

```javascript
// Export as image
const exportMap = () => {
  leafletImage(map.value, (err, canvas) => {
    const img = document.createElement('img')
    img.src = canvas.toDataURL()
    download(img.src, 'benin_map.png')
  })
}

// Export as GeoJSON
const exportGeoJSON = () => {
  const geojson = {
    type: 'FeatureCollection',
    features: communes.value.map(c => ({
      type: 'Feature',
      geometry: {
        type: 'Point',
        coordinates: [c.center_lon, c.center_lat]
      },
      properties: {
        name: c.name,
        region: c.region?.name,
        population: c.population
      }
    }))
  }

  download(JSON.stringify(geojson), 'communes.geojson')
}
```

### 6. Real-Time Updates

Show live ingestion status on map:

```vue
<div class="card">
  <h3>Live Updates</h3>
  <div class="flex items-center">
    <div class="w-3 h-3 bg-green-500 rounded-full animate-pulse mr-2"></div>
    <span>OSM data updating...</span>
  </div>
</div>
```

Use WebSockets or polling to show when new data is being ingested.

---

## Integration with Other Pages

### From Map to Agriculture View

```javascript
// User clicks "View Agriculture Data" button
const viewCommuneData = () => {
  router.push({
    name: 'agriculture',
    query: { commune_id: selectedCommune.value.id }
  })
}
```

Agriculture view receives `commune_id` query param and pre-filters data:

```javascript
// In AgricultureView.vue
onMounted(() => {
  const communeId = route.query.commune_id
  if (communeId) {
    filterByCommune(communeId)
  }
})
```

### From Dashboard to Map

Dashboard has a quick link:

```vue
<router-link to="/map">
  → View Interactive Map
</router-link>
```

### Deep Linking

Map supports direct linking to specific communes:

**URL**: `/map?commune=Cotonou`

```javascript
onMounted(() => {
  const communeName = route.query.commune
  if (communeName) {
    const commune = communes.value.find(c =>
      c.name.toLowerCase() === communeName.toLowerCase()
    )
    if (commune) {
      selectedCommune.value = commune
      map.value.setView([commune.center_lat, commune.center_lon], 12)
    }
  }
})
```

---

## Troubleshooting

### Issue: Map Not Displaying

**Symptoms**: Blank white space where map should be

**Possible Causes**:
1. Leaflet CSS not loaded
2. Map container height not set
3. Leaflet initialized before DOM ready

**Solution**:
```vue
<template>
  <!-- Ensure explicit height -->
  <div id="map" style="height: 600px; width: 100%;"></div>
</template>

<script setup>
import 'leaflet/dist/leaflet.css' // ← Must be imported

onMounted(() => {
  // Wait for DOM
  nextTick(() => {
    initMap()
  })
})
</script>
```

### Issue: Markers Not Appearing

**Symptoms**: Map displays but no markers

**Possible Causes**:
1. API request failed
2. Communes have no coordinates (`center_lat`/`center_lon` null)
3. Marker icons not loading

**Solution**:
```javascript
const loadCommunes = async () => {
  try {
    const response = await api.agriculture.getCommunes()
    console.log('Loaded communes:', response.data.length)

    // Check which communes have coordinates
    const withCoords = response.data.filter(c =>
      c.center_lat && c.center_lon
    )
    console.log('Communes with coordinates:', withCoords.length)

    // Add markers
    withCoords.forEach(addCommuneMarker)
  } catch (error) {
    console.error('Failed to load communes:', error)
  }
}
```

### Issue: Map Performance Issues

**Symptoms**: Slow panning/zooming, laggy interactions

**Possible Causes**:
1. Too many markers (1000+)
2. Complex custom icons
3. Large popup content

**Solution**:
- Use marker clustering
- Simplify custom icons
- Lazy load popup content
- Reduce marker count with filtering

---

## Related Documentation

- [API_KEYS.md](./API_KEYS.md) - API authentication for accessing commune data
- [DASHBOARD.md](./DASHBOARD.md) - Dashboard with commune statistics
- [Backend OSM Connector](../../backend/app/connectors/osm.py) - OSM data ingestion
- [Backend Spatial Tables](../../backend/PHASE_3_COMPLETION_SUMMARY.md) - PostGIS spatial schema

---

## External Resources

- [Leaflet Documentation](https://leafletjs.com/reference.html) - Official Leaflet API reference
- [OpenStreetMap](https://www.openstreetmap.org/) - Underlying map data source
- [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API) - Query language for OSM data
- [PostGIS Documentation](https://postgis.net/docs/) - Spatial database functions

---

**Last Updated**: 2026-01-13
**Component**: `/frontend/src/views/MapView.vue`
**Dependencies**: Leaflet 1.9.4, OpenStreetMap tiles
**Related Backend**: `/backend/app/connectors/osm.py`, `/backend/app/tasks/realestate.py`
