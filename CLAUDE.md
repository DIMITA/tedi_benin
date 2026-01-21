# CLAUDE CONTEXT - TEDI PROJECT

## RÉSUMÉ EXÉCUTIF
TEDI (Territorial & Economic Data Index) est une plateforme de données territoriales, économiques et sociales pour l'Afrique, démarrant avec le Bénin. L'objectif est de fournir des datasets structurés, enrichis et AI-ready pour les banques, gouvernements, ONGs et startups.

## MVP - AGRICULTURE DATA INDEX (PHASE 1)
**Périmètre strict du MVP:**
- 1 pays: Bénin
- 1 verticale: Agriculture
- 3 cultures stratégiques
- Niveau d'agrégation: Communes
- API REST + Dashboard d'administration
- Pipeline d'ingestion de données

**Exclusions MVP:**
- Paiements
- Prédictions ML
- Multi-pays
- User-generated content

## ARCHITECTURE TECHNIQUE

### Backend Stack
- Python 3.11
- Flask + Flask-RESTX (API)
- SQLAlchemy ORM
- PostgreSQL + PostGIS (données géospatiales)
- Celery + Redis (jobs asynchrones)

### Frontend Stack
- Vue.js 3 (Composition API)
- Vite (build tool)
- TailwindCSS (styling)
- Pinia (state management)
- Axios (HTTP client)
- Leaflet (cartes)

### Infrastructure
- Docker + Docker Compose
- Nginx (reverse proxy)
- VPS (Hetzner/OVH/Hostinger)

## SCHÉMA BASE DE DONNÉES (CORE)
```
countries → regions → communes (avec géométrie PostGIS)
crops (cultures)
agri_stats (statistiques agricoles par commune/culture/année)
data_sources (métadonnées des sources)
dataset_versions (versioning)
```

## SOURCES DE DONNÉES AGRICULTURE
1. **FAOSTAT** (FAO) - Statistiques agricoles mondiales
2. **World Bank Agriculture** - Indicateurs agriculture
3. **Open Data Africa** (Benin) - Données locales
4. **INStaD** (Institut National de la Statistique - Bénin)
5. **data.gouv.bj** - Portail open data du Bénin
6. **Copernicus/Landsat** (optionnel) - Imagerie satellite

## STRATÉGIE MULTI-SOURCES (POST-MVP)

### ⚠️ PRINCIPE CLÉ: TOUJOURS PLUSIEURS SOURCES
**IMPORTANT:** Une seule source n'est JAMAIS suffisante. Chaque donnée doit provenir de **minimum 2-3 sources** pour validation croisée.

### Agriculture - Sources Multiples
- **Production/Rendement:** FAOSTAT + INStaD + data.gouv.bj
- **Prix:** World Bank + marchés locaux + data.gouv.bj
- **Imagerie satellite:** Copernicus + Landsat (validation surfaces)
- **Météo/Climat:** World Bank Climate + données locales

### Real Estate - Sources à Intégrer
- **Prix immobiliers:** Sites d'annonces (expat-dakar.com, jumia.house) + notaires + banques
- **Cadastre:** Ministère des Affaires Foncières + data.gouv.bj
- **Infrastructure:** OpenStreetMap + World Bank Infrastructure Index
- **Zones à risque:** World Bank + organisations locales

### Employment - Sources à Intégrer
- **Statistiques emploi:** INStaD + World Bank + ILO (International Labour Organization)
- **Salaires:** Enquêtes sectorielles + World Bank + données entreprises
- **Secteurs:** Registre du commerce + INStaD
- **Formation:** Ministère de l'Éducation + partenaires techniques

### Business - Sources à Intégrer
- **Registre entreprises:** APIEX (Agence de Promotion des Investissements) + data.gouv.bj
- **Indicateurs économiques:** World Bank Doing Business + INStaD
- **Secteurs:** Chambres de Commerce + statistiques nationales
- **Investissements:** Banques + rapports sectoriels

### Architecture Multi-Sources
```
Source A ─┐
Source B ─┼──> Validation Croisée ──> Scoring Qualité ──> Donnée Finale
Source C ─┘
```

### Scoring de Qualité Multi-Sources
- **1 source:** Qualité = 60% max
- **2 sources concordantes:** Qualité = 80%
- **3+ sources concordantes:** Qualité = 95%+
- **Sources conflictuelles:** Flag pour révision manuelle

## API ENDPOINTS (MVP)
```
GET /api/v1/agriculture/communes
GET /api/v1/agriculture/crops
GET /api/v1/agriculture/index?commune_id=&year=
```
- Authentification via API Key (header X-API-KEY)
- Format réponse: `{ "data": [], "metadata": {} }`

## PIPELINE DE DONNÉES
1. **Fetch** - Récupération données brutes (API/CSV)
2. **Validate** - Validation du schéma
3. **Normalize** - Normalisation des valeurs
4. **Enrich** - Enrichissement géospatial + indices
5. **Store** - Stockage versionné

## DASHBOARD FRONTEND (MVP)
Pages essentielles:
- Login
- Dashboard (KPIs)
- Agriculture Index (table + filtres)
- Map View (Leaflet)
- API Keys Management

Composants clés:
- DataTable
- Map (Leaflet)
- Filters
- KPI Cards

## PRIORITÉS DE DÉVELOPPEMENT

### 1. Setup Infrastructure
- Docker Compose (PostgreSQL + PostGIS, Redis, Backend, Frontend)
- Structure projet backend (Flask app)
- Structure projet frontend (Vue 3 + Vite)

### 2. Database & Models
- Schéma PostgreSQL + PostGIS
- Models SQLAlchemy (Country, Region, Commune, Crop, AgriStats)
- Migrations Alembic

### 3. Data Pipeline
- Scripts de fetch des sources de données
- Validation et normalisation
- ETL vers PostgreSQL
- Celery tasks pour jobs asynchrones

### 4. API Backend
- Endpoints Agriculture
- Authentification API Key
- Swagger documentation (Flask-RESTX)
- Tests unitaires

### 5. Frontend Dashboard
- Layout + routing Vue
- Page Agriculture Index
- Intégration carte Leaflet
- Filtres et exports

### 6. Déploiement
- Configuration Nginx
- Setup VPS
- CI/CD (optionnel MVP)

## MÉTRIQUES DE SUCCÈS MVP
- Cohérence des données
- Usabilité API
- Premier utilisateur externe adopte la plateforme

## ROADMAP POST-MVP
- Phase 2: Real Estate Index
- Phase 3: Employment Index
- Phase 4: Business Index
- Phase 5: Corrélations cross-index + licensing AI

## LABELLISATION & INDICES (POST-MVP)

### 🌾 Agriculture Indices
- **crop_type** 🌱 - Type de culture (céréale, tubercule, cash crop, etc.)
- **geo_zone** 📍 - Zone géographique (nord, sud, côtier, etc.)
- **climate_risk_level** 🌧️ - Niveau de risque climatique (bas, moyen, élevé)
- **soil_quality_index** 🧪 - Indice de qualité du sol (0-100)
- **yield_estimation_class** 📈 - Classe d'estimation du rendement (faible, moyen, élevé)
- **price_volatility_index** 💰 - Indice de volatilité des prix (0-100)
- **mechanization_level** 🚜 - Niveau de mécanisation (manuel, semi-mécanisé, mécanisé)

### 🏠 Real Estate Indices
- **property_type** 🏠 - Type de propriété (résidentiel, commercial, agricole, industriel)
- **geo_zone** 📍 - Zone géographique (urbain, périurbain, rural)
- **price_per_sqm_index** 💰 - Indice de prix par m² (normalisé 0-100)
- **price_trend** 📈 - Tendance des prix (baisse, stable, hausse, hausse forte)
- **land_risk_level** ⚠️ - Niveau de risque foncier (bas, moyen, élevé)
- **infrastructure_score** 🛣️ - Score d'infrastructure (0-100)
- **legal_clarity_index** 🧾 - Indice de clarté juridique (0-100)
- **development_potential** 🏗️ - Potentiel de développement (faible, moyen, élevé, très élevé)

### 💼 Employment Indices
- **job_category** - Catégorie d'emploi (agriculture, services, industrie, commerce, etc.)
- **skill_level_index** - Indice de niveau de compétence (0-100)
- **employment_pressure_index** - Indice de pression sur l'emploi (0-100)
- **informality_rate** - Taux d'informalité (0-100%)
- **salary_range_estimation** - Estimation de fourchette salariale (classe: bas, moyen, élevé)

### 🏢 Business Indices
- **business_density_index** - Indice de densité d'entreprises (0-100)
- **sector_growth_score** - Score de croissance sectorielle (0-100)
- **economic_resilience_index** - Indice de résilience économique (0-100)
- **market_gap_indicator** - Indicateur d'écart de marché (0-100)

## NOTES IMPORTANTES

### Qualité des données
- **Provenance obligatoire**: Chaque donnée doit tracer sa source
- **Versioning**: Garder l'historique des datasets
- **Validation**: Schémas stricts avant insertion
- **Géolocalisation**: Utiliser PostGIS pour les données spatiales

### Scalabilité
- Design pour multi-pays dès le départ (même si MVP = Bénin)
- Architecture modulaire par verticale
- API versionnée (v1)

### Conformité
- Données légales et open data uniquement
- Respect des licences (mentionner sources)
- RGPD non applicable (données publiques agrégées)

### Tech Decisions
- **PostGIS** mandatory pour géospatial
- **Celery** pour jobs longs (fetch + ETL)
- **Flask-RESTX** pour auto-doc Swagger
- **Alembic** pour migrations DB
- **Docker** pour environnement reproductible

## FICHIERS EXISTANTS
- 01_PRD.md: Product Requirements
- 02_MVP_SCOPE.md: Périmètre MVP
- 03_TECH_ARCHITECTURE.md: Stack technique
- 04_DATA_SOURCES.md: Sources de données
- 05_DATABASE_SCHEMA.md: Schéma DB
- 06_API_SPECIFICATION.md: Specs API
- 07_FRONTEND_SPEC.md: Specs Frontend
- 08_ROADMAP.md: Roadmap produit
- CLAUDE.md: Ce fichier (context AI)

## PROCHAINES ACTIONS
Voir le plan détaillé d'exécution dans le fichier approprié ou via TodoList.
