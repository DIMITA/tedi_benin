# TEDI - Système de Scheduler Automatique de Données

## 📅 Date: 13 Janvier 2026

## ✅ Phase 1 Complétée: Infrastructure de Versioning & Tracking

### 🎯 Objectif
Créer un système de **récupération automatique** des données depuis les sources externes, avec des **fréquences adaptées** à la réalité de chaque source (pas du temps réel inutile).

---

## 🏗️ Infrastructure Créée

### 1. Modèles de Base de Données

#### `DatasetVersion` (enrichi dans `metadata.py`)
**Table**: `dataset_versions`

**Nouveaux Champs Ajoutés**:
```python
# AUTO-INGESTION: Scheduling fields
last_checked_at          # Dernière vérification
last_updated_at          # Dernière mise à jour réelle
next_check_at            # Prochaine vérification planifiée
check_enabled            # Activer/désactiver auto-check

# AUTO-INGESTION: Reliability tracking
source_reliability_score  # Score 0.0 à 1.0
consecutive_failures      # Nombre d'échecs consécutifs
last_error               # Dernier message d'erreur

# AUTO-INGESTION: Ingestion stats
last_ingestion_duration_seconds  # Durée de la dernière ingestion
last_records_added               # Records ajoutés
last_records_updated             # Records mis à jour
```

**Méthodes Intelligentes**:
- `should_check()` - Détermine si c'est le moment de vérifier
- `calculate_next_check()` - Calcule la prochaine vérification selon la fréquence
- `mark_checked()` - Marque comme vérifié avec tracking

#### `IngestionLog` (nouveau dans `ingestion.py`)
**Table**: `ingestion_logs`

**But**: Audit détaillé de chaque tentative d'ingestion

```python
# Execution details
task_id                  # ID de la tâche Celery
status                   # pending, running, success, failed, skipped
started_at, completed_at # Timestamps
duration_seconds         # Durée d'exécution

# Results
records_fetched          # Nombre de records récupérés
records_added            # Ajoutés
records_updated          # Mis à jour
records_skipped          # Ignorés

# Change detection
checksum_before, checksum_after  # SHA256 pour détecter les changements
has_changes              # Boolean

# Error handling
error_message            # Message d'erreur
error_traceback          # Traceback complet
ingestion_metadata       # Métadonnées JSON flexibles
```

**Méthodes**:
- `create_log()` - Créer un nouveau log
- `mark_running()` - Marquer comme en cours
- `mark_success()` - Marquer comme succès avec stats
- `mark_failed()` - Marquer comme échec avec erreur
- `mark_skipped()` - Marquer comme ignoré (pas de changement)

#### `DataSourceConfig` (nouveau dans `ingestion.py`)
**Table**: `data_source_configs`

**But**: Configuration des sources externes

```python
# Source identification
source_name              # Nom unique (faostat, world_bank, etc.)
display_name             # Nom d'affichage
source_type              # api, csv, xml, excel, scraping

# API Configuration
base_url                 # URL de base
api_key, api_secret      # Credentials (encrypted en prod)

# Connection settings
timeout_seconds          # Timeout par défaut
rate_limit_per_hour      # Limite de taux

# Authentication
auth_type                # none, api_key, oauth, basic
auth_config              # Config JSON flexible

# Status
is_active                # Actif/inactif
last_successful_connection  # Dernière connexion réussie
```

---

## 📊 Fréquences Recommandées (Rappel)

### Agriculture
| Source | Type | Fréquence | Détection Changement |
|--------|------|-----------|---------------------|
| FAOSTAT | Production, rendements | **Trimestrielle** | ✅ Checksum |
| World Bank | Indicateurs macro | **Annuelle** | ✅ Check semestriel |
| Open Data Bénin | Données nationales | **Mensuelle** | ✅ Si changement uniquement |
| INStaD / NADA | Enquêtes agricoles | **À l'événement** | ⚠️ Ingestion manuelle |
| Satellite (NDVI) | Végétation | **Mensuelle** | ✅ Agrégation mensuelle |

### Immobilier
| Source | Type | Fréquence | Note |
|--------|------|-----------|------|
| data.gouv.bj | Cadastre, zonage | **Trimestrielle** | Versioning obligatoire |
| OpenStreetMap | Bâtiments, routes | **Mensuelle** | Extraction par zone |
| Portails annonces | Prix affichés | **Hebdomadaire** | Agrégation immédiate |

### Emploi
| Source | Type | Fréquence | Note |
|--------|------|-----------|------|
| ILOSTAT | Emploi, chômage | **Annuelle** | Check semestriel |
| World Bank | Indicateurs emploi | **Annuelle** | - |
| INStaD | Enquêtes terrain | **À publication** | Ingestion manuelle |

### Business
| Source | Type | Fréquence | Note |
|--------|------|-----------|------|
| World Bank | Business indicators | **Annuelle** | - |
| UNIDO / OECD | Industrie | **Annuelle** | - |
| Registres locaux | RCCM | **Trimestrielle** | Parfois semestrielle |

---

## 🔄 Workflow de Récupération Automatique

```
┌─────────────────────────────────────────────────────────┐
│  1. SCHEDULER (Celery Beat)                             │
│     - Check toutes les 6 heures                         │
│     - Query: DatasetVersion.should_check()              │
└────────────────┬────────────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────────────┐
│  2. TÂCHE CELERY (Ingestion Task)                       │
│     - Créer IngestionLog(status='pending')              │
│     - Mark running                                       │
│     - Fetch data depuis source                          │
│     - Calculate checksum                                 │
└────────────────┬────────────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────────────┐
│  3. DÉTECTION DE CHANGEMENT                             │
│     - Compare checksum_before vs checksum_after         │
│     - Si identique → mark_skipped()                     │
│     - Si différent → continuer                          │
└────────────────┬────────────────────────────────────────┘
                 │ (si changement détecté)
                 v
┌─────────────────────────────────────────────────────────┐
│  4. VALIDATION & TRANSFORMATION                         │
│     - Valider le format des données                     │
│     - Transformer selon schéma TEDI                     │
│     - Appliquer quality scoring                         │
└────────────────┬────────────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────────────┐
│  5. INSERTION EN BASE                                   │
│     - Insérer nouveaux records                          │
│     - Update records existants                          │
│     - Créer source contributions                        │
└────────────────┬────────────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────────────┐
│  6. FINALISATION                                        │
│     - IngestionLog.mark_success()                       │
│     - DatasetVersion.mark_checked()                     │
│     - Calculate next_check_at                           │
│     - Update reliability_score                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🛡️ Mécanismes de Sécurité

### 1. **Circuit Breaker**
```python
if consecutive_failures >= 5:
    # Arrêter les checks automatiques
    check_enabled = False
```

### 2. **Backoff Exponential** (à implémenter)
```python
# Après un échec, attendre de plus en plus longtemps
wait_time = base_delay * (2 ** consecutive_failures)
```

### 3. **Rate Limiting**
```python
# Respecter les limites de l'API
rate_limit_per_hour = 100  # Dans DataSourceConfig
```

### 4. **Timeout Protection**
```python
# Pas d'ingestion qui bloque indéfiniment
timeout_seconds = 30  # Par défaut
```

---

## 📈 Métriques & Monitoring

Le système track automatiquement:

✅ **Fiabilité**: `source_reliability_score` (0.0 à 1.0)
✅ **Performance**: `last_ingestion_duration_seconds`
✅ **Succès**: `consecutive_failures` (0 = tout va bien)
✅ **Volume**: `last_records_added`, `last_records_updated`
✅ **Changements**: `has_changes` (détection par checksum)

---

## 🎯 Prochaines Étapes

### Phase 2: Tâches Celery (À FAIRE)
1. **Créer les tâches Celery** pour chaque source
2. **Implémenter les connecteurs** pour les APIs externes
3. **Configurer Celery Beat** avec les schedules

### Phase 3: Configuration Sources (À FAIRE)
1. **Ajouter les sources** dans `DataSourceConfig`
2. **Configurer les API keys** (encrypted)
3. **Tester les connexions**

### Phase 4: Monitoring (À FAIRE)
1. **Dashboard admin** pour voir les ingestions
2. **Alertes** en cas d'échecs répétés
3. **Logs centralisés**

---

## 💻 Utilisation

### Vérifier l'état d'une source
```python
from app.models import DatasetVersion

# Get dataset version
ds = DatasetVersion.query.filter_by(
    data_source_id=1,
    version='2023.1'
).first()

# Check si prêt pour update
if ds.should_check():
    print(f"Prêt pour check! Prochaine: {ds.next_check_at}")

# Mark comme vérifié
ds.mark_checked(
    has_changes=True,
    new_checksum='abc123...',
    records_added=150,
    records_updated=25,
    duration_seconds=12.5
)
```

### Consulter les logs d'ingestion
```python
from app.models import IngestionLog

# Get recent ingestions
logs = IngestionLog.query.filter_by(
    dataset_version_id=1
).order_by(IngestionLog.started_at.desc()).limit(10).all()

for log in logs:
    print(f"{log.started_at} - {log.status}: {log.records_added} added")
```

---

## ✅ Status Actuel

**✅ COMPLÉTÉ**:
- [x] Modèles de base de données créés
- [x] Migration appliquée avec succès
- [x] Tables créées: `ingestion_logs`, `data_source_configs`
- [x] Champs de scheduling ajoutés à `dataset_versions`
- [x] Méthodes intelligentes implémentées

**⏳ EN ATTENTE**:
- [ ] Tâches Celery pour Agriculture (FAOSTAT, World Bank, etc.)
- [ ] Tâches Celery pour Real Estate (OSM, cadastre, etc.)
- [ ] Tâches Celery pour Employment (ILOSTAT, etc.)
- [ ] Tâches Celery pour Business (registres, etc.)
- [ ] Configuration Celery Beat (schedules)
- [ ] Connecteurs API externes
- [ ] Tests automatiques

---

## 🎓 Principes Clés

1. **Pas de temps réel** → Data indexé, fiable et versionné
2. **Fréquence adaptée** → Alignée sur la réalité de la source
3. **Détection de changement** → Checksum pour éviter ingestion inutile
4. **Traçabilité totale** → Chaque ingestion loggée
5. **Résilience** → Circuit breaker après échecs répétés
6. **Monitoring** → Métriques de fiabilité et performance

---

**Document créé**: 13 Janvier 2026
**Status**: Phase 1 COMPLÉTÉE ✅
**Prochaine Phase**: Création des tâches Celery

