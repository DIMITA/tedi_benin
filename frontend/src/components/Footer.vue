<template>
  <footer class="footer-section">
    <div class="footer-container">
      <div class="footer-grid">
        <!-- Brand Column -->
        <div class="footer-brand">
          <div class="footer-logo">
            <div class="logo-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M12 2L2 7l10 5 10-5-10-5z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 17l10 5 10-5M2 12l10 5 10-5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <span class="logo-text">TEDI</span>
          </div>
          <p class="footer-tagline">
            Territorial & Economic Data Intelligence for Africa
          </p>
          <div class="footer-stats">
            <div class="footer-stat">
              <span class="stat-number">77</span>
              <span class="stat-text">Communes</span>
            </div>
            <div class="footer-stat">
              <span class="stat-number">68k+</span>
              <span class="stat-text">Data Points</span>
            </div>
          </div>
        </div>

        <!-- Data Indices Column (Auth required) -->
        <div v-if="isAuthenticated" class="footer-column">
          <h4 class="footer-title">Data Indices</h4>
          <ul class="footer-links">
            <li><router-link to="/agriculture">Agriculture Index</router-link></li>
            <li><router-link to="/realestate">Real Estate Index</router-link></li>
            <li><router-link to="/employment">Employment Index</router-link></li>
            <li><router-link to="/business">Business Index</router-link></li>
          </ul>
        </div>

        <!-- Platform Column -->
        <div class="footer-column">
          <h4 class="footer-title">Platform</h4>
          <ul class="footer-links">
            <li v-if="isAuthenticated"><router-link to="/dashboard">Dashboard</router-link></li>
            <li v-if="isAuthenticated"><router-link to="/api-keys">API Access</router-link></li>
            <li v-if="isAuthenticated"><router-link to="/map">Interactive Map</router-link></li>
            <li><router-link to="/data-sources">Data Sources</router-link></li>
            <li v-if="!isAuthenticated"><router-link to="/login">Sign In</router-link></li>
          </ul>
        </div>

        <!-- Resources Column -->
        <div class="footer-column">
          <h4 class="footer-title">Resources</h4>
          <ul class="footer-links">
            <li><router-link to="/documentation">Documentation</router-link></li>
            <li><router-link to="/api-reference">API Reference</router-link></li>
            <li><router-link to="/data-quality">Data Quality</router-link></li>
            <li><router-link to="/support">Support</router-link></li>
          </ul>
        </div>
      </div>

      <!-- Footer Bottom -->
      <div class="footer-bottom">
        <div class="footer-bottom-content">
          <p class="footer-copyright">
            © {{ currentYear }} TEDI Platform. All rights reserved.
          </p>
          <div class="footer-legal">
            <router-link to="/privacy">Privacy</router-link>
            <router-link to="/terms">Terms</router-link>
            <router-link to="/license">License</router-link>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)
const currentYear = new Date().getFullYear()
</script>

<style scoped>
/* ==================== FOOTER SECTION ==================== */
.footer-section {
  background: #1a1a2e;
  color: rgba(255, 255, 255, 0.8);
  padding: 4rem 2rem 2rem;
}

.footer-container {
  max-width: 1400px;
  margin: 0 auto;
}

.footer-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 3rem;
  margin-bottom: 3rem;
  padding-bottom: 3rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

@media (max-width: 1024px) {
  .footer-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .footer-grid {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
}

.footer-brand {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #2d5a27, #10b981);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.logo-text {
  font-size: 1.75rem;
  font-weight: 700;
  color: white;
}

.footer-tagline {
  font-size: 0.9375rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.6);
  max-width: 300px;
}

.footer-stats {
  display: flex;
  gap: 2rem;
  margin-top: 0.5rem;
}

.footer-stat {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: #10b981;
}

.stat-text {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.footer-column {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.footer-title {
  font-size: 1rem;
  font-weight: 700;
  color: white;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.5rem;
}

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.footer-links li a {
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  font-size: 0.9375rem;
  transition: all 0.2s ease;
  display: inline-block;
}

.footer-links li a:hover {
  color: #10b981;
  transform: translateX(4px);
}

.footer-bottom {
  padding-top: 2rem;
}

.footer-bottom-content {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 1.5rem;
}

@media (max-width: 768px) {
  .footer-bottom-content {
    flex-direction: column;
    text-align: center;
  }
}

.footer-copyright {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.5);
}

.footer-legal {
  display: flex;
  gap: 1.5rem;
}

.footer-legal a {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.5);
  text-decoration: none;
  transition: color 0.2s ease;
}

.footer-legal a:hover {
  color: #10b981;
}
</style>
