# TEDI - Getting Started Guide

## 🎉 Complete MVP Features

Félicitations! Votre MVP TEDI est maintenant **100% fonctionnel** avec toutes les fonctionnalités clés implémentées.

## 🚀 Démarrage Rapide

### Étape 1: Lancer les Services
```bash
cd TEDI_data
docker-compose up -d
```

### Étape 2: Initialiser la Base de Données
```bash
# Créer le schéma et les seeds de base
docker exec -it tedi_backend python scripts/seed_database.py

# Ajouter les données agricoles d'exemple (IMPORTANT!)
docker exec -it tedi_backend python scripts/add_sample_agriculture_data.py

# Ajouter les coordonnées GPS aux communes (IMPORTANT pour la carte!)
docker exec -it tedi_backend python scripts/add_commune_coordinates.py
```

**⚠️ IMPORTANT:** Sauvegardez la clé API demo affichée après la première commande!

### Étape 3: Accéder à l'Application

**Frontend Dashboard**: http://localhost:3000
- Login avec votre clé API demo
- Explorez toutes les fonctionnalités

**Backend API**: http://localhost:5000
- Documentation Swagger: http://localhost:5000/api/docs
- Health check: http://localhost:5000/health

## 🎯 Fonctionnalités Disponibles

### ✅ Backend Complet
- **API REST** avec 10+ endpoints
- **PostgreSQL + PostGIS** avec données géospatiales
- **Authentification** par API Key avec scopes
- **77 communes** du Bénin avec coordonnées GPS
- **10 cultures** (Maïs, Riz, Manioc, etc.)
- **~1200 points de données agricoles** (2020-2023)
- **Documentation Swagger** automatique
- **Celery + Redis** pour jobs asynchrones

### ✅ Frontend Complet
- **Dashboard** avec KPIs en temps réel
- **Page Agriculture** avec:
  - DataTable paginé et interactif
  - Filtres avancés (commune, culture, année)
  - Export CSV des données
  - Statistiques agrégées (production totale, rendement moyen, etc.)
  - Indicateurs de qualité des données
- **Carte Interactive** avec:
  - Leaflet pour visualisation géographique
  - 77 communes positionnées sur la carte
  - Popups informatifs
  - Navigation vers les données par commune
- **Gestion API Keys** avec:
  - Création de nouvelles clés
  - Documentation d'utilisation
  - Exemples de requêtes

## 📊 Données Disponibles

### Après l'initialisation complète:
- **1 pays**: Bénin
- **12 régions**: Alibori, Atacora, Atlantique, Borgou, Collines, Couffo, Donga, Littoral, Mono, Ouémé, Plateau, Zou
- **77 communes** avec coordonnées GPS
- **10 cultures**: Maïs, Riz, Manioc, Igname, Coton, Ananas, Anacarde, Tomate, Haricots, Arachide
- **~1200 statistiques agricoles** (production, rendement, prix)
- **4 années** de données: 2020, 2021, 2022, 2023

### Données Réalistes Générées:
- Production en tonnes
- Rendement par hectare
- Surface récoltée
- Prix au kg (en XOF)
- Scores de qualité (0.85-0.98)
- Données mesurées vs estimées

## 🧪 Tester l'API

### 1. Obtenir votre clé API
```bash
# Visible dans la sortie de seed_database.py
# Ou créez-en une nouvelle via le dashboard
```

### 2. Exemples de Requêtes

```bash
# Définir votre clé API
export API_KEY="votre-cle-api-ici"

# Lister toutes les communes
curl -H "X-API-KEY: $API_KEY" \
  http://localhost:5000/api/v1/agriculture/communes

# Lister toutes les cultures
curl -H "X-API-KEY: $API_KEY" \
  http://localhost:5000/api/v1/agriculture/crops

# Obtenir l'index agriculture (toutes données)
curl -H "X-API-KEY: $API_KEY" \
  http://localhost:5000/api/v1/agriculture/index

# Filtrer par commune (Cotonou = ID 9)
curl -H "X-API-KEY: $API_KEY" \
  "http://localhost:5000/api/v1/agriculture/index?commune_id=9"

# Filtrer par culture (Maïs = ID 1)
curl -H "X-API-KEY: $API_KEY" \
  "http://localhost:5000/api/v1/agriculture/index?crop_id=1"

# Filtrer par année
curl -H "X-API-KEY: $API_KEY" \
  "http://localhost:5000/api/v1/agriculture/index?year=2023"

# Combiner les filtres
curl -H "X-API-KEY: $API_KEY" \
  "http://localhost:5000/api/v1/agriculture/index?commune_id=9&crop_id=1&year=2023"

# Pagination
curl -H "X-API-KEY: $API_KEY" \
  "http://localhost:5000/api/v1/agriculture/index?page=2&per_page=20"
```

### 3. Format de Réponse

```json
{
  "data": [
    {
      "id": 1,
      "commune": {
        "id": 9,
        "name": "Cotonou"
      },
      "crop": {
        "id": 1,
        "name": "Maize"
      },
      "year": 2023,
      "production_tonnes": 5234.56,
      "yield_tonnes_per_ha": 2.15,
      "area_harvested_ha": 2434.68,
      "price_per_kg": 185.23,
      "price_currency": "XOF",
      "data_quality_score": 0.92,
      "is_estimated": false
    }
  ],
  "metadata": {
    "page": 1,
    "per_page": 50,
    "total": 1247,
    "total_pages": 25,
    "has_next": true,
    "has_prev": false
  }
}
```

## 🗺️ Utiliser la Carte Interactive

1. Accédez à http://localhost:3000/map
2. Explorez les 77 communes du Bénin
3. Cliquez sur un marqueur pour voir les détails
4. Utilisez le bouton "View Agriculture Data" pour filtrer les données par commune

## 📈 Utiliser le Dashboard Agriculture

1. Accédez à http://localhost:3000/agriculture
2. Utilisez les filtres pour:
   - Sélectionner une commune spécifique
   - Filtrer par culture
   - Choisir une année
3. Visualisez les statistiques agrégées en bas
4. Exportez les données en CSV

## 🔑 Gestion des API Keys

1. Accédez à http://localhost:3000/api-keys
2. Consultez votre clé actuelle (masquée)
3. Créez de nouvelles clés avec le bouton "Create New Key"
4. **IMPORTANT**: Sauvegardez la clé immédiatement après création!

## 🛠️ Commandes Utiles

### Logs
```bash
# Tous les services
docker-compose logs -f

# Backend uniquement
docker-compose logs -f backend

# Frontend uniquement
docker-compose logs -f frontend
```

### Redémarrage
```bash
# Redémarrer tous les services
docker-compose restart

# Redémarrer le backend
docker-compose restart backend

# Rebuild complet
docker-compose up -d --build
```

### Base de Données
```bash
# Accéder à PostgreSQL
docker exec -it tedi_postgres psql -U tedi_user -d tedi_db

# Requêtes utiles
\dt                              # Lister les tables
SELECT COUNT(*) FROM agri_stats; # Nombre de statistiques
SELECT COUNT(*) FROM communes;   # Nombre de communes
SELECT COUNT(*) FROM crops;      # Nombre de cultures
```

### Shell Python Backend
```bash
docker exec -it tedi_backend flask shell

# Dans le shell Python
from app.models import *
from app import db

# Compter les données
AgriStats.query.count()
Commune.query.count()
Crop.query.count()
```

## 📁 Structure des Fichiers Clés

```
TEDI_data/
├── backend/
│   ├── app/
│   │   ├── models/              # Models SQLAlchemy
│   │   ├── routes/              # API endpoints
│   │   ├── services/            # Business logic
│   │   └── utils/               # Utilities
│   └── scripts/
│       ├── seed_database.py                      # 🔴 Seeds initiaux
│       ├── add_sample_agriculture_data.py        # 🔴 Données agricoles
│       └── add_commune_coordinates.py            # 🔴 Coordonnées GPS
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── DataTable.vue                     # 🟢 Table interactive
│       │   ├── FilterPanel.vue                   # 🟢 Panneau de filtres
│       │   └── Navbar.vue                        # 🟢 Navigation
│       └── views/
│           ├── DashboardView.vue                 # 🟢 Dashboard principal
│           ├── AgricultureView.vue               # 🟢 Page agriculture complète
│           ├── MapView.vue                       # 🟢 Carte Leaflet
│           └── ApiKeysView.vue                   # 🟢 Gestion API keys
├── README.md              # Documentation complète
├── QUICKSTART.md          # Démarrage en 5 min
├── GETTING_STARTED.md     # Ce fichier
└── PROJECT_STATUS.md      # État du projet
```

## ✅ Checklist de Vérification

Après l'installation, vérifiez que tout fonctionne:

- [ ] Docker Compose démarré (`docker-compose ps` - tous les services "Up")
- [ ] Base de données initialisée (seed_database.py)
- [ ] Données agricoles ajoutées (add_sample_agriculture_data.py)
- [ ] Coordonnées GPS ajoutées (add_commune_coordinates.py)
- [ ] Frontend accessible (http://localhost:3000)
- [ ] Backend accessible (http://localhost:5000/health retourne 200)
- [ ] Login fonctionne avec la clé API demo
- [ ] Dashboard affiche les statistiques
- [ ] Page Agriculture affiche le tableau avec données
- [ ] Filtres fonctionnent
- [ ] Export CSV fonctionne
- [ ] Carte affiche les communes
- [ ] Swagger docs accessible (http://localhost:5000/api/docs)

## 🎓 Prochaines Étapes

### Phase 1 - Enrichissement des Données (Recommandé)
- Connecter aux vraies API (FAOSTAT, World Bank)
- Importer des données réelles pour le Bénin
- Ajouter les géométries PostGIS complètes des communes

### Phase 2 - Amélioration Frontend
- Ajouter des graphiques (Chart.js)
- Implémenter des vues comparatives
- Ajouter des indicateurs avancés

### Phase 3 - Production
- Déployer sur VPS
- Configurer SSL/TLS
- Ajouter monitoring et logs
- Optimiser les performances

## 📞 Support

Pour toute question:
- Consultez README.md pour la documentation complète
- Voir PROJECT_STATUS.md pour l'état du projet
- Vérifiez les logs: `docker-compose logs -f`

---

**🎉 Félicitations! Votre MVP TEDI est prêt à l'emploi!**

Fait avec ❤️ pour TEDI - Territorial & Economic Data Index
