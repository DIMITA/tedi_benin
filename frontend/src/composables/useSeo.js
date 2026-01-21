/**
 * SEO Composable for Vue 3
 * Manages dynamic meta tags for each page
 */

import { watch, onMounted, onUnmounted } from 'vue'

// Default SEO configuration
const defaultSeo = {
  siteName: 'TEDI Bénin',
  titleTemplate: '%s | TEDI Bénin - Données Économiques',
  defaultTitle: 'TEDI Bénin - Données Économiques & Territoriales du Bénin',
  defaultDescription: 'Plateforme de données économiques et territoriales du Bénin. Accédez aux statistiques agriculture, immobilier, emploi et business de toutes les communes béninoises.',
  defaultImage: 'https://tedi.bj/og-image.jpg',
  baseUrl: 'https://tedi.bj',
  twitterHandle: '@tedibenin',
}

// Page-specific SEO configurations
export const pageSeoConfig = {
  landing: {
    title: 'Accueil',
    description: 'TEDI Bénin - La plateforme de référence pour les données économiques et territoriales du Bénin. Agriculture, immobilier, emploi, business.',
    keywords: 'data benin, données bénin, économie bénin, statistiques bénin, open data benin',
  },
  agriculture: {
    title: 'Agriculture Bénin - Données & Statistiques Agricoles',
    description: 'Données agricoles du Bénin : production, rendements, prix des cultures (maïs, riz, manioc, igname, coton). Statistiques par commune de 2010 à 2024.',
    keywords: 'agriculture benin, production agricole benin, maïs benin, riz benin, manioc benin, rendement agricole benin, prix cultures benin',
  },
  realestate: {
    title: 'Immobilier Bénin - Prix & Tendances du Marché',
    description: 'Données immobilières du Bénin : prix au m², tendances du marché, transactions par commune. Résidentiel, commercial, agricole, industriel.',
    keywords: 'immobilier benin, prix immobilier benin, prix m2 cotonou, achat maison benin, terrain benin, investissement immobilier benin',
  },
  employment: {
    title: 'Emploi Bénin - Statistiques & Marché du Travail',
    description: 'Données emploi du Bénin : taux de chômage, salaires, secteurs d\'activité. Statistiques par commune et catégorie professionnelle.',
    keywords: 'emploi benin, travail benin, salaire benin, chômage benin, offre emploi benin, marché travail benin',
  },
  business: {
    title: 'Business Bénin - Entreprises & Opportunités',
    description: 'Données business du Bénin : nombre d\'entreprises, densité commerciale, opportunités d\'investissement par secteur et commune.',
    keywords: 'business benin, entreprise benin, investir benin, commerce benin, création entreprise benin, opportunités benin',
  },
  map: {
    title: 'Carte Interactive - Données Géographiques du Bénin',
    description: 'Visualisez les données économiques du Bénin sur une carte interactive. Explorez les communes et leurs indicateurs économiques.',
    keywords: 'carte benin, communes benin, géographie benin, visualisation données benin',
  },
  dashboard: {
    title: 'Tableau de Bord - Vue d\'Ensemble Économique',
    description: 'Dashboard multi-secteur : visualisez les tendances économiques du Bénin en temps réel. Agriculture, immobilier, emploi, business.',
    keywords: 'dashboard benin, tableau bord économique, statistiques benin, indicateurs benin',
  },
  login: {
    title: 'Connexion - Accédez à vos Données',
    description: 'Connectez-vous à TEDI Bénin pour accéder aux données économiques complètes et à l\'API.',
    keywords: 'connexion tedi, api données benin, accès données benin',
  },
}

/**
 * Update document title
 */
function updateTitle(title) {
  if (title) {
    document.title = defaultSeo.titleTemplate.replace('%s', title)
  } else {
    document.title = defaultSeo.defaultTitle
  }
}

/**
 * Update or create a meta tag
 */
function updateMeta(name, content, isProperty = false) {
  const attribute = isProperty ? 'property' : 'name'
  let element = document.querySelector(`meta[${attribute}="${name}"]`)
  
  if (!element) {
    element = document.createElement('meta')
    element.setAttribute(attribute, name)
    document.head.appendChild(element)
  }
  
  element.setAttribute('content', content)
}

/**
 * Update canonical URL
 */
function updateCanonical(path) {
  let link = document.querySelector('link[rel="canonical"]')
  
  if (!link) {
    link = document.createElement('link')
    link.setAttribute('rel', 'canonical')
    document.head.appendChild(link)
  }
  
  link.setAttribute('href', `${defaultSeo.baseUrl}${path}`)
}

/**
 * Main SEO composable
 */
export function useSeo(options = {}) {
  const setMeta = (config) => {
    const {
      title = defaultSeo.defaultTitle,
      description = defaultSeo.defaultDescription,
      keywords = '',
      image = defaultSeo.defaultImage,
      path = '/',
      type = 'website',
    } = config

    // Title
    updateTitle(title)

    // Basic meta tags
    updateMeta('description', description)
    if (keywords) {
      updateMeta('keywords', keywords)
    }

    // Canonical URL
    updateCanonical(path)

    // Open Graph
    updateMeta('og:title', title, true)
    updateMeta('og:description', description, true)
    updateMeta('og:image', image, true)
    updateMeta('og:url', `${defaultSeo.baseUrl}${path}`, true)
    updateMeta('og:type', type, true)
    updateMeta('og:site_name', defaultSeo.siteName, true)
    updateMeta('og:locale', 'fr_FR', true)

    // Twitter Card
    updateMeta('twitter:card', 'summary_large_image')
    updateMeta('twitter:title', title)
    updateMeta('twitter:description', description)
    updateMeta('twitter:image', image)
    updateMeta('twitter:site', defaultSeo.twitterHandle)
  }

  // Set initial meta if options provided
  if (Object.keys(options).length > 0) {
    onMounted(() => {
      setMeta(options)
    })
  }

  return {
    setMeta,
    pageSeoConfig,
    defaultSeo,
  }
}

/**
 * Hook for route-based SEO
 * Use in router/index.js or App.vue
 */
export function useRouteSeo(router) {
  router.afterEach((to) => {
    const routeName = to.name?.toString() || 'landing'
    const config = pageSeoConfig[routeName]
    
    if (config) {
      const { setMeta } = useSeo()
      setMeta({
        ...config,
        path: to.path,
      })
    }
  })
}

export default useSeo
