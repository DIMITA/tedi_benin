<template>
  <div>
    <h1 class="text-3xl font-bold text-gray-900 mb-8">Interactive Map - Benin</h1>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Map -->
      <div class="lg:col-span-2">
        <div class="card p-0 overflow-hidden">
          <div id="map" style="height: 600px; width: 100%;"></div>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="space-y-6">
        <!-- Selected Commune Info -->
        <div v-if="selectedCommune" class="card">
          <h3 class="text-lg font-semibold mb-4">{{ selectedCommune.name }}</h3>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-600">Region:</span>
              <span class="font-medium">{{ selectedCommune.region?.name }}</span>
            </div>
            <div v-if="selectedCommune.population" class="flex justify-between">
              <span class="text-gray-600">Population:</span>
              <span class="font-medium">{{ formatNumber(selectedCommune.population) }}</span>
            </div>
            <div v-if="selectedCommune.area_km2" class="flex justify-between">
              <span class="text-gray-600">Area:</span>
              <span class="font-medium">{{ formatNumber(selectedCommune.area_km2) }} km²</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Coordinates:</span>
              <span class="font-medium">{{ selectedCommune.center_lat?.toFixed(4) }}, {{ selectedCommune.center_lon?.toFixed(4) }}</span>
            </div>
          </div>
          <button
            @click="viewCommuneData"
            class="btn-primary w-full mt-4"
          >
            View Agriculture Data
          </button>
        </div>

        <!-- Legend -->
        <div class="card">
          <h3 class="text-lg font-semibold mb-4">Legend</h3>
          <div class="space-y-2 text-sm">
            <div class="flex items-center">
              <div class="w-4 h-4 bg-tedi-primary rounded-full mr-2"></div>
              <span>Commune with data</span>
            </div>
            <div class="flex items-center">
              <div class="w-4 h-4 bg-gray-400 rounded-full mr-2"></div>
              <span>Commune without data</span>
            </div>
          </div>
        </div>

        <!-- Stats -->
        <div class="card">
          <h3 class="text-lg font-semibold mb-4">Map Statistics</h3>
          <div class="space-y-3">
            <div>
              <p class="text-sm text-gray-600">Total Communes</p>
              <p class="text-2xl font-bold text-tedi-primary">{{ communes.length }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Regions</p>
              <p class="text-2xl font-bold text-tedi-secondary">{{ uniqueRegions }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()

// Lazy load Leaflet
let L = null

// State
const map = ref(null)
const communes = ref([])
const selectedCommune = ref(null)
const markers = ref([])
const mapLoading = ref(true)

// Computed
const uniqueRegions = computed(() => {
  const regions = new Set(communes.value.map(c => c.region?.name).filter(Boolean))
  return regions.size
})

// Dynamically load Leaflet
const loadLeaflet = async () => {
  if (L) return L
  const leaflet = await import('leaflet')
  await import('leaflet/dist/leaflet.css')
  L = leaflet.default
  return L
}

// Methods
const initMap = async () => {
  try {
    await loadLeaflet()
    mapLoading.value = false
    await nextTick()
    
    // Create map centered on Benin
    map.value = L.map('map').setView([9.30769, 2.315834], 7)

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(map.value)

    // Fix Leaflet marker icon issue
    delete L.Icon.Default.prototype._getIconUrl
    L.Icon.Default.mergeOptions({
      iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
      iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
    })
  } catch (error) {
    console.error('Failed to load map:', error)
    mapLoading.value = false
  }
}

const loadCommunes = async () => {
  try {
    const response = await api.agriculture.getCommunes()
    communes.value = response.data

    // Add markers for communes with coordinates
    communes.value.forEach(commune => {
      if (commune.center_lat && commune.center_lon) {
        addCommuneMarker(commune)
      }
    })

    // Adjust map bounds to fit all markers
    if (markers.value.length > 0) {
      const bounds = L.featureGroup(markers.value).getBounds()
      map.value.fitBounds(bounds, { padding: [50, 50] })
    }
  } catch (error) {
    console.error('Failed to load communes:', error)
  }
}

const addCommuneMarker = (commune) => {
  // Create custom icon
  const icon = L.divIcon({
    className: 'custom-marker',
    html: `<div class="w-8 h-8 bg-tedi-primary rounded-full border-2 border-white shadow-lg flex items-center justify-center text-white text-xs font-bold">${commune.name.charAt(0)}</div>`,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  })

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

const viewCommuneData = () => {
  router.push({
    name: 'agriculture',
    query: { commune_id: selectedCommune.value.id },
  })
}

const formatNumber = (value) => {
  return new Intl.NumberFormat('fr-FR').format(value)
}

// Lifecycle
onMounted(async () => {
  await initMap()
  await loadCommunes()
})

onBeforeUnmount(() => {
  if (map.value) {
    map.value.remove()
  }
})
</script>

<style>
/* Fix Leaflet marker icons */
.leaflet-marker-icon {
  background: none !important;
  border: none !important;
}

.custom-marker {
  background: none !important;
  border: none !important;
}

/* Leaflet popup customization */
.leaflet-popup-content-wrapper {
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.leaflet-popup-content {
  margin: 8px;
  font-family: inherit;
}
</style>
