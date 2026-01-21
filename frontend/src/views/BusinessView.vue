<template>
  <div>
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-3xl font-bold text-gray-900">🏢 Business Index</h1>
      <ExportDropdown
        v-if="canExport"
        :disabled="loading"
        :exporting="exporting"
        @export="exportData"
      />
    </div>

    <!-- Filters -->
    <div class="card mb-6">
      <h3 class="text-lg font-semibold mb-4">Filters</h3>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Business Sector</label>
          <select v-model="filters.sector_id" @change="loadData" class="w-full px-3 py-2 border border-gray-300 rounded-md">
            <option :value="null">All Sectors</option>
            <option v-for="sector in sectors" :key="sector.id" :value="sector.id">
              {{ sector.name }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Year</label>
          <select v-model="filters.year" @change="loadData" class="w-full px-3 py-2 border border-gray-300 rounded-md">
            <option :value="null">All Years</option>
            <option v-for="year in availableYears" :key="year" :value="year">
              {{ year }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Market Saturation</label>
          <select v-model="filters.market_saturation" @change="loadData" class="w-full px-3 py-2 border border-gray-300 rounded-md">
            <option :value="null">All Levels</option>
            <option value="undersaturated">Undersaturated</option>
            <option value="balanced">Balanced</option>
            <option value="saturated">Saturated</option>
            <option value="oversaturated">Oversaturated</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Competition</label>
          <select v-model="filters.competition" @change="loadData" class="w-full px-3 py-2 border border-gray-300 rounded-md">
            <option :value="null">All Levels</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="card text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-tedi-primary"></div>
      <p class="mt-4 text-gray-600">Loading data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="card bg-red-50 border border-red-200">
      <p class="text-red-800">{{ error }}</p>
      <button @click="loadData" class="btn-secondary mt-4">Retry</button>
    </div>

    <!-- Data Table -->
    <div v-else class="card">
      <DataTable
        :columns="columns"
        :data="tableData"
        :pagination="pagination"
        @page-change="changePage"
        @per-page-change="changePerPage"
        empty-message="No business data found. Try adjusting your filters."
      >
        <template #cell-commune="{ row }">
          <span class="font-medium text-gray-900">{{ row.commune?.name }}</span>
        </template>
        <template #cell-sector="{ row }">
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-teal-100 text-teal-800">
            {{ row.sector?.name }}
          </span>
        </template>
        <template #cell-market_saturation="{ row }">
          <span
            class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
            :class="{
              'bg-green-100 text-green-800': row.market_saturation === 'undersaturated',
              'bg-blue-100 text-blue-800': row.market_saturation === 'balanced',
              'bg-yellow-100 text-yellow-800': row.market_saturation === 'saturated',
              'bg-red-100 text-red-800': row.market_saturation === 'oversaturated'
            }"
          >
            {{ formatSaturation(row.market_saturation) }}
          </span>
        </template>
        <template #cell-competition_intensity="{ row }">
          <span
            class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
            :class="{
              'bg-green-100 text-green-800': row.competition_intensity === 'low',
              'bg-yellow-100 text-yellow-800': row.competition_intensity === 'medium',
              'bg-red-100 text-red-800': row.competition_intensity === 'high'
            }"
          >
            {{ formatCompetition(row.competition_intensity) }}
          </span>
        </template>
        <template #cell-formality_rate="{ row }">
          <div class="flex items-center">
            <div class="flex-1 bg-gray-200 rounded-full h-2 mr-2">
              <div
                class="h-2 rounded-full bg-indigo-500"
                :style="{ width: `${(row.formality_rate || 0)}%` }"
              ></div>
            </div>
            <span class="text-xs text-gray-600">{{ (row.formality_rate || 0).toFixed(0) }}%</span>
          </div>
        </template>
        <template #cell-data_quality_score="{ row }">
          <div class="flex items-center">
            <div class="flex-1 bg-gray-200 rounded-full h-2 mr-2">
              <div
                class="h-2 rounded-full"
                :class="getQualityColor(row.data_quality_score)"
                :style="{ width: `${(row.data_quality_score || 0) * 100}%` }"
              ></div>
            </div>
            <span class="text-xs text-gray-600">{{ ((row.data_quality_score || 0) * 100).toFixed(0) }}%</span>
          </div>
        </template>
      </DataTable>
    </div>

    <!-- Summary Stats -->
    <div v-if="!loading && !error && tableData.length > 0" class="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
      <div class="card">
        <h4 class="text-sm font-medium text-gray-500 mb-1">Total Businesses</h4>
        <p class="text-2xl font-bold text-tedi-primary">{{ formatNumber(totalBusinesses) }}</p>
      </div>
      <div class="card">
        <h4 class="text-sm font-medium text-gray-500 mb-1">Avg Business Density</h4>
        <p class="text-2xl font-bold text-tedi-secondary">{{ formatNumber(avgDensity) }}</p>
      </div>
      <div class="card">
        <h4 class="text-sm font-medium text-gray-500 mb-1">Avg Sector Growth</h4>
        <p class="text-2xl font-bold text-tedi-accent">{{ formatNumber(avgGrowth) }}</p>
      </div>
      <div class="card">
        <h4 class="text-sm font-medium text-gray-500 mb-1">Avg Formality Rate</h4>
        <p class="text-2xl font-bold text-gray-900">{{ formatNumber(avgFormality) }}%</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import DataTable from '@/components/DataTable.vue'
import ExportDropdown from '@/components/ExportDropdown.vue'
import { formatPrice } from '@/utils/formatters'

const authStore = useAuthStore()
const canExport = computed(() => authStore.canExport)

// State
const loading = ref(false)
const exporting = ref(false)
const error = ref(null)
const tableData = ref([])
const pagination = ref(null)
const currentPage = ref(1)
const perPage = ref(10)
const sectors = ref([])
const filters = ref({
  sector_id: null,
  year: null,
  market_saturation: null,
  competition: null,
})

// Year range for filters
const currentYear = new Date().getFullYear()
const availableYears = Array.from({ length: currentYear - 2010 + 1 }, (_, i) => 2010 + i)

// Table columns configuration
const columns = [
  { key: 'commune', label: 'Commune', format: 'text' },
  { key: 'sector', label: 'Sector', format: 'text' },
  { key: 'year', label: 'Year', format: 'number' },
  { key: 'num_businesses', label: 'Businesses', format: 'number' },
  { key: 'business_density_index', label: 'Density Index', format: 'number' },
  { key: 'sector_growth_score', label: 'Growth Score', format: 'number' },
  { key: 'market_saturation', label: 'Saturation', format: 'text' },
  { key: 'competition_intensity', label: 'Competition', format: 'text' },
  { key: 'formality_rate', label: 'Formality', format: 'percent' },
  { key: 'data_quality_score', label: 'Quality', format: 'percent' },
]

// Computed
const totalBusinesses = computed(() => {
  return tableData.value.reduce((sum, row) => sum + (row.num_businesses || 0), 0)
})

const avgDensity = computed(() => {
  const validRows = tableData.value.filter(row => row.business_density_index > 0)
  if (validRows.length === 0) return 0
  return validRows.reduce((sum, row) => sum + row.business_density_index, 0) / validRows.length
})

const avgGrowth = computed(() => {
  const validRows = tableData.value.filter(row => row.sector_growth_score > 0)
  if (validRows.length === 0) return 0
  return validRows.reduce((sum, row) => sum + row.sector_growth_score, 0) / validRows.length
})

const avgFormality = computed(() => {
  const validRows = tableData.value.filter(row => row.formality_rate >= 0)
  if (validRows.length === 0) return 0
  return validRows.reduce((sum, row) => sum + row.formality_rate, 0) / validRows.length
})

// Methods
const loadData = async () => {
  loading.value = true
  error.value = null

  try {
    const params = {
      page: currentPage.value,
      per_page: perPage.value,
      ...filters.value,
    }

    // Remove null values
    Object.keys(params).forEach(key => {
      if (params[key] === null) delete params[key]
    })

    const response = await api.business.getIndex(params)

    tableData.value = response.data.data
    pagination.value = response.data.metadata
  } catch (err) {
    console.error('Failed to load business data:', err)
    error.value = err.response?.data?.message || 'Failed to load data. Please try again.'
  } finally {
    loading.value = false
  }
}

const changePage = (page) => {
  currentPage.value = page
  loadData()
}

const changePerPage = (newPerPage) => {
  perPage.value = newPerPage
  currentPage.value = 1
  loadData()
}

const loadFiltersData = async () => {
  try {
    const response = await api.business.getSectors()
    sectors.value = response.data
  } catch (err) {
    console.error('Failed to load business sectors:', err)
  }
}

const exportData = async (format) => {
  exporting.value = true
  
  try {
    const response = await api.export.business(format, filters.value)
    
    const extensions = { csv: 'csv', xlsx: 'xlsx', json: 'json', pdf: 'pdf', geojson: 'geojson' }
    const mimeTypes = {
      csv: 'text/csv',
      xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      json: 'application/json',
      pdf: 'application/pdf',
      geojson: 'application/geo+json'
    }
    
    const ext = extensions[format] || 'csv'
    const mimeType = mimeTypes[format] || 'text/csv'
    const filename = `tedi-business-${new Date().toISOString().split('T')[0]}.${ext}`
    
    let blob
    if (format === 'json') {
      blob = new Blob([JSON.stringify(response.data, null, 2)], { type: mimeType })
    } else {
      blob = new Blob([response.data], { type: mimeType })
    }
    
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch (err) {
    console.error('Export failed:', err)
    if (err.response?.status === 403) {
      alert('Export permission required. Please upgrade your API key.')
    } else {
      alert('Export failed. Please try again.')
    }
  } finally {
    exporting.value = false
  }
}

const formatNumber = (value) => {
  return formatPrice(value)
}

const formatSaturation = (level) => {
  const levels = {
    undersaturated: 'Undersaturated',
    balanced: 'Balanced',
    saturated: 'Saturated',
    oversaturated: 'Oversaturated'
  }
  return levels[level] || level
}

const formatCompetition = (level) => {
  const levels = {
    low: 'Low',
    medium: 'Medium',
    high: 'High'
  }
  return levels[level] || level
}

const getQualityColor = (score) => {
  if (score >= 0.9) return 'bg-green-500'
  if (score >= 0.7) return 'bg-yellow-500'
  return 'bg-red-500'
}

// Lifecycle
onMounted(() => {
  loadFiltersData()
  loadData()
})
</script>
