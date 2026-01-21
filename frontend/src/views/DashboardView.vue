<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-4xl font-bold text-gray-900 mb-2">Agriculture Dashboard</h1>
    <p class="text-gray-600 mb-8">Real-time KPIs and analytics for Benin's agricultural sector</p>

    <!-- Filters Section -->
    <div class="card mb-8 bg-white border border-gray-200">
      <h2 class="text-xl font-semibold mb-4">Filters & Selection</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Year Range -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Start Year</label>
          <input 
            v-model.number="filters.yearFrom" 
            type="number" 
            min="2010" 
            max="2024"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-tedi-primary"
            @change="loadAggregatedData"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">End Year</label>
          <input 
            v-model.number="filters.yearTo" 
            type="number" 
            min="2010" 
            max="2024"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-tedi-primary"
            @change="loadAggregatedData"
          />
        </div>

        <!-- Commune Selection -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Commune</label>
          <select 
            v-model="filters.communeId" 
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-tedi-primary"
            @change="loadAggregatedData"
          >
            <option :value="null">All Communes</option>
            <option v-for="commune in communes" :key="commune.id" :value="commune.id">
              {{ commune.name }}
            </option>
          </select>
        </div>

        <!-- Crop Selection -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Crop</label>
          <select 
            v-model="filters.cropId" 
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-tedi-primary"
            @change="loadAggregatedData"
          >
            <option :value="null">All Crops</option>
            <option v-for="crop in crops" :key="crop.id" :value="crop.id">
              {{ crop.name }}
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-8">
      <p class="text-gray-600">Loading data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="card bg-red-50 border border-red-200 mb-8">
      <p class="text-red-800">{{ error }}</p>
    </div>

    <!-- Main Content -->
    <div v-else-if="aggregatedData">
      <!-- KPI Cards Row 1 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <!-- Total Production -->
        <div class="card bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-sm font-medium text-gray-600 mb-2">Total Production</h3>
              <p class="text-3xl font-bold text-tedi-primary">
                {{ formatNumber(aggregatedData.summary.total_production_tonnes) }}
              </p>
              <p class="text-xs text-gray-500 mt-1">tonnes</p>
            </div>
            <div class="text-4xl text-tedi-primary opacity-20">🌾</div>
          </div>
          <div v-if="trends.production_change_pct !== undefined" class="mt-4 pt-4 border-t border-blue-200">
            <span :class="trends.production_change_pct >= 0 ? 'text-green-600' : 'text-red-600'" class="text-sm font-semibold">
              {{ trends.production_change_pct >= 0 ? '↑' : '↓' }} {{ Math.abs(trends.production_change_pct) }}%
            </span>
            <p class="text-xs text-gray-500">{{ trends.period }}</p>
          </div>
        </div>

        <!-- Average Yield -->
        <div class="card bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-sm font-medium text-gray-600 mb-2">Average Yield</h3>
              <p class="text-3xl font-bold text-green-600">
                {{ formatNumber(aggregatedData.summary.average_yield_t_ha) }}
              </p>
              <p class="text-xs text-gray-500 mt-1">t/ha</p>
            </div>
            <div class="text-4xl opacity-20">📊</div>
          </div>
          <div v-if="trends.yield_change_pct !== undefined" class="mt-4 pt-4 border-t border-green-200">
            <span :class="trends.yield_change_pct >= 0 ? 'text-green-600' : 'text-red-600'" class="text-sm font-semibold">
              {{ trends.yield_change_pct >= 0 ? '↑' : '↓' }} {{ Math.abs(trends.yield_change_pct) }}%
            </span>
            <p class="text-xs text-gray-500">Efficiency trend</p>
          </div>
        </div>

        <!-- Average Price -->
        <div class="card bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-sm font-medium text-gray-600 mb-2">Average Price</h3>
              <p class="text-3xl font-bold text-purple-600">
                {{ formatNumber(aggregatedData.summary.average_price_xof_kg) }}
              </p>
              <p class="text-xs text-gray-500 mt-1">XOF/kg</p>
            </div>
            <div class="text-4xl opacity-20">💰</div>
          </div>
          <div v-if="trends.price_change_pct !== undefined" class="mt-4 pt-4 border-t border-purple-200">
            <span :class="trends.price_change_pct >= 0 ? 'text-green-600' : 'text-red-600'" class="text-sm font-semibold">
              {{ trends.price_change_pct >= 0 ? '↑' : '↓' }} {{ Math.abs(trends.price_change_pct) }}%
            </span>
            <p class="text-xs text-gray-500">Market trend</p>
          </div>
        </div>

        <!-- Data Quality -->
        <div class="card bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-sm font-medium text-gray-600 mb-2">Data Quality</h3>
              <p class="text-3xl font-bold text-orange-600">
                {{ Math.round(aggregatedData.summary.average_quality_score * 100) }}%
              </p>
              <p class="text-xs text-gray-500 mt-1">{{ aggregatedData.summary.data_points }} records</p>
            </div>
            <div class="text-4xl opacity-20">✓</div>
          </div>
          <div class="mt-4 pt-4 border-t border-orange-200">
            <p class="text-xs text-gray-600">
              {{ aggregatedData.summary.estimated_data_pct }}% estimated data
            </p>
          </div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- Production Trend Chart -->
        <div class="card">
          <h3 class="text-lg font-semibold mb-4">Production Trend</h3>
          <div style="height: 300px; position: relative;">
            <Line :data="productionChartData" :options="chartOptions" />
          </div>
        </div>

        <!-- Yield by Year Chart -->
        <div class="card">
          <h3 class="text-lg font-semibold mb-4">Yield Evolution (t/ha)</h3>
          <div style="height: 300px; position: relative;">
            <Line :data="yieldChartData" :options="chartOptions" />
          </div>
        </div>

        <!-- Price Trend Chart -->
        <div class="card">
          <h3 class="text-lg font-semibold mb-4">Price Trend (XOF/kg)</h3>
          <div style="height: 300px; position: relative;">
            <Line :data="priceChartData" :options="chartOptions" />
          </div>
        </div>

        <!-- Top Crops Chart -->
        <div class="card">
          <h3 class="text-lg font-semibold mb-4">Top 10 Crops by Production</h3>
          <div style="height: 300px; position: relative;">
            <Bar :data="topCropsChartData" :options="barChartOptions" />
          </div>
        </div>
      </div>

      <!-- Top Communes Table -->
      <div class="card mb-8">
        <h3 class="text-lg font-semibold mb-4">Top Communes by Production</h3>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Commune</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Production (tonnes)</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Area (ha)</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Yield (t/ha)</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Records</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="(commune, idx) in topCommunesDisplay" :key="idx" class="hover:bg-gray-50">
                <td class="px-6 py-4 text-sm font-medium text-gray-900">{{ commune.commune_name }}</td>
                <td class="px-6 py-4 text-sm text-gray-700">{{ formatNumber(commune.production_tonnes) }}</td>
                <td class="px-6 py-4 text-sm text-gray-700">{{ formatNumber(commune.area_ha) }}</td>
                <td class="px-6 py-4 text-sm text-gray-700">{{ formatNumber(commune.avg_yield) }}</td>
                <td class="px-6 py-4 text-sm text-gray-700">{{ commune.records }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Top Crops Table -->
      <div class="card">
        <h3 class="text-lg font-semibold mb-4">Top Crops by Production</h3>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Crop</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Production (tonnes)</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Area (ha)</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Yield (t/ha)</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Price (XOF/kg)</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="(crop, idx) in topCropsDisplay" :key="idx" class="hover:bg-gray-50">
                <td class="px-6 py-4 text-sm font-medium text-gray-900">{{ crop.crop_name }}</td>
                <td class="px-6 py-4 text-sm text-gray-700">{{ formatNumber(crop.production_tonnes) }}</td>
                <td class="px-6 py-4 text-sm text-gray-700">{{ formatNumber(crop.area_ha) }}</td>
                <td class="px-6 py-4 text-sm text-gray-700">{{ formatNumber(crop.avg_yield) }}</td>
                <td class="px-6 py-4 text-sm text-gray-700">{{ formatNumber(crop.avg_price) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Line, Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import api from '@/services/api'

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

// Data
const communes = ref([])
const crops = ref([])
const aggregatedData = ref(null)
const loading = ref(false)
const error = ref(null)

const filters = ref({
  yearFrom: 2015,
  yearTo: 2024,
  communeId: null,
  cropId: null,
})

// Chart options
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
    },
  },
  scales: {
    y: {
      beginAtZero: true,
    },
  },
}

const barChartOptions = {
  indexAxis: 'y',
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
  },
  scales: {
    x: {
      beginAtZero: true,
    },
  },
}

// Computed properties
const trends = computed(() => aggregatedData.value?.data?.trends || {})

const topCommunesDisplay = computed(() => {
  return aggregatedData.value?.data?.by_commune?.slice(0, 10) || []
})

const topCropsDisplay = computed(() => {
  return aggregatedData.value?.data?.by_crop?.slice(0, 10) || []
})

const productionChartData = computed(() => {
  const byYear = aggregatedData.value?.data?.by_year || []
  return {
    labels: byYear.map(y => y.year),
    datasets: [
      {
        label: 'Production (tonnes)',
        data: byYear.map(y => y.production_tonnes),
        borderColor: '#2563eb',
        backgroundColor: 'rgba(37, 99, 235, 0.1)',
        fill: true,
        tension: 0.4,
        borderWidth: 2,
      },
    ],
  }
})

const yieldChartData = computed(() => {
  const byYear = aggregatedData.value?.data?.by_year || []
  return {
    labels: byYear.map(y => y.year),
    datasets: [
      {
        label: 'Avg Yield (t/ha)',
        data: byYear.map(y => y.avg_yield),
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
        tension: 0.4,
        borderWidth: 2,
      },
    ],
  }
})

const priceChartData = computed(() => {
  const byYear = aggregatedData.value?.data?.by_year || []
  return {
    labels: byYear.map(y => y.year),
    datasets: [
      {
        label: 'Avg Price (XOF/kg)',
        data: byYear.map(y => y.avg_price),
        borderColor: '#a855f7',
        backgroundColor: 'rgba(168, 85, 247, 0.1)',
        fill: true,
        tension: 0.4,
        borderWidth: 2,
      },
    ],
  }
})

const topCropsChartData = computed(() => {
  const topCrops = aggregatedData.value?.data?.by_crop?.slice(0, 10) || []
  return {
    labels: topCrops.map(c => c.crop_name),
    datasets: [
      {
        label: 'Production (tonnes)',
        data: topCrops.map(c => c.production_tonnes),
        backgroundColor: [
          '#3b82f6',
          '#8b5cf6',
          '#ec4899',
          '#f59e0b',
          '#10b981',
          '#06b6d4',
          '#6366f1',
          '#f43f5e',
          '#14b8a6',
          '#eab308',
        ],
      },
    ],
  }
})

// Methods
const formatNumber = (num) => {
  if (!num) return '0'
  return new Intl.NumberFormat('fr-FR', {
    maximumFractionDigits: 2,
    minimumFractionDigits: 0,
  }).format(num)
}

const loadAggregatedData = async () => {
  loading.value = true
  error.value = null
  try {
    const params = {
      year_from: filters.value.yearFrom,
      year_to: filters.value.yearTo,
    }
    if (filters.value.communeId) {
      params.commune_id = filters.value.communeId
    }
    if (filters.value.cropId) {
      params.crop_id = filters.value.cropId
    }

    const response = await api.agriculture.getAggregatedStats(params)
    aggregatedData.value = response.data
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to load data'
    console.error('Error loading aggregated data:', err)
  } finally {
    loading.value = false
  }
}

const loadInitialData = async () => {
  try {
    const [communesRes, cropsRes] = await Promise.all([
      api.agriculture.getCommunes(),
      api.agriculture.getCrops(),
    ])
    communes.value = communesRes.data
    crops.value = cropsRes.data
    await loadAggregatedData()
  } catch (err) {
    error.value = 'Failed to load communes and crops'
    console.error('Error loading initial data:', err)
  }
}

onMounted(() => {
  loadInitialData()
})
</script>

<style scoped>
.card {
  @apply bg-white rounded-lg shadow-md p-6;
}
</style>
