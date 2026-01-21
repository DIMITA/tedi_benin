import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const apiKey = ref(localStorage.getItem('tedi_api_key') || '')
  const keyInfo = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const isAuthenticated = computed(() => !!apiKey.value)
  const isAdmin = computed(() => keyInfo.value?.is_admin || false)
  const canExport = computed(() => keyInfo.value?.can_export || false)
  const canApiDirect = computed(() => keyInfo.value?.can_api_direct || false)

  // Actions
  async function login(key) {
    loading.value = true
    error.value = null

    try {
      const response = await api.auth.validateKey(key)

      if (response.data.valid) {
        apiKey.value = key
        keyInfo.value = response.data.data
        localStorage.setItem('tedi_api_key', key)
        return true
      } else {
        error.value = response.data.message
        return false
      }
    } catch (err) {
      error.value = err.response?.data?.message || 'Invalid API key'
      return false
    } finally {
      loading.value = false
    }
  }

  function logout() {
    apiKey.value = ''
    keyInfo.value = null
    localStorage.removeItem('tedi_api_key')
  }

  async function checkAuth() {
    if (!apiKey.value) return false

    try {
      const response = await api.auth.validateKey(apiKey.value)
      if (response.data.valid) {
        keyInfo.value = response.data.data
        return true
      } else {
        logout()
        return false
      }
    } catch (err) {
      logout()
      return false
    }
  }

  // Register a new user (public registration with limited permissions)
  async function register(userData) {
    loading.value = true
    error.value = null

    try {
      const response = await api.auth.register(userData)
      
      if (response.data.api_key) {
        // Automatically log in with the new key
        apiKey.value = response.data.api_key
        keyInfo.value = response.data.data
        localStorage.setItem('tedi_api_key', response.data.api_key)
        return { success: true, data: response.data }
      }
      
      return { success: false, error: 'Registration failed' }
    } catch (err) {
      error.value = err.response?.data?.message || 'Registration failed'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  return {
    apiKey,
    keyInfo,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    canExport,
    canApiDirect,
    login,
    logout,
    checkAuth,
    register,
  }
})
