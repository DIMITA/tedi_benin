<template>
  <div>
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-3xl font-bold text-gray-900">API Keys Management</h1>
      <button @click="showCreateModal = true" class="btn-primary">
        <svg class="inline-block w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Create New Key
      </button>
    </div>

    <!-- Current API Key Info -->
    <div class="card mb-6 bg-blue-50 border border-blue-200">
      <h3 class="text-lg font-semibold mb-2 text-blue-900">Your Current API Key</h3>
      <div class="flex items-center justify-between">
        <code class="px-3 py-2 bg-white rounded text-sm">{{ maskedApiKey }}</code>
        <span class="text-sm text-blue-600">Active</span>
      </div>
    </div>

    <!-- API Keys List (Placeholder) -->
    <div class="card">
      <h2 class="text-xl font-semibold mb-4">How to Use API Keys</h2>
      <div class="space-y-4 text-gray-700">
        <p>
          API keys are used to authenticate requests to the TEDI API. Include your API key in the
          <code class="px-2 py-1 bg-gray-100 rounded">X-API-KEY</code> header of your HTTP requests.
        </p>

        <div>
          <h3 class="font-semibold mb-2">Example Request:</h3>
          <pre class="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">curl -H "X-API-KEY: your-api-key-here" \
  https://api.tedi.africa/api/v1/agriculture/communes</pre>
        </div>

        <div>
          <h3 class="font-semibold mb-2">Rate Limits:</h3>
          <ul class="list-disc list-inside space-y-1">
            <li>1,000 requests per hour</li>
            <li>10,000 requests per day</li>
          </ul>
        </div>

        <div>
          <h3 class="font-semibold mb-2">Available Endpoints:</h3>
          <ul class="list-disc list-inside space-y-1">
            <li><code class="px-2 py-1 bg-gray-100 rounded">/api/v1/agriculture/communes</code> - List all communes</li>
            <li><code class="px-2 py-1 bg-gray-100 rounded">/api/v1/agriculture/crops</code> - List all crops</li>
            <li><code class="px-2 py-1 bg-gray-100 rounded">/api/v1/agriculture/index</code> - Get agriculture statistics</li>
          </ul>
        </div>

        <div class="mt-4 pt-4 border-t border-gray-200">
          <a
            href="/api-reference"
            class="text-tedi-primary hover:underline"
          >
            → View Full API Documentation
          </a>
        </div>
      </div>
    </div>

    <!-- Create API Key Modal -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showCreateModal = false"
    >
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-xl font-semibold mb-4">Create New API Key</h3>

        <form @submit.prevent="createApiKey" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Key Name *
            </label>
            <input
              v-model="newKey.name"
              type="text"
              class="input-field"
              placeholder="Production Key"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Owner Name *
            </label>
            <input
              v-model="newKey.owner_name"
              type="text"
              class="input-field"
              placeholder="John Doe"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Email *
            </label>
            <input
              v-model="newKey.owner_email"
              type="email"
              class="input-field"
              placeholder="john@example.com"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Organization
            </label>
            <input
              v-model="newKey.owner_organization"
              type="text"
              class="input-field"
              placeholder="My Company"
            />
          </div>

          <div v-if="createdKey" class="p-4 bg-green-50 border border-green-200 rounded">
            <p class="text-sm font-medium text-green-800 mb-2">
              API Key Created Successfully!
            </p>
            <code class="block px-3 py-2 bg-white rounded text-sm break-all">{{ createdKey }}</code>
            <p class="text-xs text-green-600 mt-2">
              ⚠️ Save this key now. You won't be able to see it again!
            </p>
          </div>

          <div v-if="error" class="p-4 bg-red-50 border border-red-200 rounded">
            <p class="text-sm text-red-800">{{ error }}</p>
          </div>

          <div class="flex space-x-3">
            <button
              type="submit"
              class="btn-primary flex-1"
              :disabled="loading || createdKey"
            >
              {{ loading ? 'Creating...' : 'Create Key' }}
            </button>
            <button
              type="button"
              @click="closeModal"
              class="btn-secondary flex-1"
            >
              {{ createdKey ? 'Close' : 'Cancel' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const authStore = useAuthStore()

// State
const showCreateModal = ref(false)
const loading = ref(false)
const error = ref(null)
const createdKey = ref(null)
const newKey = ref({
  name: '',
  owner_name: '',
  owner_email: '',
  owner_organization: '',
})

// Computed
const maskedApiKey = computed(() => {
  const key = authStore.apiKey
  if (!key) return ''
  return key.substring(0, 12) + '...' + key.substring(key.length - 8)
})

// Methods
const createApiKey = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await api.auth.createKey({
      ...newKey.value,
      scopes: ['agriculture:read'],
      expires_in_days: 365,
    })

    createdKey.value = response.data.key
  } catch (err) {
    console.error('Failed to create API key:', err)
    error.value = err.response?.data?.message || 'Failed to create API key'
  } finally {
    loading.value = false
  }
}

const closeModal = () => {
  showCreateModal.value = false
  newKey.value = {
    name: '',
    owner_name: '',
    owner_email: '',
    owner_organization: '',
  }
  createdKey.value = null
  error.value = null
}
</script>
