# TEDI MVP - Instructions d'Accès

**Date de Test:** 2026-01-13
**Statut:** ✅ Testé et Fonctionnel

---

## 🔑 Clé API Demo

Utilisez cette clé pour tous les tests:

```
OHIMu02lxux9uDd0__lKMlR5fNtkMQ35-S8bHWm2l2OMDSzbufMJNf3QufujFlAW
```

**Email:** demo@tedi.africa
**Scopes:** `*` (tous les accès)
**Expiration:** Jamais

---

## 🌐 URLs d'Accès

### Frontend (Dashboard)
**URL:** http://localhost:8080

**Pages disponibles:**
- `/login` - Connexion avec API Key
- `/` - Dashboard principal
- `/agriculture` - Index Agriculture complet
- `/map` - Carte interactive (35 communes)
- `/api-keys` - Gestion des API Keys

### Backend (API)
**URL:** http://localhost:5000

**Endpoints principaux:**
- `/health` - Health check
- `/api/docs` - Documentation Swagger
- `/api/v1/agriculture/communes` - Liste des communes
- `/api/v1/agriculture/crops` - Liste des cultures
- `/api/v1/agriculture/index` - Données agricoles (filtres + pagination)
- `/api/v1/auth/keys` - Gestion API Keys
- `/api/v1/auth/validate` - Validation API Key

---

## 🚀 Quick Start

### 1. Accéder au Dashboard

```bash
# Ouvrir dans le navigateur
open http://localhost:8080
# ou
xdg-open http://localhost:8080
```

**Puis:**
1. Entrer la clé API demo (voir ci-dessus)
2. Cliquer sur "Login"
3. Explorer le dashboard!

### 2. Tester l'API avec curl

```bash
# Définir la clé API
export API_KEY="OHIMu02lxux9uDd0__lKMlR5fNtkMQ35-S8bHWm2l2OMDSzbufMJNf3QufujFlAW"

# 1. Health check (pas d'auth requise)
curl http://localhost:5000/health

# 2. Lister les communes
curl -H "X-API-KEY: $API_KEY" http://localhost:5000/api/v1/agriculture/communes

# 3. Lister les cultures
curl -H "X-API-KEY: $API_KEY" http://localhost:5000/api/v1/agriculture/crops

# 4. Obtenir l'index agriculture (5 premiers)
curl -H "X-API-KEY: $API_KEY" "http://localhost:5000/api/v1/agriculture/index?per_page=5"

# 5. Filtrer par commune (Cotonou = ID 9)
curl -H "X-API-KEY: $API_KEY" "http://localhost:5000/api/v1/agriculture/index?commune_id=9"

# 6. Filtrer par culture (Maïs = ID 1)
curl -H "X-API-KEY: $API_KEY" "http://localhost:5000/api/v1/agriculture/index?crop_id=1"

# 7. Filtrer par année
curl -H "X-API-KEY: $API_KEY" "http://localhost:5000/api/v1/agriculture/index?year=2023"

# 8. Filtrer combiné
curl -H "X-API-KEY: $API_KEY" \
  "http://localhost:5000/api/v1/agriculture/index?commune_id=9&crop_id=1&year=2023"
```

### 3. Accéder à Swagger UI

```bash
# Ouvrir dans le navigateur
open http://localhost:5000/api/docs
```

**Dans Swagger:**
1. Cliquer sur "Authorize" (cadenas en haut à droite)
2. Entrer la clé API dans le champ
3. Cliquer sur "Authorize"
4. Tester les endpoints avec "Try it out"

---

## 📊 Données Disponibles

### Statistiques Globales
- **Communes:** 77
- **Régions:** 12
- **Cultures:** 10
- **Statistiques Agricoles:** 978
- **Années:** 2020-2023
- **Communes avec GPS:** 35

### Cultures Disponibles
1. Maize (Maïs)
2. Rice (Riz)
3. Cassava (Manioc)
4. Yam (Igname)
5. Cotton (Coton)
6. Pineapple (Ananas)
7. Cashew (Anacarde)
8. Tomato (Tomate)
9. Beans (Haricots)
10. Groundnut (Arachide)

### Communes Principales avec GPS
- Cotonou (Littoral)
- Porto-Novo (Ouémé)
- Parakou (Borgou)
- Abomey-Calavi (Atlantique)
- Djougou (Donga)
- Bohicon (Zou)
- Kandi (Alibori)
- Natitingou (Atacora)
- Savalou (Collines)
- Lokossa (Mono)
- Aplahoué (Couffo)
- Pobè (Plateau)
... et 23 autres

---

## 🧪 Tests à Effectuer

### Test 1: Login Frontend
1. Aller sur http://localhost:8080
2. Entrer la clé API
3. ✅ Vérifier redirection vers dashboard

### Test 2: Dashboard
1. ✅ Vérifier les 3 KPI cards (communes, crops, data points)
2. ✅ Cliquer sur "Explore Agriculture Data"

### Test 3: Page Agriculture
1. ✅ Vérifier que le tableau charge avec des données
2. ✅ Tester les filtres:
   - Sélectionner une commune (ex: Cotonou)
   - Sélectionner une culture (ex: Maize)
   - Sélectionner une année (ex: 2023)
3. ✅ Cliquer sur "Clear Filters"
4. ✅ Tester la pagination (Next/Previous)
5. ✅ Cliquer sur "Export CSV"
6. ✅ Vérifier les statistiques en bas (production, yield, area, price)

### Test 4: Carte Interactive
1. ✅ Aller sur http://localhost:8080/map
2. ✅ Vérifier que la carte affiche le Bénin
3. ✅ Cliquer sur un marqueur (ex: Cotonou)
4. ✅ Vérifier le popup avec infos
5. ✅ Vérifier la sidebar avec détails de la commune
6. ✅ Cliquer sur "View Agriculture Data"
7. ✅ Vérifier que les filtres sont appliqués

### Test 5: API Keys Management
1. ✅ Aller sur http://localhost:8080/api-keys
2. ✅ Vérifier que la clé actuelle est masquée
3. ✅ Cliquer sur "Create New Key"
4. ✅ Remplir le formulaire
5. ✅ Vérifier que la nouvelle clé s'affiche (une seule fois)
6. ✅ Copier et sauvegarder la clé

### Test 6: API avec Swagger
1. ✅ Aller sur http://localhost:5000/api/docs
2. ✅ Authoriser avec la clé API
3. ✅ Tester GET /api/v1/agriculture/communes
4. ✅ Tester GET /api/v1/agriculture/index avec filtres

---

## 🔧 Commandes Docker Utiles

### Voir les Logs
```bash
# Tous les services
docker compose logs -f

# Backend uniquement
docker compose logs -f backend

# Frontend uniquement
docker compose logs -f frontend

# PostgreSQL uniquement
docker compose logs -f postgres
```

### Redémarrer un Service
```bash
# Backend
docker compose restart backend

# Frontend
docker compose restart frontend

# Tous
docker compose restart
```

### Arrêter / Démarrer
```bash
# Arrêter tous les services
docker compose down

# Démarrer tous les services
docker compose up -d

# Rebuild et redémarrer
docker compose up -d --build
```

### Accéder à la Base de Données
```bash
# Ligne de commande PostgreSQL
docker exec -it tedi_postgres psql -U tedi_user -d tedi_db

# Quelques requêtes utiles
\dt                                    # Lister les tables
SELECT COUNT(*) FROM agri_stats;       # Nombre de stats
SELECT COUNT(*) FROM communes;         # Nombre de communes
SELECT COUNT(*) FROM crops;            # Nombre de cultures

# Top 5 productions
SELECT
  c.name as commune,
  cr.name as crop,
  a.year,
  a.production_tonnes
FROM agri_stats a
JOIN communes c ON a.commune_id = c.id
JOIN crops cr ON a.crop_id = cr.id
ORDER BY a.production_tonnes DESC
LIMIT 5;
```

---

## ⚠️ Notes Importantes

### Ports Modifiés
Les ports ont été modifiés pour éviter les conflits avec les services locaux:
- **PostgreSQL:** 5433 (au lieu de 5432)
- **Redis:** 6380 (au lieu de 6379)
- **Frontend:** 8080 (au lieu de 3000)
- **Backend:** 5000 (inchangé)

### Celery Worker
Le worker Celery n'est pas nécessaire pour le MVP.
Il n'est utilisé que pour les jobs asynchrones (fetch de données, ETL, etc.).

### Données
Les données agricoles sont **générées de manière réaliste** mais ne proviennent pas directement de FAOSTAT.
Pour la production, il faudra intégrer les vraies API (voir Phase 2).

---

## 📞 Problèmes Courants

### Le frontend ne charge pas
```bash
# Vérifier les logs
docker compose logs frontend

# Redémarrer
docker compose restart frontend
```

### Erreur 401 sur l'API
- Vérifier que le header `X-API-KEY` est bien inclus
- Vérifier que la clé API est correcte
- Tester avec l'endpoint de validation:
  ```bash
  curl "http://localhost:5000/api/v1/auth/validate?key=VOTRE_CLE"
  ```

### La base de données est vide
Ré-exécuter les scripts de seed:
```bash
docker exec -it tedi_backend python scripts/seed_database.py
docker exec -it tedi_backend python scripts/add_sample_agriculture_data.py
docker exec -it tedi_backend python scripts/add_commune_coordinates.py
```

### Port déjà utilisé
Si un port est toujours occupé, modifier dans `docker-compose.yml`:
```yaml
ports:
  - "NOUVEAU_PORT:PORT_INTERNE"
```

---

## ✅ Checklist de Vérification

- [ ] Services Docker tous en "Up"
- [ ] Backend répond sur http://localhost:5000/health
- [ ] Frontend accessible sur http://localhost:8080
- [ ] Login fonctionne avec la clé API demo
- [ ] Dashboard affiche les KPIs
- [ ] Page Agriculture affiche le tableau
- [ ] Filtres fonctionnent
- [ ] Export CSV fonctionne
- [ ] Carte affiche les communes
- [ ] Swagger docs accessible

---

**Bon test! 🚀**

Pour toute question, consulter:
- README.md (documentation complète)
- GETTING_STARTED.md (guide détaillé)
- TEST_RESULTS.md (résultats des tests)
- PROJECT_STATUS.md (état du projet)
