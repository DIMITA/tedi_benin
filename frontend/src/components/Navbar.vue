<template>
  <nav class="bg-white shadow-lg" v-if="isAuthenticated">
    <div class="container mx-auto px-4">
      <div class="flex justify-between items-center h-16">
        <div class="flex items-center space-x-8">
          <router-link to="/" class="text-2xl font-bold text-tedi-primary flex items-center space-x-2">
            <div class="logo-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M12 2L2 7l10 5 10-5-10-5z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 17l10 5 10-5M2 12l10 5 10-5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            TEDI
          </router-link>
          <div class="hidden md:flex space-x-4">
            <router-link
              to="/dashboard"
              class="nav-link"
              v-if="isAuthenticated"
              active-class="text-tedi-primary font-semibold"
            >
              Dashboard
            </router-link>
            <router-link
              to="/agriculture"
              class="nav-link"
              v-if="isAuthenticated"
              active-class="text-tedi-primary font-semibold"
            >
              🌾 Agriculture
            </router-link>
            <router-link
              to="/realestate"
              class="nav-link"
              v-if="isAuthenticated"
              active-class="text-tedi-primary font-semibold"
            >
              🏠 Real Estate
            </router-link>
            <router-link
              to="/employment"
              v-if="isAuthenticated"
              class="nav-link"
              active-class="text-tedi-primary font-semibold"
            >
              💼 Employment
            </router-link>
            <router-link
              to="/business"
              v-if="isAuthenticated"
              class="nav-link"
              active-class="text-tedi-primary font-semibold"
            >
              🏢 Business
            </router-link>
            <router-link
              to="/api-keys"
              v-if="isAuthenticated"
              class="nav-link"
              active-class="text-tedi-primary font-semibold"
            >
              API Keys
            </router-link>
          </div>
        </div>
        <div class="flex items-center space-x-4" v-if="isAuthenticated">
          <span class="text-sm text-gray-600">{{ keyInfo?.owner_email }}</span>
          <button @click="handleLogout" class="btn-secondary text-sm">
            Logout
          </button>
        </div>
        <div class="flex items-center space-x-4" v-if="!isAuthenticated">
          <router-link
              to="/login"
              v-if="isAuthenticated"
              class="nav-link"
              active-class="text-tedi-primary font-semibold"
            >
              Login
            </router-link>
        </div>
      </div>
    </div>
  </nav>

</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)
const isLandingPage = computed(() => route.name === 'landing')

const keyInfo = computed(() => authStore.keyInfo)

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.nav-link {
  @apply text-gray-700 hover:text-tedi-primary transition-colors duration-200;
}
</style>
