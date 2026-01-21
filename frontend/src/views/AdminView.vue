<template>
  <div class="flex h-screen bg-gray-100">
    <!-- Authentication Modal -->
    <div v-if="!isAuthenticated" class="fixed inset-0 bg-gray-900/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl p-8 max-w-md w-full mx-4">
        <h2 class="text-2xl font-bold text-gray-800 mb-6 text-center">🔐 Admin Access</h2>
        <form @submit.prevent="authenticate" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Admin Secret</label>
            <input
              v-model="adminSecret"
              type="password"
              class="input-field"
              placeholder="Enter admin secret"
              required
              autofocus
            />
          </div>
          <button type="submit" class="btn-primary w-full" :disabled="loading">
            {{ loading ? 'Authenticating...' : 'Login' }}
          </button>
          <p v-if="authError" class="text-red-600 text-sm text-center">{{ authError }}</p>
        </form>
        <router-link to="/" class="block text-center text-gray-500 text-sm mt-4 hover:underline">
          ← Back to home
        </router-link>
      </div>
    </div>

    <!-- Sidebar -->
    <aside v-if="isAuthenticated" class="w-64 bg-white shadow-lg flex flex-col">
      <div class="p-6 border-b">
        <h1 class="text-xl font-bold text-tedi-primary">🛡️ TEDI Admin</h1>
        <p class="text-sm text-gray-500">Key Management</p>
      </div>

      <nav class="flex-1 p-4 space-y-2">
        <button
          v-for="item in menuItems"
          :key="item.id"
          @click="currentSection = item.id"
          :class="[
            'w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors',
            currentSection === item.id 
              ? 'bg-tedi-primary text-white' 
              : 'text-gray-700 hover:bg-gray-100'
          ]"
        >
          <span class="text-xl">{{ item.icon }}</span>
          <span class="font-medium">{{ item.label }}</span>
        </button>
      </nav>

    
    </aside>

    <!-- Main Content -->
    <main v-if="isAuthenticated" class="flex-1 overflow-auto p-6">
      <!-- Dashboard Section -->
      <section v-if="currentSection === 'dashboard'">
        <h2 class="text-2xl font-bold text-gray-800 mb-6">📊 Dashboard</h2>
        
        <!-- Stats Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div class="bg-white rounded-lg shadow p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-gray-500 text-sm">Total Keys</p>
                <p class="text-3xl font-bold text-gray-800">{{ stats.total_keys }}</p>
              </div>
              <div class="text-4xl">🔑</div>
            </div>
          </div>
          <div class="bg-white rounded-lg shadow p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-gray-500 text-sm">Active Keys</p>
                <p class="text-3xl font-bold text-green-600">{{ stats.active_keys }}</p>
              </div>
              <div class="text-4xl">✅</div>
            </div>
          </div>
          <div class="bg-white rounded-lg shadow p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-gray-500 text-sm">Export Enabled</p>
                <p class="text-3xl font-bold text-blue-600">{{ stats.export_enabled }}</p>
              </div>
              <div class="text-4xl">📤</div>
            </div>
          </div>
          <div class="bg-white rounded-lg shadow p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-gray-500 text-sm">Total Requests</p>
                <p class="text-3xl font-bold text-purple-600">{{ totalRequests }}</p>
              </div>
              <div class="text-4xl">📈</div>
            </div>
          </div>
        </div>

        <!-- Requests by Key Chart -->
        <div class="bg-white rounded-lg shadow p-6 mb-8">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">📊 Requests by API Key</h3>
          <div class="space-y-3">
            <div v-for="key in topKeysByRequests" :key="key.id" class="flex items-center gap-4">
              <div class="w-40 truncate text-sm text-gray-600">{{ key.owner_name }}</div>
              <div class="flex-1 bg-gray-200 rounded-full h-4 overflow-hidden">
                <div 
                  class="h-full bg-gradient-to-r from-tedi-primary to-tedi-secondary rounded-full transition-all duration-500"
                  :style="{ width: `${(key.total_requests / maxRequests) * 100}%` }"
                ></div>
              </div>
              <div class="w-20 text-right text-sm font-medium text-gray-800">{{ key.total_requests }}</div>
            </div>
            <p v-if="topKeysByRequests.length === 0" class="text-gray-500 text-center py-4">No request data yet</p>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">🕐 Recent Activity</h3>
          <div class="overflow-x-auto">
            <table class="min-w-full">
              <thead>
                <tr class="text-left text-xs text-gray-500 uppercase">
                  <th class="pb-3">User</th>
                  <th class="pb-3">Email</th>
                  <th class="pb-3">Last Used</th>
                  <th class="pb-3">Requests</th>
                  <th class="pb-3">Status</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr v-for="key in recentlyActiveKeys" :key="key.id" class="text-sm">
                  <td class="py-3 font-medium text-gray-800">{{ key.owner_name }}</td>
                  <td class="py-3 text-gray-600">{{ key.owner_email }}</td>
                  <td class="py-3 text-gray-500">{{ formatDate(key.last_used_at) }}</td>
                  <td class="py-3 text-gray-800">{{ key.total_requests }}</td>
                  <td class="py-3">
                    <span :class="[
                      'px-2 py-1 text-xs rounded-full',
                      key.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                    ]">
                      {{ key.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- Manage Keys Section -->
      <section v-if="currentSection === 'keys'">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold text-gray-800">🔑 API Keys</h2>
          <button @click="loadKeys" class="text-tedi-primary hover:underline text-sm flex items-center gap-1">
            🔄 Refresh
          </button>
        </div>

        <!-- Keys Table -->
        <div class="bg-white rounded-lg shadow overflow-hidden">
          <table class="min-w-full">
            <thead class="bg-gray-50">
              <tr class="text-left text-xs text-gray-500 uppercase">
                <th class="px-4 py-3">ID</th>
                <th class="px-4 py-3">Name</th>
                <th class="px-4 py-3">Owner</th>
                <th class="px-4 py-3">Email</th>
                <th class="px-4 py-3">Permissions</th>
                <th class="px-4 py-3">Requests</th>
                <th class="px-4 py-3">Status</th>
                <th class="px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="key in apiKeys" :key="key.id" class="hover:bg-gray-50">
                <td class="px-4 py-3 text-sm text-gray-600">{{ key.id }}</td>
                <td class="px-4 py-3 text-sm font-medium text-gray-800">{{ key.name }}</td>
                <td class="px-4 py-3 text-sm text-gray-800">{{ key.owner_name }}</td>
                <td class="px-4 py-3 text-sm text-gray-600">{{ key.owner_email }}</td>
                <td class="px-4 py-3">
                  <div class="flex flex-wrap gap-1">
                    <span v-if="key.is_admin" class="px-2 py-0.5 text-xs bg-yellow-100 text-yellow-700 rounded">Admin</span>
                    <span v-if="key.can_export" class="px-2 py-0.5 text-xs bg-blue-100 text-blue-700 rounded">Export</span>
                    <span v-if="key.can_api_direct" class="px-2 py-0.5 text-xs bg-purple-100 text-purple-700 rounded">API</span>
                    <span v-if="!key.is_admin && !key.can_export && !key.can_api_direct" class="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">View Only</span>
                  </div>
                </td>
                <td class="px-4 py-3 text-sm text-gray-800">{{ key.total_requests }}</td>
                <td class="px-4 py-3">
                  <span :class="[
                    'px-2 py-1 text-xs rounded-full',
                    key.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                  ]">
                    {{ key.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="px-4 py-3">
                  <div class="flex gap-2">
                    <button @click="editKey(key)" class="p-1 text-blue-600 hover:bg-blue-50 rounded" title="Edit">
                      ✏️
                    </button>
                    <button @click="toggleKeyActive(key)" class="p-1 rounded" :class="key.is_active ? 'text-orange-600 hover:bg-orange-50' : 'text-green-600 hover:bg-green-50'" :title="key.is_active ? 'Disable' : 'Enable'">
                      {{ key.is_active ? '⏸️' : '▶️' }}
                    </button>
                    <button @click="confirmDeleteKey(key)" class="p-1 text-red-600 hover:bg-red-50 rounded" title="Delete">
                      🗑️
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          <p v-if="apiKeys.length === 0" class="text-gray-500 text-center py-8">No API keys found</p>
        </div>
      </section>

      <!-- Add Key Section -->
      <section v-if="currentSection === 'add'">
        <h2 class="text-2xl font-bold text-gray-800 mb-6">➕ Create API Key</h2>
        
        <div class="bg-white rounded-lg shadow p-6 max-w-2xl">
          <form @submit.prevent="createKey" class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Key Name *</label>
                <input v-model="newKey.name" type="text" class="input-field" placeholder="e.g., Production Key" required />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Owner Name *</label>
                <input v-model="newKey.owner_name" type="text" class="input-field" placeholder="Full name" required />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Email *</label>
                <input v-model="newKey.owner_email" type="email" class="input-field" placeholder="email@example.com" required />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Organization</label>
                <input v-model="newKey.owner_organization" type="text" class="input-field" placeholder="Company name" />
              </div>
            </div>

            <div class="border-t pt-4 mt-4">
              <p class="text-sm font-medium text-gray-700 mb-3">Permissions</p>
              <div class="flex flex-wrap gap-6">
                <label class="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" v-model="newKey.is_admin" class="w-4 h-4 text-tedi-primary rounded" />
                  <span class="text-sm text-gray-700">🛡️ Admin</span>
                </label>
                <label class="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" v-model="newKey.can_export" class="w-4 h-4 text-tedi-primary rounded" />
                  <span class="text-sm text-gray-700">📤 Can Export</span>
                </label>
                <label class="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" v-model="newKey.can_api_direct" class="w-4 h-4 text-tedi-primary rounded" />
                  <span class="text-sm text-gray-700">🔌 Direct API Access</span>
                </label>
              </div>
            </div>

            <div class="flex justify-end pt-4">
              <button type="submit" class="btn-primary" :disabled="loading">
                {{ loading ? 'Creating...' : '✨ Create Key' }}
              </button>
            </div>
          </form>

          <!-- Show created key -->
          <div v-if="createdKey" class="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <p class="text-green-800 font-medium mb-2">✅ Key created successfully!</p>
            <p class="text-sm text-green-700 mb-3">Copy this key now - it will only be shown once:</p>
            <div class="flex items-center gap-2">
              <code class="bg-white px-4 py-2 rounded border flex-1 text-sm break-all font-mono">{{ createdKey }}</code>
              <button @click="copyKey(createdKey)" class="btn-primary text-sm whitespace-nowrap">📋 Copy</button>
            </div>
          </div>
        </div>
      </section>

      <!-- Stats Section -->
      <section v-if="currentSection === 'stats'">
        <h2 class="text-2xl font-bold text-gray-800 mb-6">📈 Statistics</h2>

        <!-- Summary Cards -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div class="bg-white rounded-lg shadow p-6">
            <p class="text-gray-500 text-sm mb-1">Total API Requests</p>
            <p class="text-3xl font-bold text-tedi-primary">{{ totalRequests }}</p>
          </div>
          <div class="bg-white rounded-lg shadow p-6">
            <p class="text-gray-500 text-sm mb-1">Avg Requests/Key</p>
            <p class="text-3xl font-bold text-tedi-secondary">{{ avgRequestsPerKey }}</p>
          </div>
          <div class="bg-white rounded-lg shadow p-6">
            <p class="text-gray-500 text-sm mb-1">Most Active User</p>
            <p class="text-xl font-bold text-gray-800">{{ mostActiveUser }}</p>
          </div>
        </div>

        <!-- Detailed Stats Table -->
        <div class="bg-white rounded-lg shadow overflow-hidden">
          <div class="px-6 py-4 border-b">
            <h3 class="font-semibold text-gray-800">Usage Details by Key</h3>
          </div>
          <table class="min-w-full">
            <thead class="bg-gray-50">
              <tr class="text-left text-xs text-gray-500 uppercase">
                <th class="px-4 py-3">User</th>
                <th class="px-4 py-3">Email</th>
                <th class="px-4 py-3">Organization</th>
                <th class="px-4 py-3">Total Requests</th>
                <th class="px-4 py-3">Last Used</th>
                <th class="px-4 py-3">Created</th>
                <th class="px-4 py-3">% of Total</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="key in sortedKeysByRequests" :key="key.id" class="hover:bg-gray-50">
                <td class="px-4 py-3 font-medium text-gray-800">{{ key.owner_name }}</td>
                <td class="px-4 py-3 text-gray-600">{{ key.owner_email }}</td>
                <td class="px-4 py-3 text-gray-600">{{ key.owner_organization || '-' }}</td>
                <td class="px-4 py-3">
                  <span class="font-semibold text-tedi-primary">{{ key.total_requests }}</span>
                </td>
                <td class="px-4 py-3 text-gray-500 text-sm">{{ formatDate(key.last_used_at) }}</td>
                <td class="px-4 py-3 text-gray-500 text-sm">{{ formatDate(key.created_at) }}</td>
                <td class="px-4 py-3">
                  <div class="flex items-center gap-2">
                    <div class="w-16 bg-gray-200 rounded-full h-2">
                      <div 
                        class="h-full bg-tedi-primary rounded-full"
                        :style="{ width: `${totalRequests > 0 ? (key.total_requests / totalRequests) * 100 : 0}%` }"
                      ></div>
                    </div>
                    <span class="text-xs text-gray-500">{{ totalRequests > 0 ? ((key.total_requests / totalRequests) * 100).toFixed(1) : 0 }}%</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>

    <!-- Edit Modal -->
    <div v-if="editingKey" class="fixed inset-0 bg-gray-900/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
        <h3 class="text-xl font-bold text-gray-800 mb-4">Edit API Key</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Owner</label>
            <p class="text-gray-800">{{ editingKey.owner_name }} ({{ editingKey.owner_email }})</p>
          </div>
          <div class="space-y-2">
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" v-model="editingKey.is_active" class="w-4 h-4 text-tedi-primary rounded" />
              <span class="text-sm text-gray-700">Active</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" v-model="editingKey.is_admin" class="w-4 h-4 text-tedi-primary rounded" />
              <span class="text-sm text-gray-700">Admin</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" v-model="editingKey.can_export" class="w-4 h-4 text-tedi-primary rounded" />
              <span class="text-sm text-gray-700">Can Export</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" v-model="editingKey.can_api_direct" class="w-4 h-4 text-tedi-primary rounded" />
              <span class="text-sm text-gray-700">Direct API Access</span>
            </label>
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button @click="editingKey = null" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">Cancel</button>
          <button @click="saveKeyEdit" class="btn-primary" :disabled="loading">Save Changes</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="deletingKey" class="fixed inset-0 bg-gray-900/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
        <h3 class="text-xl font-bold text-gray-800 mb-4">🗑️ Delete API Key?</h3>
        <p class="text-gray-600 mb-4">
          Are you sure you want to delete the key for <strong>{{ deletingKey.owner_name }}</strong>?
          This action cannot be undone.
        </p>
        <div class="flex justify-end gap-3">
          <button @click="deletingKey = null" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">Cancel</button>
          <button @click="deleteKey" class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700" :disabled="loading">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '@/services/api'

// Auth state
const isAuthenticated = ref(false)
const adminSecret = ref('')
const authError = ref('')
const loading = ref(false)

// UI state
const currentSection = ref('dashboard')
const menuItems = [
  { id: 'dashboard', label: 'Dashboard', icon: '📊' },
  { id: 'keys', label: 'Manage Keys', icon: '🔑' },
  { id: 'add', label: 'Add Key', icon: '➕' },
  { id: 'stats', label: 'Statistics', icon: '📈' },
]

// Data state
const apiKeys = ref([])
const stats = ref({
  total_keys: 0,
  active_keys: 0,
  admin_keys: 0,
  export_enabled: 0,
  api_direct_enabled: 0
})

const createdKey = ref('')
const editingKey = ref(null)
const deletingKey = ref(null)

const newKey = reactive({
  name: '',
  owner_name: '',
  owner_email: '',
  owner_organization: '',
  is_admin: false,
  can_export: true,
  can_api_direct: true
})

// Computed
const totalRequests = computed(() => {
  return apiKeys.value.reduce((sum, key) => sum + (key.total_requests || 0), 0)
})

const maxRequests = computed(() => {
  return Math.max(...apiKeys.value.map(k => k.total_requests || 0), 1)
})

const avgRequestsPerKey = computed(() => {
  if (apiKeys.value.length === 0) return 0
  return Math.round(totalRequests.value / apiKeys.value.length)
})

const mostActiveUser = computed(() => {
  if (apiKeys.value.length === 0) return 'N/A'
  const sorted = [...apiKeys.value].sort((a, b) => (b.total_requests || 0) - (a.total_requests || 0))
  return sorted[0]?.owner_name || 'N/A'
})

const topKeysByRequests = computed(() => {
  return [...apiKeys.value]
    .filter(k => k.total_requests > 0)
    .sort((a, b) => (b.total_requests || 0) - (a.total_requests || 0))
    .slice(0, 5)
})

const sortedKeysByRequests = computed(() => {
  return [...apiKeys.value].sort((a, b) => (b.total_requests || 0) - (a.total_requests || 0))
})

const recentlyActiveKeys = computed(() => {
  return [...apiKeys.value]
    .filter(k => k.last_used_at)
    .sort((a, b) => new Date(b.last_used_at) - new Date(a.last_used_at))
    .slice(0, 5)
})

// Methods
onMounted(() => {
  const storedSecret = sessionStorage.getItem('tedi_admin_secret')
  if (storedSecret) {
    adminSecret.value = storedSecret
    authenticate()
  }
})

async function authenticate() {
  loading.value = true
  authError.value = ''

  try {
    const response = await api.admin.getKeys(adminSecret.value)
    isAuthenticated.value = true
    apiKeys.value = response.data.data
    stats.value = response.data.stats
    sessionStorage.setItem('tedi_admin_secret', adminSecret.value)
  } catch (err) {
    authError.value = 'Invalid admin secret'
    isAuthenticated.value = false
  }

  loading.value = false
}

async function loadKeys() {
  loading.value = true
  try {
    const response = await api.admin.getKeys(adminSecret.value)
    apiKeys.value = response.data.data
    stats.value = response.data.stats
  } catch (err) {
    console.error('Failed to load keys:', err)
  }
  loading.value = false
}

async function createKey() {
  loading.value = true
  createdKey.value = ''

  try {
    const response = await api.admin.createKey(adminSecret.value, {
      name: newKey.name,
      owner_name: newKey.owner_name,
      owner_email: newKey.owner_email,
      owner_organization: newKey.owner_organization || undefined,
      is_admin: newKey.is_admin,
      can_export: newKey.can_export,
      can_api_direct: newKey.can_api_direct
    })

    createdKey.value = response.data.data.key
    
    // Reset form
    Object.assign(newKey, {
      name: '',
      owner_name: '',
      owner_email: '',
      owner_organization: '',
      is_admin: false,
      can_export: true,
      can_api_direct: true
    })

    await loadKeys()
  } catch (err) {
    alert('Failed to create key: ' + (err.response?.data?.message || err.message))
  }

  loading.value = false
}

function editKey(key) {
  editingKey.value = { ...key }
}

async function saveKeyEdit() {
  loading.value = true
  try {
    await api.admin.updateKey(adminSecret.value, editingKey.value.id, {
      is_active: editingKey.value.is_active,
      is_admin: editingKey.value.is_admin,
      can_export: editingKey.value.can_export,
      can_api_direct: editingKey.value.can_api_direct
    })
    editingKey.value = null
    await loadKeys()
  } catch (err) {
    alert('Failed to update key: ' + (err.response?.data?.message || err.message))
  }
  loading.value = false
}

async function toggleKeyActive(key) {
  try {
    await api.admin.updateKey(adminSecret.value, key.id, {
      is_active: !key.is_active
    })
    await loadKeys()
  } catch (err) {
    alert('Failed to update key: ' + (err.response?.data?.message || err.message))
  }
}

function confirmDeleteKey(key) {
  deletingKey.value = key
}

async function deleteKey() {
  loading.value = true
  try {
    await api.admin.deleteKey(adminSecret.value, deletingKey.value.id)
    deletingKey.value = null
    await loadKeys()
  } catch (err) {
    alert('Failed to delete key: ' + (err.response?.data?.message || err.message))
  }
  loading.value = false
}

function copyKey(key) {
  navigator.clipboard.writeText(key)
  alert('Key copied to clipboard!')
}

function formatDate(dateStr) {
  if (!dateStr) return 'Never'
  const date = new Date(dateStr)
  return date.toLocaleDateString('fr-FR', { 
    day: '2-digit', 
    month: 'short', 
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function logout() {
  isAuthenticated.value = false
  adminSecret.value = ''
  sessionStorage.removeItem('tedi_admin_secret')
}
</script>

<style scoped>
.input-field {
  @apply w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-tedi-primary focus:border-transparent;
}
</style>
