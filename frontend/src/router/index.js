import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { pageSeoConfig } from '@/composables/useSeo'

// Helper function to update SEO meta tags
function updateSeoMeta(routeName, path) {
  const config = pageSeoConfig[routeName]
  if (!config) return
  
  // Update title
  const titleTemplate = '%s | TEDI Bénin - Données Économiques'
  document.title = config.title ? titleTemplate.replace('%s', config.title) : 'TEDI Bénin - Données Économiques & Territoriales'
  
  // Update meta description
  const descMeta = document.querySelector('meta[name="description"]')
  if (descMeta) descMeta.setAttribute('content', config.description || '')
  
  // Update meta keywords
  let keywordsMeta = document.querySelector('meta[name="keywords"]')
  if (keywordsMeta && config.keywords) {
    keywordsMeta.setAttribute('content', config.keywords)
  }
  
  // Update canonical URL
  const canonicalLink = document.querySelector('link[rel="canonical"]')
  if (canonicalLink) {
    canonicalLink.setAttribute('href', `https://tedi.bj${path}`)
  }
  
  // Update Open Graph
  const ogTitle = document.querySelector('meta[property="og:title"]')
  const ogDesc = document.querySelector('meta[property="og:description"]')
  const ogUrl = document.querySelector('meta[property="og:url"]')
  if (ogTitle) ogTitle.setAttribute('content', config.title || '')
  if (ogDesc) ogDesc.setAttribute('content', config.description || '')
  if (ogUrl) ogUrl.setAttribute('href', `https://tedi.bj${path}`)
  
  // Update Twitter
  const twTitle = document.querySelector('meta[name="twitter:title"]')
  const twDesc = document.querySelector('meta[name="twitter:description"]')
  if (twTitle) twTitle.setAttribute('content', config.title || '')
  if (twDesc) twDesc.setAttribute('content', config.description || '')
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  // Scroll to top on navigation
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  },
  routes: [
    {
      path: '/',
      name: 'landing',
      component: () => import('@/views/LandingView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/views/MultiSectorDashboard.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/agriculture',
      name: 'agriculture',
      component: () => import('@/views/AgricultureView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/realestate',
      name: 'realestate',
      component: () => import('@/views/RealEstateView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/employment',
      name: 'employment',
      component: () => import('@/views/EmploymentView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/business',
      name: 'business',
      component: () => import('@/views/BusinessView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/map',
      name: 'map',
      component: () => import('@/views/MapView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/api-keys',
      name: 'api-keys',
      component: () => import('@/views/ApiKeysView.vue'),
      meta: { requiresAuth: true }
    },
    // Public pages
    {
      path: '/documentation',
      name: 'documentation',
      component: () => import('@/views/DocumentationView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/api-reference',
      name: 'api-reference',
      component: () => import('@/views/ApiReferenceView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/data-quality',
      name: 'data-quality',
      component: () => import('@/views/DataQualityView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/data-sources',
      name: 'data-sources',
      component: () => import('@/views/DataSourcesView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/support',
      name: 'support',
      component: () => import('@/views/SupportView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/privacy',
      name: 'privacy',
      component: () => import('@/views/PrivacyView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/terms',
      name: 'terms',
      component: () => import('@/views/TermsView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/license',
      name: 'license',
      component: () => import('@/views/LicenseView.vue'),
      meta: { requiresAuth: false }
    },
    // Admin panel (has its own authentication)
    {
      path: '/admin',
      name: 'admin',
      component: () => import('@/views/AdminView.vue'),
      meta: { requiresAuth: false }
    }
  ]
})

// Navigation guard
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login' })
  } else if (to.name === 'login' && authStore.isAuthenticated) {
    next({ name: 'dashboard' })
  } else {
    next()
  }
})

// SEO: Update meta tags after each navigation
router.afterEach((to) => {
  const routeName = to.name?.toString() || 'landing'
  updateSeoMeta(routeName, to.path)
})

export default router
