<template>
  <div id="app" class="min-h-screen flex flex-col">
    <Navbar />
    <main :class="['flex-grow', isLandingPage ? '' : 'container mx-auto px-4 py-8']">
      <router-view />
    </main>
    <Footer v-if="!isLandingPage" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Navbar from '@/components/Navbar.vue'
import Footer from '@/components/Footer.vue'

const route = useRoute()
const authStore = useAuthStore()

const isLandingPage = computed(() => route.name === 'landing')
</script>

<style scoped>
#app {
  font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
