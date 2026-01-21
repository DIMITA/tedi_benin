import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api/v1'

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add API key
apiClient.interceptors.request.use(
  (config) => {
    const apiKey = localStorage.getItem('tedi_api_key')
    if (apiKey) {
      config.headers['X-API-KEY'] = apiKey
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Don't redirect to login for admin endpoints - they have their own auth
    const isAdminEndpoint = error.config?.url?.includes('/admin/')
    if (error.response?.status === 401 && !isAdminEndpoint) {
      // Unauthorized - clear API key and redirect to login
      localStorage.removeItem('tedi_api_key')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default {
  // Public endpoints (no auth required)
  public: {
    getStats() {
      return apiClient.get('/public/stats')
    },
    getCommunes() {
      return apiClient.get('/public/communes')
    },
    getCommuneSummary(communeId) {
      return apiClient.get(`/public/communes/${communeId}/summary`)
    },
  },

  // Agriculture endpoints
  agriculture: {
    getCommunes() {
      return apiClient.get('/agriculture/communes')
    },
    getCommune(id) {
      return apiClient.get(`/agriculture/communes/${id}`)
    },
    getCrops() {
      return apiClient.get('/agriculture/crops')
    },
    getCrop(id) {
      return apiClient.get(`/agriculture/crops/${id}`)
    },
    getIndex(params = {}) {
      return apiClient.get('/agriculture/index', { params })
    },
    getIndexDetail(communeId, cropId, year) {
      return apiClient.get(`/agriculture/index/${communeId}/${cropId}/${year}`)
    },
    getAggregatedStats(params = {}) {
      return apiClient.get('/agriculture/stats/aggregated', { params })
    },
  },

  // Real Estate endpoints
  realestate: {
    getPropertyTypes() {
      return apiClient.get('/realestate/property-types')
    },
    getPropertyType(id) {
      return apiClient.get(`/realestate/property-types/${id}`)
    },
    getIndex(params = {}) {
      return apiClient.get('/realestate/index', { params })
    },
    getStats(id) {
      return apiClient.get(`/realestate/stats/${id}`)
    },
    getAggregatedStats(params = {}) {
      return apiClient.get('/realestate/stats/aggregated', { params })
    },
  },

  // Employment endpoints
  employment: {
    getJobCategories() {
      return apiClient.get('/employment/categories')
    },
    getJobCategory(id) {
      return apiClient.get(`/employment/categories/${id}`)
    },
    getIndex(params = {}) {
      return apiClient.get('/employment/index', { params })
    },
    getStats(id) {
      return apiClient.get(`/employment/stats/${id}`)
    },
    getAggregatedStats(params = {}) {
      return apiClient.get('/employment/stats/aggregated', { params })
    },
  },

  // Business endpoints
  business: {
    getSectors() {
      return apiClient.get('/business/sectors')
    },
    getSector(id) {
      return apiClient.get(`/business/sectors/${id}`)
    },
    getIndex(params = {}) {
      return apiClient.get('/business/index', { params })
    },
    getStats(id) {
      return apiClient.get(`/business/stats/${id}`)
    },
    getAggregatedStats(params = {}) {
      return apiClient.get('/business/stats/aggregated', { params })
    },
  },

  // Auth endpoints
  auth: {
    validateKey(key) {
      return apiClient.get('/auth/validate', { params: { key } })
    },
    // Public registration (creates key with limited permissions)
    register(data) {
      return apiClient.post('/auth/register', data)
    },
    createKey(data) {
      return apiClient.post('/auth/keys', data)
    },
    getKeys(email) {
      return apiClient.get('/auth/keys', { params: { email } })
    },
    getKey(id) {
      return apiClient.get(`/auth/keys/${id}`)
    },
    updateKey(id, data) {
      return apiClient.patch(`/auth/keys/${id}`, data)
    },
    deleteKey(id) {
      return apiClient.delete(`/auth/keys/${id}`)
    },
  },

  // Admin endpoints (require admin secret)
  admin: {
    getKeys(adminSecret) {
      return apiClient.get('/auth/admin/keys', {
        headers: { 'X-Admin-Secret': adminSecret }
      })
    },
    createKey(adminSecret, data) {
      return apiClient.post('/auth/admin/keys', data, {
        headers: { 'X-Admin-Secret': adminSecret }
      })
    },
    updateKey(adminSecret, keyId, data) {
      return apiClient.patch(`/auth/admin/keys/${keyId}`, data, {
        headers: { 'X-Admin-Secret': adminSecret }
      })
    },
    deleteKey(adminSecret, keyId) {
      return apiClient.delete(`/auth/admin/keys/${keyId}`, {
        headers: { 'X-Admin-Secret': adminSecret }
      })
    },
  },

  // Export endpoints
  export: {
    getFormats() {
      return apiClient.get('/export/formats')
    },
    // Helper to clean filters (remove null/undefined values)
    _cleanFilters(filters) {
      const cleaned = {}
      Object.keys(filters).forEach(key => {
        if (filters[key] !== null && filters[key] !== undefined && filters[key] !== '') {
          cleaned[key] = filters[key]
        }
      })
      return cleaned
    },
    agriculture(format = 'csv', filters = {}) {
      return apiClient.get('/export/agriculture', {
        params: { format, ...this._cleanFilters(filters) },
        responseType: format === 'json' ? 'json' : 'blob'
      })
    },
    realestate(format = 'csv', filters = {}) {
      return apiClient.get('/export/realestate', {
        params: { format, ...this._cleanFilters(filters) },
        responseType: format === 'json' ? 'json' : 'blob'
      })
    },
    employment(format = 'csv', filters = {}) {
      return apiClient.get('/export/employment', {
        params: { format, ...this._cleanFilters(filters) },
        responseType: format === 'json' ? 'json' : 'blob'
      })
    },
    business(format = 'csv', filters = {}) {
      return apiClient.get('/export/business', {
        params: { format, ...this._cleanFilters(filters) },
        responseType: format === 'json' ? 'json' : 'blob'
      })
    },
  },
}
