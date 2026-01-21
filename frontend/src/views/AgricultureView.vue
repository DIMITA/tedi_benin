<template>
  <div>
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-3xl font-bold text-gray-900">Agriculture Index</h1>
      <ExportDropdown
        v-if="canExport"
        :disabled="loading"
        :exporting="exporting"
        @export="exportData"
      />
    </div>

    <!-- Filters -->
    <FilterPanel
      v-model="filters"
      :communes="communes"
      :crops="crops"
      :years="availableYears"
      @filter-change="loadData"
    />

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
        empty-message="No agriculture data found. Try adjusting your filters."
      >
        <template #cell-commune="{ row }">
          <span class="font-medium text-gray-900">{{ row.commune?.name }}</span>
        </template>
        <template #cell-crop="{ row }">
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
            {{ row.crop?.name }}
          </span>
        </template>
        <template #cell-is_estimated="{ row }">
          <span
            class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
            :class="row.is_estimated ? 'bg-yellow-100 text-yellow-800' : 'bg-blue-100 text-blue-800'"
          >
            {{ row.is_estimated ? 'Estimated' : 'Measured' }}
          </span>
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
        <h4 class="text-sm font-medium text-gray-500 mb-1">Total Production</h4>
        <p class="text-2xl font-bold text-tedi-primary">{{ formatNumber(totalProduction) }} t</p>
      </div>
      <div class="card">
        <h4 class="text-sm font-medium text-gray-500 mb-1">Avg Yield</h4>
        <p class="text-2xl font-bold text-tedi-secondary">{{ formatNumber(avgYield) }} t/ha</p>
      </div>
      <div class="card">
        <h4 class="text-sm font-medium text-gray-500 mb-1">Total Area</h4>
        <p class="text-2xl font-bold text-tedi-accent">{{ formatNumber(totalArea) }} ha</p>
      </div>
      <div class="card">
        <h4 class="text-sm font-medium text-gray-500 mb-1">Avg Price</h4>
        <p class="text-2xl font-bold text-gray-900">{{ formatNumber(avgPrice) }} XOF/kg</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import DataTable from '@/components/DataTable.vue'
import FilterPanel from '@/components/FilterPanel.vue'
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
const communes = ref([])
const crops = ref([])
const filters = ref({
  commune_id: null,
  crop_id: null,
  year: null,
})

// Generate years from 2010 to current year
const currentYear = new Date().getFullYear()
const availableYears = Array.from({ length: currentYear - 2010 + 1 }, (_, i) => 2010 + i)

// Table columns configuration
const columns = [
  { key: 'commune', label: 'Commune', format: 'text' },
  { key: 'crop', label: 'Crop', format: 'text' },
  { key: 'year', label: 'Year', format: 'number' },
  { key: 'production_tonnes', label: 'Production (t)', format: 'number' },
  { key: 'yield_tonnes_per_ha', label: 'Yield (t/ha)', format: 'number' },
  { key: 'area_harvested_ha', label: 'Area (ha)', format: 'number' },
  { key: 'price_per_kg', label: 'Price (XOF/kg)', format: 'price' },
  { key: 'is_estimated', label: 'Type', format: 'text' },
  { key: 'data_quality_score', label: 'Quality', format: 'percent' },
]

// Computed
const totalProduction = computed(() => {
  return tableData.value.reduce((sum, row) => sum + (row.production_tonnes || 0), 0)
})

const avgYield = computed(() => {
  const validRows = tableData.value.filter(row => row.yield_tonnes_per_ha > 0)
  if (validRows.length === 0) return 0
  return validRows.reduce((sum, row) => sum + row.yield_tonnes_per_ha, 0) / validRows.length
})

const totalArea = computed(() => {
  return tableData.value.reduce((sum, row) => sum + (row.area_harvested_ha || 0), 0)
})

const avgPrice = computed(() => {
  const validRows = tableData.value.filter(row => row.price_per_kg > 0)
  if (validRows.length === 0) return 0
  return validRows.reduce((sum, row) => sum + row.price_per_kg, 0) / validRows.length
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

    const response = await api.agriculture.getIndex(params)

    tableData.value = response.data.data
    pagination.value = response.data.metadata
  } catch (err) {
    console.error('Failed to load agriculture data:', err)
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
    const [communesRes, cropsRes] = await Promise.all([
      api.agriculture.getCommunes(),
      api.agriculture.getCrops(),
    ])

    communes.value = communesRes.data
    crops.value = cropsRes.data
  } catch (err) {
    console.error('Failed to load filter data:', err)
  }
}

const exportData = async (format) => {
  exporting.value = true
  
  try {
    const response = await api.export.agriculture(format, filters.value)
    
    // Get file extension and MIME type
    const extensions = {
      csv: 'csv',
      xlsx: 'xlsx',
      json: 'json',
      pdf: 'pdf',
      geojson: 'geojson'
    }
    
    const mimeTypes = {
      csv: 'text/csv',
      xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      json: 'application/json',
      pdf: 'application/pdf',
      geojson: 'application/geo+json'
    }
    
    const ext = extensions[format] || 'csv'
    const mimeType = mimeTypes[format] || 'text/csv'
    const filename = `tedi-agriculture-${new Date().toISOString().split('T')[0]}.${ext}`
    
    // Handle JSON format differently (it returns JSON, not blob)
    let blob
    if (format === 'json') {
      blob = new Blob([JSON.stringify(response.data, null, 2)], { type: mimeType })
    } else {
      blob = new Blob([response.data], { type: mimeType })
    }
    
    // Download file
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
