<template>
  <div class="p-48 flex items-center justify-center from-blue-50 to-indigo-100">
    <div class="card max-w-md w-full">
      <h1 class="text-3xl font-bold text-center text-tedi-primary mb-2">TEDI</h1>
      <p class="text-center text-gray-600 mb-6">Territorial & Economic Data Index</p>

      <!-- Tab Navigation -->
      <div class="flex mb-6 border-b border-gray-200">
        <button
          @click="activeTab = 'login'"
          :class="[
            'flex-1 py-2 text-sm font-medium border-b-2 transition-colors',
            activeTab === 'login' 
              ? 'border-tedi-primary text-tedi-primary' 
              : 'border-transparent text-gray-500 hover:text-gray-700'
          ]"
        >
          Login
        </button>
        <button
          @click="activeTab = 'register'"
          :class="[
            'flex-1 py-2 text-sm font-medium border-b-2 transition-colors',
            activeTab === 'register' 
              ? 'border-tedi-primary text-tedi-primary' 
              : 'border-transparent text-gray-500 hover:text-gray-700'
          ]"
        >
          Register
        </button>
      </div>

      <!-- Login Form -->
      <form v-if="activeTab === 'login'" @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label for="apiKey" class="block text-sm font-medium text-gray-700 mb-2">
            API Key
          </label>
          <input
            id="apiKey"
            v-model="apiKeyInput"
            type="text"
            class="input-field"
            placeholder="Enter your API key"
            required
          />
        </div>

        <button
          type="submit"
          class="btn-primary w-full"
          :disabled="loading"
        >
          {{ loading ? 'Validating...' : 'Login' }}
        </button>
      </form>

      <!-- Register Form -->
      <form v-if="activeTab === 'register'" @submit.prevent="handleRegister" class="space-y-4">
        <div>
          <label for="name" class="block text-sm font-medium text-gray-700 mb-2">
            Full Name *
          </label>
          <input
            id="name"
            v-model="registerForm.name"
            type="text"
            class="input-field"
            placeholder="Enter your full name"
            required
          />
        </div>

        <div>
          <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
            Email *
          </label>
          <input
            id="email"
            v-model="registerForm.email"
            type="email"
            class="input-field"
            placeholder="Enter your email"
            required
          />
        </div>

        <div>
          <label for="organization" class="block text-sm font-medium text-gray-700 mb-2">
            Organization (optional)
          </label>
          <input
            id="organization"
            v-model="registerForm.organization"
            type="text"
            class="input-field"
            placeholder="Your company or organization"
          />
        </div>

        <button
          type="submit"
          class="btn-primary w-full"
          :disabled="loading"
        >
          {{ loading ? 'Creating account...' : 'Get API Key' }}
        </button>

        <p class="text-xs text-gray-500 text-center">
          By registering, you get access to view data on the dashboard.
          Export and direct API access require admin approval.
        </p>
      </form>

      <!-- Success Message -->
      <div v-if="registrationSuccess" class="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
        <p class="text-green-800 font-medium mb-2">🎉 Registration successful!</p>
        <p class="text-green-700 text-sm mb-2">Your API key has been created and you are now logged in.</p>
        <p class="text-green-600 text-xs">
          <strong>Note:</strong> You can view data but export features require admin approval.
        </p>
      </div>

      <p v-if="error" class="mt-4 text-red-600 text-sm text-center">
        {{ error }}
      </p>

      <div v-if="!registrationSuccess" class="mt-6 pt-6 border-t border-gray-200">
        <p v-if="activeTab === 'login'" class="text-sm text-gray-600 text-center">
          Don't have an API key? Switch to the Register tab above.
        </p>
        <p v-else class="text-sm text-gray-600 text-center">
          Already have an API key? Switch to the Login tab above.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref('login')
const apiKeyInput = ref('')
const loading = ref(false)
const error = ref('')
const registrationSuccess = ref(false)

const registerForm = reactive({
  name: '',
  email: '',
  organization: ''
})

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  registrationSuccess.value = false

  const success = await authStore.login(apiKeyInput.value)

  if (success) {
    router.push('/')
  } else {
    error.value = authStore.error
  }

  loading.value = false
}

const handleRegister = async () => {
  loading.value = true
  error.value = ''
  registrationSuccess.value = false

  const result = await authStore.register({
    name: registerForm.name,
    email: registerForm.email,
    organization: registerForm.organization || undefined
  })

  if (result.success) {
    registrationSuccess.value = true
    // Wait a moment then redirect
    setTimeout(() => {
      router.push('/')
    }, 2000)
  } else {
    error.value = result.error
  }

  loading.value = false
}
</script>
