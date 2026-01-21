<template>
  <div class="landing-page" itemscope itemtype="https://schema.org/WebPage">
    <!-- SEO Content for Search Engines (Screen reader friendly) -->
    <div class="sr-only" aria-hidden="false">
      <h1>TEDI Bénin - Données Économiques et Territoriales du Bénin</h1>
      <p>TEDI est la plateforme de référence pour accéder aux données économiques du Bénin. 
         Retrouvez toutes les statistiques sur l'agriculture au Bénin, l'immobilier au Bénin, 
         l'emploi au Bénin et les entreprises béninoises.</p>
      <h2>Agriculture Bénin - Données de Production Agricole</h2>
      <p>Consultez les statistiques agricoles du Bénin : production de maïs, coton, manioc, 
         igname et autres cultures. Données par commune et par année depuis 2010.</p>
      <h2>Immobilier Bénin - Prix et Tendances du Marché</h2>
      <p>Analysez le marché immobilier béninois : prix au m², tendances par ville et commune, 
         données immobilières de Cotonou, Porto-Novo, Parakou et toutes les régions du Bénin.</p>
      <h2>Emploi Bénin - Statistiques du Marché du Travail</h2>
      <p>Découvrez les données sur l'emploi au Bénin : taux de chômage, salaires moyens, 
         offres d'emploi par secteur et par région.</p>
      <h2>Business Bénin - Environnement des Affaires</h2>
      <p>Explorez les opportunités d'investissement au Bénin : création d'entreprises, 
         secteurs économiques, données commerciales et indicateurs de croissance.</p>
    </div>

    <!-- Hero Section with Animated Background -->
    <section class="hero-section" aria-label="Présentation TEDI">
      <div class="hero-pattern"></div>
      <div class="hero-gradient"></div>

      <div class="hero-content">
        <div class="hero-badge">
          <span class="badge-dot"></span>
          Territorial & Economic Data Intelligence
        </div>

        <h1 class="hero-title" itemprop="name">
          <span class="title-line" style="animation-delay: 0.1s">Données</span>
          <span class="title-line" style="animation-delay: 0.2s">Économiques</span>
          <span class="title-line title-highlight" style="animation-delay: 0.3s">du Bénin</span>
        </h1>

        <p class="hero-subtitle" style="animation-delay: 0.5s" itemprop="description">
          Accédez aux données économiques et territoriales du Bénin en temps réel.
          Agriculture, immobilier, emploi et business - tout sur une seule plateforme.
        </p>

        <div class="hero-cta" style="animation-delay: 0.7s">
          <router-link to="/login" class="btn-primary">
            <span>Commencer</span>
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M4 10h12m0 0l-4-4m4 4l-4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </router-link>
          <a href="#explore" class="btn-secondary">
            Explorer les données
          </a>
        </div>
      </div>

      <!-- Decorative Elements -->
      <div class="hero-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="stats-section" aria-label="Statistiques de la plateforme">
      <div class="stats-container">
        <div class="stat-card" style="animation-delay: 0.1s">
          <div class="stat-icon stat-icon-1">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M12 2L2 7l10 5 10-5-10-5z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 17l10 5 10-5M2 12l10 5 10-5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ formatNumber(overview.communes) }}</div>
            <div class="stat-label">Communes du Bénin</div>
          </div>
          <div class="stat-pattern pattern-1"></div>
        </div>

        <div class="stat-card" style="animation-delay: 0.2s">
          <div class="stat-icon stat-icon-2">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M20 7h-9M14 17H5M3 12h18" stroke-width="2" stroke-linecap="round"/>
              <circle cx="17" cy="7" r="2" stroke-width="2"/>
              <circle cx="7" cy="17" r="2" stroke-width="2"/>
              <circle cx="12" cy="12" r="2" stroke-width="2"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ formatNumber(overview.dataSources) }}</div>
            <div class="stat-label">Sources de données</div>
          </div>
          <div class="stat-pattern pattern-2"></div>
        </div>

        <div class="stat-card" style="animation-delay: 0.3s">
          <div class="stat-icon stat-icon-3">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M3 3v18h18" stroke-width="2" stroke-linecap="round"/>
              <path d="M18 9l-4 4-3-3-4 4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ formatNumber(overview.dataPoints) }}</div>
            <div class="stat-label">Points de données</div>
          </div>
          <div class="stat-pattern pattern-3"></div>
        </div>

        <div class="stat-card" style="animation-delay: 0.4s">
          <div class="stat-icon stat-icon-4">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke-width="2" stroke-linecap="round"/>
              <circle cx="9" cy="7" r="4" stroke-width="2"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ formatNumber(overview.activeUsers) }}</div>
            <div class="stat-label">Utilisateurs actifs</div>
          </div>
          <div class="stat-pattern pattern-4"></div>
        </div>
      </div>
    </section>

    <!-- Map Exploration Section -->
    <section id="explore" class="map-section" aria-label="Carte interactive du Bénin">
      <div class="section-header">
        <div class="section-badge">Exploration interactive</div>
        <h2 class="section-title">
          Découvrez les données <span class="title-accent">par région</span>
        </h2>
        <p class="section-subtitle">
          Cliquez sur n'importe quelle commune pour découvrir les statistiques économiques et territoriales
        </p>
      </div>

      <div class="map-layout">
        <!-- Map Container -->
        <div class="map-wrapper">
          <div class="map-container">
            <div id="landing-map"></div>
            <div class="map-overlay">
              <div class="map-legend">
                <div class="legend-item">
                  <div class="legend-dot legend-active"></div>
                  <span>Data Available</span>
                </div>
                <div class="legend-item">
                  <div class="legend-dot legend-inactive"></div>
                  <span>No Data</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Stats Sidebar -->
        <div class="sidebar-wrapper">
          <!-- Selected Commune Stats -->
          <div v-if="selectedCommune" class="commune-panel">
            <div class="panel-header">
              <div>
                <h3 class="commune-name">{{ selectedCommune.name }}</h3>
                <p class="commune-region">{{ selectedCommune.region?.name }}</p>
              </div>
              <button @click="selectedCommune = null" class="btn-close">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor">
                  <path d="M15 5L5 15M5 5l10 10" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </button>
            </div>

            <div class="commune-info">
              <div class="info-row">
                <span class="info-label">Population</span>
                <span class="info-value">{{ formatNumber(selectedCommune.population) }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Area</span>
                <span class="info-value">{{ formatNumber(selectedCommune.area_km2) }} km²</span>
              </div>
              <div class="info-row">
                <span class="info-label">Coordinates</span>
                <span class="info-value coord">
                  {{ selectedCommune.center_lat?.toFixed(4) }}, {{ selectedCommune.center_lon?.toFixed(4) }}
                </span>
              </div>
            </div>

            <!-- Loading State -->
            <div v-if="loadingStats" class="loading-state">
              <div class="spinner"></div>
              <p>Loading statistics...</p>
            </div>

            <!-- Data Stats -->
            <div v-else-if="communeStats" class="data-stats">
              <h4 class="stats-title">Available Data</h4>

              <!-- Agriculture -->
              <div class="data-item">
                <div class="data-header">
                  <div class="data-icon data-icon-agri">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path d="M12 2v20M2 12h20" stroke-width="2"/>
                      <path d="M7.5 7.5c0 2-1.5 3.5-3.5 3.5M16.5 7.5c0 2 1.5 3.5 3.5 3.5" stroke-width="1.5"/>
                    </svg>
                  </div>
                  <div class="data-info">
                    <div class="data-name">Agriculture</div>
                    <div class="data-desc">Crops & Production</div>
                  </div>
                  <div class="data-count">{{ communeStats.agriculture.count }}</div>
                </div>
                <div v-if="communeStats.agriculture.topCrops.length" class="crop-tags">
                  <span v-for="crop in communeStats.agriculture.topCrops" :key="crop" class="crop-tag">
                    {{ crop }}
                  </span>
                </div>
              </div>

              <!-- Employment -->
              <div class="data-item">
                <div class="data-header">
                  <div class="data-icon data-icon-employ">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke-width="2"/>
                      <circle cx="9" cy="7" r="4" stroke-width="2"/>
                      <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" stroke-width="2"/>
                    </svg>
                  </div>
                  <div class="data-info">
                    <div class="data-name">Employment</div>
                    <div class="data-desc">Labor Statistics</div>
                  </div>
                  <div class="data-count">{{ communeStats.employment.count }}</div>
                </div>
              </div>

              <!-- Business -->
              <div class="data-item">
                <div class="data-header">
                  <div class="data-icon data-icon-business">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <rect x="3" y="3" width="18" height="18" rx="2" stroke-width="2"/>
                      <path d="M3 9h18M9 21V9" stroke-width="2"/>
                    </svg>
                  </div>
                  <div class="data-info">
                    <div class="data-name">Business</div>
                    <div class="data-desc">Economic Activity</div>
                  </div>
                  <div class="data-count">{{ communeStats.business.count }}</div>
                </div>
              </div>

              <!-- Real Estate -->
              <div class="data-item">
                <div class="data-header">
                  <div class="data-icon data-icon-realestate">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" stroke-width="2"/>
                      <path d="M9 22V12h6v10" stroke-width="2"/>
                    </svg>
                  </div>
                  <div class="data-info">
                    <div class="data-name">Real Estate</div>
                    <div class="data-desc">Property & Land</div>
                  </div>
                  <div class="data-count">{{ communeStats.realestate.count }}</div>
                </div>
              </div>

              <!-- Total -->
              <div class="total-bar">
                <div class="total-label">Total Data Points</div>
                <div class="total-value">{{ formatNumber(communeStats.total) }}</div>
              </div>

              <router-link
                :to="{ name: 'agriculture', query: { commune_id: selectedCommune.id } }"
                class="btn-view-all"
              >
                View Full Dataset
                <svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor">
                  <path d="M4 10h12m0 0l-4-4m4 4l-4 4" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </router-link>
            </div>

            <!-- No Data State -->
            <div v-else-if="!loadingStats && !communeStats" class="empty-state">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" stroke-width="1.5"/>
              </svg>
              <p>No data available for this commune</p>
            </div>
          </div>

          <!-- Default Prompt -->
          <div v-else class="prompt-panel">
            <div class="prompt-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" stroke-width="2"/>
                <circle cx="12" cy="10" r="3" stroke-width="2"/>
              </svg>
            </div>
            <h3 class="prompt-title">Sélectionnez une commune</h3>
            <p class="prompt-text">Cliquez sur un marqueur de la carte pour explorer les statistiques détaillées de cette région</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section" aria-label="Fonctionnalités de la plateforme">
      <div class="features-pattern"></div>

      <div class="features-content">
        <div class="section-header">
          <div class="section-badge">Capacités de la plateforme</div>
          <h2 class="section-title">
            Conçu pour <span class="title-accent">la croissance africaine</span>
          </h2>
          <p class="section-subtitle">
            Une plateforme de données complète conçue spécifiquement pour le contexte africain
          </p>
        </div>

        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon feature-icon-1">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" stroke-width="2" stroke-linecap="round"/>
                <path d="M22 4L12 14.01l-3-3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <h3 class="feature-title">Sources de données vérifiées</h3>
            <p class="feature-desc">
              Agrégées d'organisations internationales de confiance : FAOSTAT, Banque Mondiale,
              ILOSTAT et OpenStreetMap pour une fiabilité maximale.
            </p>
            <div class="feature-pattern"></div>
          </div>

          <div class="feature-card">
            <div class="feature-icon feature-icon-2">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" stroke-width="2"/>
                <path d="M3.27 6.96L12 12.01l8.73-5.05M12 22.08V12" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </div>
            <h3 class="feature-title">Mises à jour en temps réel</h3>
            <p class="feature-desc">
              L'ingestion automatique des données toutes les 6 heures garantit un accès permanent
              aux informations les plus récentes.
            </p>
            <div class="feature-pattern"></div>
          </div>

          <div class="feature-card">
            <div class="feature-icon feature-icon-3">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M16 18l2-2 4 4" stroke-width="2" stroke-linecap="round"/>
                <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <h3 class="feature-title">Accès API RESTful</h3>
            <p class="feature-desc">
              Intégrez facilement les données TEDI dans vos applications grâce à notre
              API REST complète et notre documentation exhaustive.
            </p>
            <div class="feature-pattern"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section" aria-label="Appel à l'action">
      <div class="cta-pattern"></div>
      <div class="cta-content">
        <h2 class="cta-title">Prêt à exploiter le potentiel des données africaines ?</h2>
        <p class="cta-subtitle">
          Rejoignez les chercheurs, analystes et décideurs qui utilisent TEDI pour des insights actionnables
        </p>
        <div class="cta-actions">
          <router-link to="/login" class="btn-cta-primary">
            Commencer gratuitement
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor">
              <path d="M4 10h12m0 0l-4-4m4 4l-4 4" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </router-link>
          <router-link to="/documentation" class="btn-cta-secondary">
            Voir la documentation
          </router-link>
        </div>
      </div>
    </section>

    <!-- Footer Component -->
    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import api from '@/services/api'
import Footer from '@/components/Footer.vue'

// Lazy load Leaflet only when needed
let L = null

// State
const map = ref(null)
const communes = ref([])
const selectedCommune = ref(null)
const markers = ref([])
const communeStats = ref(null)
const loadingStats = ref(false)
const mapLoading = ref(true)

const overview = ref({
  communes: 0,
  dataSources: 4,
  dataPoints: 0,
  activeUsers: 0,
})

// Methods
const formatNumber = (value) => {
  if (!value) return '0'
  return new Intl.NumberFormat('en-US').format(value)
}

const loadPlatformStats = async () => {
  try {
    const response = await api.public.getStats()
    overview.value = {
      communes: response.data.communes,
      dataSources: response.data.data_sources,
      dataPoints: response.data.data_points,
      activeUsers: response.data.active_users,
    }
  } catch (error) {
    console.error('Failed to load platform stats:', error)
    // Keep default values if loading fails
  }
}

// Dynamically load Leaflet for better performance
const loadLeaflet = async () => {
  if (L) return L
  const leaflet = await import('leaflet')
  await import('leaflet/dist/leaflet.css')
  L = leaflet.default
  return L
}

const initMap = async () => {
  try {
    // Load Leaflet dynamically
    await loadLeaflet()
    mapLoading.value = false
    
    await nextTick()
    
    // Create map centered on Benin
    map.value = L.map('landing-map').setView([9.30769, 2.315834], 7)

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(map.value)

    // Fix Leaflet marker icons
    delete L.Icon.Default.prototype._getIconUrl
    L.Icon.Default.mergeOptions({
      iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
      iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
    })
  } catch (error) {
    console.error('Failed to load map:', error)
    mapLoading.value = false
  }
}

const loadCommunes = async () => {
  try {
    const response = await api.public.getCommunes()
    communes.value = response.data.data

    // Add markers for communes with coordinates
    communes.value.forEach(commune => {
      if (commune.center_lat && commune.center_lon) {
        addCommuneMarker(commune)
      }
    })

    // Adjust map bounds
    if (markers.value.length > 0) {
      const bounds = L.featureGroup(markers.value).getBounds()
      map.value.fitBounds(bounds, { padding: [50, 50] })
    }
  } catch (error) {
    console.error('Failed to load communes:', error)
  }
}

const addCommuneMarker = (commune) => {
  const icon = L.divIcon({
    className: 'custom-marker',
    html: `<div class="marker-pin">
      <div class="marker-inner">${commune.name.charAt(0)}</div>
    </div>`,
    iconSize: [40, 40],
    iconAnchor: [20, 40],
  })

  const marker = L.marker([commune.center_lat, commune.center_lon], { icon })
    .addTo(map.value)
    .bindPopup(`
      <div class="marker-popup">
        <h4>${commune.name}</h4>
        <p>${commune.region?.name || 'Unknown region'}</p>
        <span class="popup-cta">Click to view details →</span>
      </div>
    `)
    .on('click', async () => {
      selectedCommune.value = commune
      await loadCommuneStats(commune.id)
    })

  markers.value.push(marker)
}

const loadCommuneStats = async (communeId) => {
  loadingStats.value = true
  communeStats.value = null

  try {
    const response = await api.public.getCommuneSummary(communeId)
    const data = response.data

    communeStats.value = {
      agriculture: {
        count: data.statistics.agriculture,
        topCrops: data.top_crops
      },
      employment: {
        count: data.statistics.employment
      },
      business: {
        count: data.statistics.business
      },
      realestate: {
        count: data.statistics.real_estate
      },
      total: data.statistics.total
    }
  } catch (error) {
    console.error('Failed to load commune stats:', error)
  } finally {
    loadingStats.value = false
  }
}

// Lifecycle
onMounted(async () => {
  // Load stats first (fast), then map (lazy loaded)
  loadPlatformStats()
  await initMap()
  await loadCommunes()
})

onBeforeUnmount(() => {
  if (map.value) {
    map.value.remove()
  }
})
</script>

<style scoped>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Clash+Display:wght@600;700&family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap');

/* CSS Variables - Modern Professional Palette */
.landing-page {
  --color-primary: #0066FF;
  --color-secondary: #00C896;
  --color-accent: #FF6B35;
  --color-purple: #7C3AED;
  --color-dark: #0F172A;
  --color-light: #F8FAFC;
  --color-gray: #64748B;

  --font-display: 'Clash Display', sans-serif;
  --font-body: 'DM Sans', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  --shadow-sm: 0 2px 8px rgba(0, 102, 255, 0.08);
  --shadow-md: 0 4px 16px rgba(0, 102, 255, 0.12);
  --shadow-lg: 0 8px 32px rgba(0, 102, 255, 0.16);
  --shadow-xl: 0 16px 48px rgba(0, 102, 255, 0.2);
}

.landing-page {
  min-height: 100vh;
  background: #F8FAFC !important;
  font-family: var(--font-body);
  color: var(--color-dark);
  overflow-x: hidden;
}

/* ==================== HERO SECTION ==================== */
.hero-section {
  position: relative;
  min-height: 75vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  overflow: hidden;
  background: #0066 !important;
}

.hero-pattern {
  position: absolute;
  inset: 0;
  opacity: 0.08;
  background-image:
    radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.15) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(0, 200, 150, 0.15) 0%, transparent 50%),
    radial-gradient(circle at 40% 20%, rgba(255, 107, 53, 0.1) 0%, transparent 40%);
  animation: patternPulse 8s ease-in-out infinite;
}

@keyframes patternPulse {
  0%, 100% {
    opacity: 0.08;
    transform: scale(1);
  }
  50% {
    opacity: 0.12;
    transform: scale(1.05);
  }
}

.hero-gradient {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse at top left, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(ellipse at bottom right, rgba(0, 200, 150, 0.15) 0%, transparent 60%);
  animation: gradientFloat 15s ease-in-out infinite alternate;
}

@keyframes gradientFloat {
  0% {
    transform: translate(0, 0) rotate(0deg);
  }
  100% {
    transform: translate(20px, -20px) rotate(5deg);
  }
}

.hero-shapes {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.shape {
  position: absolute;
  border: 2px solid rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(2px);
}

.shape-1 {
  width: 400px;
  height: 400px;
  top: -10%;
  right: -5%;
  border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%;
  background: radial-gradient(circle, rgba(0, 200, 150, 0.05) 0%, transparent 70%);
  animation: float1 20s ease-in-out infinite;
}

.shape-2 {
  width: 250px;
  height: 250px;
  bottom: 10%;
  left: -5%;
  clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
  background: radial-gradient(circle, rgba(255, 107, 53, 0.05) 0%, transparent 70%);
  animation: float2 18s ease-in-out infinite reverse;
}

.shape-3 {
  width: 180px;
  height: 180px;
  top: 50%;
  right: 15%;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.05) 0%, transparent 70%);
  animation: float3 22s ease-in-out infinite;
}

@keyframes float1 {
  0%, 100% {
    transform: translate(0, 0) rotate(0deg) scale(1);
    opacity: 0.6;
  }
  33% {
    transform: translate(30px, -30px) rotate(10deg) scale(1.1);
    opacity: 0.8;
  }
  66% {
    transform: translate(-20px, -50px) rotate(-10deg) scale(0.9);
    opacity: 0.7;
  }
}

@keyframes float2 {
  0%, 100% {
    transform: translate(0, 0) rotate(0deg);
    opacity: 0.5;
  }
  50% {
    transform: translate(-30px, 30px) rotate(45deg);
    opacity: 0.8;
  }
}

@keyframes float3 {
  0%, 100% {
    transform: translate(0, 0) scale(1);
    opacity: 0.4;
  }
  25% {
    transform: translate(20px, -30px) scale(1.2);
    opacity: 0.7;
  }
  50% {
    transform: translate(-10px, -40px) scale(0.8);
    opacity: 0.5;
  }
  75% {
    transform: translate(-30px, 20px) scale(1.1);
    opacity: 0.6;
  }
}

.hero-content {
  position: relative;
  z-index: 10;
  max-width: 900px;
  text-align: center;
  color: white;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1.5rem;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 50px;
  font-size: 0.875rem;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  margin-bottom: 2rem;
  animation: fadeInUp 0.8s ease-out, badgeGlow 3s ease-in-out infinite;
}

@keyframes badgeGlow {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.2);
  }
  50% {
    box-shadow: 0 0 20px 5px rgba(0, 200, 150, 0.3);
  }
}

.badge-dot {
  width: 8px;
  height: 8px;
  background: var(--color-accent);
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.2); }
}

.hero-title {
  font-family: var(--font-display);
  font-size: clamp(3rem, 8vw, 6rem);
  font-weight: 700;
  line-height: 1.1;
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.title-line {
  display: block;
  animation: fadeInUp 0.8s ease-out backwards;
  color: white;
}

.title-highlight {
  background: #0066FF;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: clamp(1.125rem, 2vw, 1.375rem);
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.95);
  margin-bottom: 3rem;
  max-width: 700px;
  margin-left: auto;
  margin-right: auto;
  animation: fadeInUp 0.8s ease-out backwards;
}

.hero-cta {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  animation: fadeInUp 0.8s ease-out backwards;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.hero-cta .btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 2rem;
  background: white !important;
  color: var(--color-purple) !important;
  font-weight: 600;
  font-size: 1.125rem;
  border-radius: 12px;
  text-decoration: none;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-lg);
}

.hero-cta .btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-xl);
}

.hero-cta .btn-primary svg {
  transition: transform 0.3s ease;
}

.hero-cta .btn-primary:hover svg {
  transform: translateX(4px);
}

.hero-cta .btn-secondary {
  display: inline-flex;
  align-items: center;
  padding: 1rem 2rem;
  background: rgba(255, 255, 255, 0.1) !important;
  backdrop-filter: blur(10px);
  color: white !important;
  font-weight: 600;
  font-size: 1.125rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  text-decoration: none;
  transition: all 0.3s ease;
}

.hero-cta .btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2) !important;
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
}

/* ==================== STATS SECTION ==================== */
.stats-section {
  position: relative;
  padding: 4rem 2rem;
  margin-top: -6rem;
  z-index: 10;
}

.stats-container {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.stat-card {
  position: relative;
  background: white;
  padding: 2rem;
  border-radius: 20px;
  box-shadow: var(--shadow-md);
  display: flex;
  align-items: flex-start;
  gap: 1.5rem;
  overflow: hidden;
  transition: all 0.3s ease;
  animation: fadeInUp 0.6s ease-out backwards;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-xl);
}

.stat-pattern {
  position: absolute;
  right: -20px;
  bottom: -20px;
  width: 100px;
  height: 100px;
  opacity: 0.05;
}

.pattern-1 {
  background: repeating-linear-gradient(45deg, var(--color-accent), var(--color-accent) 10px, transparent 10px, transparent 20px);
}

.pattern-2 {
  background: repeating-linear-gradient(-45deg, var(--color-secondary), var(--color-secondary) 10px, transparent 10px, transparent 20px);
}

.pattern-3 {
  background: radial-gradient(circle, var(--color-primary) 2px, transparent 2px);
  background-size: 20px 20px;
}

.pattern-4 {
  background: conic-gradient(from 45deg, var(--color-purple) 0deg, transparent 90deg, transparent 270deg, var(--color-purple) 360deg);
}

.stat-icon {
  flex-shrink: 0;
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  position: relative;
}

.stat-icon::before {
  content: '';
  position: absolute;
  inset: -4px;
  border-radius: 18px;
  padding: 4px;
  background: linear-gradient(135deg, currentColor, transparent);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0.3;
}

.stat-icon-1 {
  background: linear-gradient(135deg, rgba(0, 102, 255, 0.1), rgba(0, 102, 255, 0.05));
  color: var(--color-primary);
}

.stat-icon-2 {
  background: linear-gradient(135deg, rgba(0, 200, 150, 0.1), rgba(0, 200, 150, 0.05));
  color: var(--color-secondary);
}

.stat-icon-3 {
  background: linear-gradient(135deg, rgba(255, 107, 53, 0.1), rgba(255, 107, 53, 0.05));
  color: var(--color-accent);
}

.stat-icon-4 {
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.1), rgba(124, 58, 237, 0.05));
  color: var(--color-purple);
}

.stat-content {
  flex: 1;
  position: relative;
  z-index: 1;
}

.stat-value {
  font-family: var(--font-mono);
  font-size: 2.5rem;
  font-weight: 600;
  line-height: 1;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-gray);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* ==================== MAP SECTION ==================== */
.map-section {
  position: relative;
  padding: 6rem 2rem;
  background: white;
  z-index: 50;
  isolation: isolate;
}

.section-header {
  max-width: 800px;
  margin: 0 auto 4rem;
  text-align: center;
}

.section-badge {
  display: inline-block;
  padding: 0.5rem 1.5rem;
  background: linear-gradient(135deg, rgba(0, 102, 255, 0.1), rgba(0, 200, 150, 0.1));
  color: var(--color-primary);
  font-size: 0.875rem;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  border-radius: 50px;
  margin-bottom: 1.5rem;
}

.section-title {
  font-family: var(--font-display);
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 1rem;
  color: var(--color-dark);
}

.title-accent {
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.section-subtitle {
  font-size: 1.25rem;
  line-height: 1.6;
  color: var(--color-gray);
}

.map-layout {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 2rem;
}

@media (max-width: 1024px) {
  .map-layout {
    grid-template-columns: 1fr;
  }
}

.map-wrapper {
  position: relative;
}

.map-container {
  position: relative;
  background: white;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  height: 600px;
}

#landing-map {
  width: 100%;
  height: 100%;
  z-index: 1;
  position: relative;
}

.map-overlay {
  position: absolute;
  top: 1.5rem;
  left: 1.5rem;
  z-index: 1000;
}

.map-legend {
  background: white;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  box-shadow: var(--shadow-md);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-dark);
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-active {
  background: var(--color-secondary);
  box-shadow: 0 0 0 3px rgba(0, 200, 150, 0.2);
}

.legend-inactive {
  background: var(--color-gray);
  opacity: 0.4;
}

/* Custom Map Markers */
:deep(.marker-pin) {
  position: relative;
  width: 40px;
  height: 40px;
}

:deep(.marker-inner) {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--color-secondary), var(--color-primary));
  border: 3px solid white;
  border-radius: 50% 50% 50% 0;
  transform-origin: center;
  animation: markerDrop 0.6s ease-out;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.875rem;
  color: white;
  cursor: pointer;
  transition: transform 0.3s ease;
  box-shadow: var(--shadow-md);
  rotate: -45deg;
}

:deep(.marker-inner):hover {
  transform: scale(1.15);
}

@keyframes markerDrop {
  0% {
    transform: translateY(-100px) translateX(-50%);
    opacity: 0;
  }
  60% {
    transform: translateY(5px) translateX(-50%);
  }
  100% {
    transform: translateY(0) translateX(-50%);
    opacity: 1;
  }
}

:deep(.marker-popup) {
  padding: 0.75rem;
  min-width: 180px;
}

:deep(.marker-popup h4) {
  font-weight: 700;
  font-size: 1.125rem;
  margin-bottom: 0.25rem;
  color: var(--color-dark);
}

:deep(.marker-popup p) {
  font-size: 0.875rem;
  color: var(--color-gray);
  margin-bottom: 0.5rem;
}

:deep(.popup-cta) {
  display: inline-block;
  color: var(--color-secondary);
  font-weight: 600;
  font-size: 0.875rem;
}

/* ==================== SIDEBAR ==================== */
.sidebar-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.commune-panel,
.prompt-panel {
  background: white;
  border-radius: 24px;
  box-shadow: var(--shadow-lg);
  padding: 2rem;
  animation: slideInRight 0.4s ease-out;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid var(--color-light);
}

.commune-name {
  font-family: var(--font-display);
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--color-dark);
  margin-bottom: 0.25rem;
}

.commune-region {
  font-size: 0.875rem;
  color: var(--color-gray);
  font-weight: 500;
}

.btn-close {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-light);
  border: none;
  border-radius: 10px;
  color: var(--color-gray);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-close:hover {
  background: var(--color-accent);
  color: white;
  transform: rotate(90deg);
}

.commune-info {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: var(--color-light);
  border-radius: 10px;
}

.info-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-gray);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-family: var(--font-mono);
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-dark);
}

.info-value.coord {
  font-size: 0.875rem;
}

.loading-state {
  text-align: center;
  padding: 3rem 0;
}

.spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 1rem;
  border: 3px solid var(--color-light);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  color: var(--color-gray);
  font-size: 0.875rem;
}

.data-stats {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.stats-title {
  font-weight: 700;
  font-size: 1.125rem;
  color: var(--color-dark);
  margin-bottom: 0.5rem;
}

.data-item {
  background: var(--color-light);
  padding: 1rem;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.data-item:hover {
  background: linear-gradient(135deg, rgba(0, 102, 255, 0.05), rgba(0, 200, 150, 0.05));
  transform: translateX(4px);
}

.data-header {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.data-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  flex-shrink: 0;
}

.data-icon-agri {
  background: linear-gradient(135deg, rgba(0, 200, 150, 0.1), rgba(0, 200, 150, 0.05));
  color: var(--color-secondary);
}

.data-icon-employ {
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.1), rgba(124, 58, 237, 0.05));
  color: var(--color-purple);
}

.data-icon-business {
  background: linear-gradient(135deg, rgba(255, 107, 53, 0.1), rgba(255, 107, 53, 0.05));
  color: var(--color-accent);
}

.data-icon-realestate {
  background: linear-gradient(135deg, rgba(0, 102, 255, 0.1), rgba(0, 102, 255, 0.05));
  color: var(--color-primary);
}

.data-info {
  flex: 1;
}

.data-name {
  font-weight: 600;
  font-size: 0.9375rem;
  color: var(--color-dark);
  margin-bottom: 0.125rem;
}

.data-desc {
  font-size: 0.75rem;
  color: var(--color-gray);
}

.data-count {
  font-family: var(--font-mono);
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-secondary);
}

.crop-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.75rem;
  padding-left: 3.5rem;
}

.crop-tag {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: white;
  color: var(--color-secondary);
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 50px;
  border: 1px solid var(--color-secondary);
}

.total-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, var(--color-primary), var(--color-purple));
  border-radius: 12px;
  margin-top: 0.5rem;
  color: white;
}

.total-label {
  font-weight: 600;
  font-size: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.total-value {
  font-family: var(--font-mono);
  font-size: 2rem;
  font-weight: 700;
}

.btn-view-all {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  padding: 1rem;
  margin-top: 1rem;
  background: var(--color-primary);
  color: white;
  font-weight: 600;
  border-radius: 12px;
  text-decoration: none;
  transition: all 0.3s ease;
}

.btn-view-all:hover {
  background: var(--color-accent);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.btn-view-all svg {
  transition: transform 0.3s ease;
}

.btn-view-all:hover svg {
  transform: translateX(4px);
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--color-gray);
}

.empty-state svg {
  margin-bottom: 1rem;
  opacity: 0.3;
}

.prompt-panel {
  text-align: center;
  padding: 3rem 2rem;
}

.prompt-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(0, 200, 150, 0.1), rgba(0, 102, 255, 0.1));
  border-radius: 20px;
  color: var(--color-secondary);
}

.prompt-title {
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-dark);
  margin-bottom: 0.75rem;
}

.prompt-text {
  color: var(--color-gray);
  line-height: 1.6;
}

/* ==================== FEATURES SECTION ==================== */
.features-section {
  position: relative;
  padding: 6rem 2rem;
  background: var(--color-light);
  overflow: hidden;
  z-index: 100;
}

.features-pattern {
  position: absolute;
  inset: 0;
  opacity: 0.03;
  background-image:
    radial-gradient(circle, var(--color-accent) 1px, transparent 1px),
    radial-gradient(circle, var(--color-secondary) 1px, transparent 1px);
  background-size: 40px 40px;
  background-position: 0 0, 20px 20px;
}

.features-content {
  position: relative;
  z-index: 1;
  max-width: 1200px;
  margin: 0 auto;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 2rem;
  margin-top: 4rem;
}

.feature-card {
  position: relative;
  background: white;
  padding: 2.5rem;
  border-radius: 24px;
  box-shadow: var(--shadow-md);
  transition: all 0.4s ease;
  overflow: hidden;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-xl);
}

.feature-card:hover .feature-pattern {
  opacity: 0.15;
  transform: scale(1.1) rotate(10deg);
}

.feature-pattern {
  position: absolute;
  bottom: -20px;
  right: -20px;
  width: 150px;
  height: 150px;
  background: currentColor;
  opacity: 0.05;
  clip-path: polygon(30% 0%, 100% 0%, 100% 70%, 70% 100%, 0% 100%, 0% 30%);
  transition: all 0.4s ease;
}

.feature-card:nth-child(1) .feature-pattern { color: var(--color-secondary); }
.feature-card:nth-child(2) .feature-pattern { color: var(--color-accent); }
.feature-card:nth-child(3) .feature-pattern { color: var(--color-primary); }

.feature-icon {
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 18px;
  margin-bottom: 1.5rem;
  position: relative;
  z-index: 1;
}

.feature-icon-1 {
  background: linear-gradient(135deg, rgba(0, 200, 150, 0.1), rgba(0, 200, 150, 0.05));
  color: var(--color-secondary);
}

.feature-icon-2 {
  background: linear-gradient(135deg, rgba(255, 107, 53, 0.1), rgba(255, 107, 53, 0.05));
  color: var(--color-accent);
}

.feature-icon-3 {
  background: linear-gradient(135deg, rgba(0, 102, 255, 0.1), rgba(0, 102, 255, 0.05));
  color: var(--color-primary);
}

.feature-title {
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-dark);
  margin-bottom: 1rem;
  position: relative;
  z-index: 1;
}

.feature-desc {
  font-size: 1rem;
  line-height: 1.7;
  color: var(--color-gray);
  position: relative;
  z-index: 1;
}

/* ==================== CTA SECTION ==================== */
.cta-section {
  position: relative;
  padding: 6rem 2rem;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-purple) 100%);
  overflow: hidden;
}

.cta-pattern {
  position: absolute;
  inset: 0;
  opacity: 0.1;
  background:
    repeating-linear-gradient(90deg, transparent, transparent 20px, white 20px, white 21px),
    repeating-linear-gradient(0deg, transparent, transparent 20px, white 20px, white 21px);
}

.cta-content {
  position: relative;
  z-index: 1;
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
  color: white;
}

.cta-title {
  font-family: var(--font-display);
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 1.5rem;
}

.cta-subtitle {
  font-size: 1.25rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 3rem;
}

.cta-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-cta-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.25rem 2.5rem;
  background: white;
  color: var(--color-purple);
  font-weight: 700;
  font-size: 1.125rem;
  border-radius: 12px;
  text-decoration: none;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-lg);
}

.btn-cta-primary:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: var(--shadow-xl);
}

.btn-cta-primary svg {
  transition: transform 0.3s ease;
}

.btn-cta-primary:hover svg {
  transform: translateX(4px);
}

.btn-cta-secondary {
  display: inline-flex;
  align-items: center;
  padding: 1.25rem 2.5rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  color: white;
  font-weight: 600;
  font-size: 1.125rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  text-decoration: none;
  transition: all 0.3s ease;
}

.btn-cta-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
}

/* ==================== RESPONSIVE ==================== */
@media (max-width: 768px) {
  .hero-section {
    min-height: 90vh;
    padding: 1rem;
  }

  .stats-container {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }

  .stat-card {
    padding: 1.5rem;
  }

  .stat-value {
    font-size: 2rem;
  }

  .map-layout {
    grid-template-columns: 1fr;
  }

  .map-container {
    height: 400px;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .hero-cta,
  .cta-actions {
    flex-direction: column;
    width: 100%;
  }

  .btn-primary,
  .btn-secondary,
  .btn-cta-primary,
  .btn-cta-secondary {
    width: 100%;
    justify-content: center;
  }
}

/* ==================== FOOTER SECTION ==================== */
.footer-section {
  background: var(--color-dark);
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
  background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.logo-text {
  font-family: var(--font-display);
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
  font-family: var(--font-mono);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-secondary);
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
  font-family: var(--font-display);
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
  color: var(--color-secondary);
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

.footer-data-sources {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .footer-data-sources {
    justify-content: center;
  }
}

.sources-label {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.4);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.source-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 50px;
  font-size: 0.75rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.6);
  transition: all 0.2s ease;
}

.source-badge:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: var(--color-secondary);
  color: var(--color-secondary);
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
  color: var(--color-secondary);
}

/* Screen Reader Only - SEO Content visible to search engines but hidden from visual display */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
</style>
