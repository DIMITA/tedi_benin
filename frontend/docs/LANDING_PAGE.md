# Landing Page Documentation - TEDI Platform

## Vue d'Ensemble

La Landing Page est la page d'accueil publique de la plateforme TEDI. Elle présente le service de manière attractive et permet aux visiteurs d'explorer les données disponibles via une carte interactive avant même de créer un compte.

**Route**: `/` (page d'accueil)
**Authentification**: Non requise (page publique)

---

## Sections de la Page

### 1. Hero Section (En-tête)

**Contenu**:
- Titre principal: "TEDI Platform"
- Sous-titre: "Territorial & Economic Data Intelligence for Africa"
- Description du service
- 2 Call-to-Action (CTA):
  - "Commencer Gratuitement" → `/login`
  - "Explorer les Données" → Scroll vers la carte

**Design**:
- Dégradé de couleur: vert TEDI → bleu TEDI
- Texte blanc pour contraste maximal
- Animations au chargement (fade-in)

### 2. Stats Overview Cards

Quatre cartes affichant les statistiques clés de la plateforme:

#### Carte 1: Communes
- **Icône**: Pin de localisation
- **Valeur**: Nombre total de communes dans la base
- **Source**: Compté depuis `/api/v1/agriculture/communes`
- **Couleur**: Vert TEDI (primary)

#### Carte 2: Sources de Données
- **Icône**: Maison/Database
- **Valeur**: 4 sources (FAOSTAT, World Bank, ILOSTAT, OSM)
- **Couleur**: Vert clair

#### Carte 3: Points de Données
- **Icône**: Graphique à barres
- **Valeur**: Total calculé (communes × crops × années)
- **Couleur**: Bleu

#### Carte 4: Disponibilité
- **Icône**: Horloge
- **Valeur**: "24/7"
- **Message**: Disponibilité continue de l'API
- **Couleur**: Amber (accent)

**Position**: Cartes positionnées juste en dessous du hero avec un effet de "sortie" (negative margin)

### 3. Carte Interactive avec Statistiques

#### Carte Leaflet (2/3 de la largeur sur desktop)

**Configuration**:
- **Centre**: Bénin (9.30769°N, 2.315834°E)
- **Zoom initial**: 7
- **Tiles**: OpenStreetMap
- **Marqueurs**: Communes avec données

**Fonctionnalités**:
- Marqueurs personnalisés avec première lettre de la commune
- Couleur verte TEDI
- Popup au survol avec nom et région
- Clic sur marqueur → Charge les statistiques détaillées

#### Panneau de Statistiques (1/3 de la largeur)

**État par défaut** (aucune commune sélectionnée):
- Icône de pin
- Message: "Sélectionnez une Commune"
- Instruction: "Cliquez sur un marqueur..."

**État avec commune sélectionnée**:

##### Informations de Base
- Nom de la commune (titre)
- Région (sous-titre)
- Bouton fermer (×)

##### Statistiques Démographiques
- **Population**: Formatée avec séparateurs de milliers
- **Superficie**: En km²
- **Coordonnées**: Lat, Lon (4 décimales)

##### Données Disponibles par Vertical

###### Agriculture
- **Icône**: Champ/Ferme
- **Compteur**: Nombre de données agricoles
- **Détail**: Top 3 des cultures principales
- **Badges**: Noms des cultures en vert
- **Source API**: `/api/v1/agriculture/index?commune_id=X`

###### Emploi
- **Icône**: Groupe de personnes
- **Compteur**: Nombre de données d'emploi
- **Source API**: `/api/v1/employment/index?commune_id=X`

###### Business
- **Icône**: Immeuble de bureaux
- **Compteur**: Nombre de données business
- **Source API**: `/api/v1/business/index?commune_id=X`

###### Immobilier
- **Icône**: Maison
- **Compteur**: Nombre de données immobilières
- **Source API**: `/api/v1/realestate/index?commune_id=X`

##### Total des Données
- Somme de toutes les données
- Affiché en grand avec bordure supérieure

##### Action
- Bouton "Voir Toutes les Données"
- Navigation vers `/agriculture?commune_id=X`
- Gradient vert-bleu TEDI

**Chargement**:
- Spinner animé pendant le chargement des stats
- Message "Chargement des statistiques..."

**Aucune donnée**:
- Icône de document
- Message: "Aucune donnée disponible pour cette commune"

#### Légende de la Carte
- Cercle vert: Commune avec données
- Cercle gris: Commune sans données (future)

### 4. Features Section (Pourquoi TEDI)

Trois cartes présentant les avantages de la plateforme:

#### Données Fiables
- **Icône**: Checkmark dans cercle
- **Description**: Agrégation de sources officielles
- **Sources mentionnées**: FAOSTAT, Banque Mondiale, ILOSTAT, OpenStreetMap

#### Mise à Jour Automatique
- **Icône**: Flèches circulaires (refresh)
- **Description**: Actualisation toutes les 6 heures
- **Technologie**: Système d'ingestion automatisé

#### API REST Complète
- **Icône**: Code brackets
- **Description**: Intégration facile via API
- **Bénéfice**: Connexion directe aux applications

### 5. Call-to-Action Final

**Contenu**:
- Titre: "Prêt à Explorer les Données ?"
- Description: "Créez votre compte gratuitement..."
- Bouton: "Commencer Maintenant" → `/login`

**Design**:
- Fond: Gradient vert-bleu TEDI
- Texte blanc
- Bouton blanc avec texte vert

---

## Flux de Données

### Chargement Initial

```
1. Page Load
   ↓
2. initMap() - Initialise Leaflet
   ↓
3. loadCommunes() - GET /api/v1/agriculture/communes
   ↓
4. Pour chaque commune avec coordonnées:
   └→ addCommuneMarker(commune)
       └→ Crée marqueur Leaflet avec icône personnalisée
   ↓
5. map.fitBounds() - Ajuste vue pour voir tous les marqueurs
   ↓
6. Affiche overview stats (communes count, etc.)
```

### Clic sur Commune

```
1. User clicks marker
   ↓
2. selectedCommune.value = commune
   ↓
3. loadCommuneStats(commune.id)
   ↓
4. Promise.allSettled([
     api.agriculture.getIndex({ commune_id }),
     api.employment.getIndex({ commune_id }),
     api.business.getIndex({ commune_id }),
     api.realestate.getIndex({ commune_id })
   ])
   ↓
5. Process responses:
   - Count data per vertical
   - Extract top 3 crops
   - Calculate total
   ↓
6. Display in sidebar panel
   ↓
7. User can click "Voir Toutes les Données"
   └→ Navigate to /agriculture?commune_id=X
```

---

## Intégration avec le Backend

### Endpoints Utilisés

#### 1. Liste des Communes
```javascript
GET /api/v1/agriculture/communes

Response: [
  {
    "id": 1,
    "name": "Cotonou",
    "region": { "name": "Littoral" },
    "center_lat": 6.3654,
    "center_lon": 2.4183,
    "population": 679012,
    "area_km2": 79.0
  },
  ...
]
```

#### 2. Données Agricoles par Commune
```javascript
GET /api/v1/agriculture/index?commune_id=1

Response: [
  {
    "commune_id": 1,
    "commune_name": "Cotonou",
    "crop_id": 5,
    "crop_name": "Maïs",
    "year": 2023,
    "yield_kg_per_ha": 1500,
    ...
  },
  ...
]
```

#### 3. Données Emploi par Commune
```javascript
GET /api/v1/employment/index?commune_id=1

Response: [
  {
    "commune_id": 1,
    "job_category": "Agriculture",
    "year": 2023,
    "unemployment_rate": 8.5,
    ...
  },
  ...
]
```

#### 4. Données Business par Commune
```javascript
GET /api/v1/business/index?commune_id=1

Response: [
  {
    "commune_id": 1,
    "sector": "Services",
    "year": 2023,
    "business_count": 1250,
    ...
  },
  ...
]
```

#### 5. Données Immobilier par Commune
```javascript
GET /api/v1/realestate/index?commune_id=1

Response: [
  {
    "commune_id": 1,
    "property_type": "Résidentiel",
    "year": 2023,
    "avg_price_per_sqm": 85000,
    ...
  },
  ...
]
```

### Gestion des Erreurs

La landing page utilise `Promise.allSettled()` pour charger les stats, ce qui signifie:
- ✅ Si un endpoint échoue, les autres continuent
- ✅ Les compteurs affichent 0 pour les verticaux sans données
- ✅ Pas d'erreur visible à l'utilisateur
- ✅ Expérience dégradée gracieuse

---

## Design Responsive

### Desktop (lg+)
- **Hero**: Pleine largeur
- **Stats Cards**: Grille 4 colonnes
- **Carte/Sidebar**: 2/3 + 1/3 (côte à côte)
- **Features**: Grille 3 colonnes

### Tablet (md)
- **Stats Cards**: Grille 2 colonnes
- **Carte/Sidebar**: Empilés verticalement
- **Features**: Grille 2 colonnes

### Mobile (sm)
- **Stats Cards**: 1 colonne
- **Carte**: Hauteur réduite (400px)
- **Sidebar**: Pleine largeur
- **Features**: 1 colonne

---

## Performance

### Optimisations Implémentées

1. **Chargement Parallèle**:
   - `Promise.allSettled()` pour charger 4 endpoints simultanément
   - Pas de blocage si un endpoint est lent

2. **Lazy Loading**:
   - Stats de commune chargées uniquement au clic
   - Pas de chargement inutile des 77 communes

3. **Marqueurs Légers**:
   - Icônes DIV HTML (pas d'images)
   - CSS simple pour style
   - Rendu rapide

4. **Pas de Cache Agressif**:
   - Données fraîches à chaque visite
   - Reflète l'état actuel du système d'ingestion

### Considérations Futures

**Pour >100 communes**:
- Implémenter marker clustering (Leaflet.markercluster)
- Pagination des résultats
- Lazy loading des marqueurs (viewport-based)

**Pour données volumineuses**:
- Ajouter cache côté client (LocalStorage)
- Implementer service worker
- Pagination des stats dans le panneau

---

## Animations et Interactions

### Animations CSS

```css
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slide-in {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
```

**Appliquées à**:
- Hero title: `animate-fade-in`
- Sidebar stats panel: `animate-slide-in`

### Transitions

- **Cards hover**: `hover:shadow-xl transition-shadow`
- **Buttons hover**: `hover:scale-105 transition-all`
- **Markers hover**: `hover:scale-110 transition-transform`
- **Stats items hover**: `hover:bg-gray-100 transition-colors`

---

## SEO et Accessibilité

### SEO

La landing page devrait inclure (à ajouter dans `index.html`):

```html
<meta name="description" content="TEDI - Plateforme de données territoriales et économiques pour l'Afrique. Accédez aux données agricoles, d'emploi, d'immobilier et de business pour le Bénin.">
<meta name="keywords" content="données économiques, Bénin, agriculture, emploi, immobilier, API, open data">
<meta property="og:title" content="TEDI Platform - Données Territoriales pour l'Afrique">
<meta property="og:description" content="Accédez à des données fiables sur l'agriculture, l'emploi, l'immobilier et le business au Bénin">
<meta property="og:image" content="/og-image.png">
```

### Accessibilité

**Améliorations recommandées**:

1. **Aria Labels**:
```vue
<button
  @click="selectedCommune = null"
  aria-label="Fermer le panneau de statistiques"
>
  <!-- Close icon -->
</button>
```

2. **Alt Text pour SVG**:
```vue
<svg role="img" aria-label="Icône de localisation">
  <!-- SVG content -->
</svg>
```

3. **Navigation Clavier**:
- Tab order logique
- Focus visible sur marqueurs
- Escape pour fermer panneau

4. **Contraste**:
- ✅ Texte blanc sur fond gradient (ratio > 4.5:1)
- ✅ Badges colorés avec bon contraste

---

## Tests

### Checklist de Test Manuel

- [ ] Page charge sans erreurs
- [ ] Carte s'affiche correctement
- [ ] Marqueurs apparaissent pour toutes les communes
- [ ] Clic sur marqueur affiche le panneau
- [ ] Stats se chargent pour chaque commune
- [ ] Top crops s'affichent correctement
- [ ] Bouton "Voir Toutes les Données" navigue correctement
- [ ] Bouton fermer (×) ferme le panneau
- [ ] Liens de navigation fonctionnent
- [ ] Responsive sur mobile/tablet
- [ ] Animations fluides
- [ ] Pas de console errors

### Tests Automatisés (Recommandés)

```javascript
import { mount } from '@vue/test-utils'
import LandingView from '@/views/LandingView.vue'

describe('LandingView', () => {
  it('renders hero section', () => {
    const wrapper = mount(LandingView)
    expect(wrapper.text()).toContain('TEDI Platform')
  })

  it('loads communes on mount', async () => {
    const wrapper = mount(LandingView)
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.communes.length).toBeGreaterThan(0)
  })

  it('displays stats when commune selected', async () => {
    const wrapper = mount(LandingView)
    await wrapper.vm.selectCommune({ id: 1, name: 'Cotonou' })
    expect(wrapper.vm.selectedCommune).toBeTruthy()
  })
})
```

---

## Maintenance

### Mises à Jour Fréquentes

1. **Overview Stats**: Se mettent à jour automatiquement via API
2. **Nouvelles Communes**: Apparaissent automatiquement après ingestion OSM
3. **Nouvelles Données**: Compteurs s'actualisent automatiquement

### Changements à Faire Manuellement

1. **Nombre de Sources de Données**:
```javascript
const overview = ref({
  communes: 0,
  dataSources: 4,  // ← Mettre à jour si ajout de sources
  dataPoints: 0,
})
```

2. **Liste des Sources** (Features Section):
```vue
<p>Agrégation de sources officielles : FAOSTAT, Banque Mondiale, ILOSTAT, OpenStreetMap</p>
<!-- Ajouter nouvelles sources ici -->
```

3. **Fréquence de Mise à Jour**:
```vue
<p>Données actualisées automatiquement toutes les 6 heures</p>
<!-- Ajuster si changement de fréquence -->
```

---

## Améliorations Futures

### Phase 1: Expérience Utilisateur

1. **Recherche de Commune**:
```vue
<div class="search-bar">
  <input
    v-model="searchQuery"
    @input="filterCommunes"
    placeholder="Rechercher une commune..."
  />
</div>
```

2. **Filtres sur la Carte**:
- Par région
- Par niveau de données disponibles
- Par population
- Par superficie

3. **Comparaison de Communes**:
- Sélectionner 2-3 communes
- Vue comparée côte à côte

### Phase 2: Visualisations Avancées

1. **Graphiques dans le Panneau**:
- Chart.js ou D3.js
- Évolution temporelle des données
- Comparaison avec moyenne nationale

2. **Heatmap**:
- Intensité de couleur selon données disponibles
- Ou selon indicateur choisi (population, production, etc.)

3. **Mode 3D** (Optionnel):
- Cesium.js pour vue 3D
- Hauteur des bâtiments basée sur données

### Phase 3: Partage et Export

1. **Partage de Vue**:
- URL avec commune pré-sélectionnée: `/?commune=Cotonou`
- Deep linking

2. **Export PDF**:
- Générer rapport PDF de la commune
- Inclure carte, stats, graphiques

3. **Embed Widget**:
- Code iframe pour intégrer carte sur sites externes
- Personnalisable (couleurs, communes affichées)

---

## Troubleshooting

### Issue: Carte ne s'affiche pas

**Symptômes**: Zone blanche où devrait être la carte

**Solutions**:
1. Vérifier import Leaflet CSS: `import 'leaflet/dist/leaflet.css'`
2. Vérifier hauteur du conteneur: `style="height: 600px"`
3. Vérifier que map.value n'est pas null

### Issue: Marqueurs ne s'affichent pas

**Symptômes**: Carte visible mais pas de marqueurs

**Solutions**:
1. Vérifier que communes ont `center_lat` et `center_lon`
2. Vérifier console pour erreurs API
3. Vérifier que `addCommuneMarker()` est appelée

### Issue: Stats ne se chargent pas

**Symptômes**: Spinner infini ou panel vide

**Solutions**:
1. Vérifier que endpoints API fonctionnent
2. Vérifier auth (API key peut être requise)
3. Vérifier CORS si applicable
4. Regarder Network tab dans DevTools

### Issue: Performance lente

**Symptômes**: Lag lors du clic sur communes

**Solutions**:
1. Implémenter debounce sur loadCommuneStats
2. Ajouter cache local
3. Réduire nombre de marqueurs affichés
4. Utiliser marker clustering

---

## Ressources

### Documentation Externe

- [Leaflet.js Documentation](https://leafletjs.com/)
- [OpenStreetMap Wiki](https://wiki.openstreetmap.org/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Vue.js Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)

### Fichiers Liés

- `/frontend/src/views/LandingView.vue` - Composant principal
- `/frontend/src/router/index.js` - Configuration des routes
- `/frontend/src/services/api.js` - Appels API
- `/frontend/tailwind.config.js` - Configuration couleurs

### Backend Endpoints

- Documentation: http://localhost:5000/api/docs
- Agriculture: `/api/v1/agriculture/*`
- Employment: `/api/v1/employment/*`
- Business: `/api/v1/business/*`
- Real Estate: `/api/v1/realestate/*`

---

**Last Updated**: 2026-01-13
**Component**: `/frontend/src/views/LandingView.vue`
**Author**: TEDI Development Team
