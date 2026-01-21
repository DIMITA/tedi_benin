# 🚀 Guide de Déploiement TEDI - Serveur Debian

Ce guide détaille le déploiement complet de la plateforme TEDI sur un serveur Debian (11/12).

## 📋 Prérequis

- Serveur Debian 11 (Bullseye) ou 12 (Bookworm)
- Accès root ou utilisateur avec sudo
- Nom de domaine pointant vers le serveur (ex: `tedi.bj`)
- Minimum 2 Go RAM, 20 Go d'espace disque

---

## Étape 1 : Mise à jour du système

```bash
# Connexion au serveur
ssh root@votre-serveur-ip

# Mise à jour du système
apt update && apt upgrade -y

# Installation des outils de base
apt install -y curl wget git nano htop ufw software-properties-common ca-certificates gnupg lsb-release
```

---

## Étape 2 : Création d'un utilisateur dédié

```bash
# Créer un utilisateur pour l'application
adduser tedi

# Ajouter au groupe sudo
usermod -aG sudo tedi

# Se connecter avec le nouvel utilisateur
su - tedi
```

---

## Étape 3 : Installation de Docker

```bash
# Ajouter la clé GPG officielle de Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Ajouter le repository Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Installer Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER

# Appliquer les changements de groupe (ou se reconnecter)
newgrp docker

# Vérifier l'installation
docker --version
docker compose version
```

---

## Étape 4 : Configuration du Firewall

```bash
# Activer UFW
sudo ufw enable

# Autoriser SSH
sudo ufw allow 22/tcp

# Autoriser HTTP et HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Vérifier le statut
sudo ufw status
```

---

## Étape 5 : Clonage du projet

```bash
# Créer le répertoire de l'application
sudo mkdir -p /opt/tedi
sudo chown $USER:$USER /opt/tedi
cd /opt/tedi

# Cloner le repository
git clone https://github.com/votre-username/TEDI_data.git .

# Ou si vous avez un fichier tar/zip
# scp votre-machine:/chemin/vers/TEDI_data.tar.gz /opt/tedi/
# tar -xzf TEDI_data.tar.gz
```

---

## Étape 6 : Configuration de l'environnement

### 6.1 Créer le fichier .env

```bash
cd /opt/tedi

# Créer le fichier d'environnement
cat > .env << 'EOF'
# Base de données
POSTGRES_DB=tedi_db
POSTGRES_USER=tedi_user
POSTGRES_PASSWORD=VotreMotDePasseSecurise123!

# Backend
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=postgresql://tedi_user:VotreMotDePasseSecurise123!@postgres:5432/tedi_db
REDIS_URL=redis://redis:6379/0

# Frontend
VITE_API_URL=https://tedi.bj/api/v1

# Domaine
DOMAIN=tedi.bj
EOF

# Générer une vraie clé secrète
SECRET_KEY=$(openssl rand -hex 32)
sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env

# Sécuriser le fichier
chmod 600 .env
```

### 6.2 Créer le fichier docker-compose.prod.yml

```bash
cat > docker-compose.prod.yml << 'EOF'
services:
  # PostgreSQL avec PostGIS
  postgres:
    image: postgis/postgis:15-3.3
    container_name: tedi_postgres
    restart: always
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - tedi_network

  # Redis
  redis:
    image: redis:7-alpine
    container_name: tedi_redis
    restart: always
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - tedi_network

  # Backend Flask API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: tedi_backend
    restart: always
    environment:
      FLASK_ENV: production
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - tedi_network

  # Celery Worker
  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: tedi_celery_worker
    restart: always
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      - postgres
      - redis
    command: celery -A app.celery_app worker --loglevel=info
    networks:
      - tedi_network

  # Frontend Vue.js (Production avec Nginx)
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: production
    container_name: tedi_frontend
    restart: always
    depends_on:
      - backend
    networks:
      - tedi_network

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: tedi_nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx.prod.conf:/etc/nginx/nginx.conf:ro
      - ./certbot/www:/var/www/certbot:ro
      - ./certbot/conf:/etc/letsencrypt:ro
    depends_on:
      - backend
      - frontend
    networks:
      - tedi_network

  # Certbot pour SSL
  certbot:
    image: certbot/certbot
    container_name: tedi_certbot
    volumes:
      - ./certbot/www:/var/www/certbot
      - ./certbot/conf:/etc/letsencrypt
    networks:
      - tedi_network

volumes:
  postgres_data:
  redis_data:

networks:
  tedi_network:
    driver: bridge
EOF
```

---

## Étape 7 : Configuration du Backend pour la production

### 7.1 Créer le Dockerfile de production pour le backend

```bash
cat > backend/Dockerfile.prod << 'EOF'
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Copier le code
COPY . .

# Exposer le port
EXPOSE 5000

# Commande de démarrage avec Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "app:create_app()"]
EOF
```

---

## Étape 8 : Configuration Nginx pour la production

```bash
mkdir -p docker certbot/www certbot/conf

cat > docker/nginx.prod.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Optimisations
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript 
               application/xml+rss application/atom+xml image/svg+xml;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=general:10m rate=30r/s;

    # Upstream servers
    upstream backend {
        server backend:5000;
    }

    upstream frontend {
        server frontend:80;
    }

    # Redirection HTTP vers HTTPS
    server {
        listen 80;
        server_name tedi.bj www.tedi.bj;

        # Certbot challenge
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        # Redirection vers HTTPS
        location / {
            return 301 https://$server_name$request_uri;
        }
    }

    # Serveur HTTPS principal
    server {
        listen 443 ssl http2;
        server_name tedi.bj www.tedi.bj;

        # Certificats SSL
        ssl_certificate /etc/letsencrypt/live/tedi.bj/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/tedi.bj/privkey.pem;

        # Configuration SSL moderne
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 1d;

        # Headers de sécurité
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # API Backend
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }

        # Frontend
        location / {
            limit_req zone=general burst=50 nodelay;
            
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Fichiers statiques avec cache long
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
            proxy_pass http://frontend;
            expires 1y;
            add_header Cache-Control "public, immutable";
            access_log off;
        }
    }
}
EOF
```

---

## Étape 9 : Obtention du certificat SSL

### 9.1 Configuration temporaire pour Certbot

```bash
# Créer une configuration Nginx temporaire (sans SSL)
cat > docker/nginx.init.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        server_name tedi.bj www.tedi.bj;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            return 200 'TEDI - En cours de configuration';
            add_header Content-Type text/plain;
        }
    }
}
EOF

# Copier temporairement la config initiale
cp docker/nginx.init.conf docker/nginx.prod.conf.bak
cp docker/nginx.init.conf docker/nginx.prod.conf
```

### 9.2 Démarrer Nginx et obtenir le certificat

```bash
# Démarrer seulement Nginx
docker compose -f docker-compose.prod.yml up -d nginx

# Vérifier que Nginx fonctionne
curl http://tedi.bj

# Obtenir le certificat SSL
docker compose -f docker-compose.prod.yml run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email votre-email@example.com \
    --agree-tos \
    --no-eff-email \
    -d tedi.bj \
    -d www.tedi.bj

# Restaurer la configuration Nginx complète
mv docker/nginx.prod.conf.bak docker/nginx.prod.conf

# Redémarrer Nginx
docker compose -f docker-compose.prod.yml restart nginx
```

---

## Étape 10 : Exporter les données locales vers le serveur

### 10.1 Sur votre machine locale

```bash
# Aller dans le répertoire du projet
cd /home/dimita/Documents/project/TEDI_data

# Exporter la base de données locale
docker exec tedi_postgres pg_dump -U tedi_user -d tedi_db > backup_local.sql

# Compresser le fichier
gzip backup_local.sql

# Vérifier la taille du fichier
ls -lh backup_local.sql.gz
```

### 10.2 Transférer vers le serveur

```bash
# Transférer le dump vers le serveur
scp backup_local.sql.gz tedi@votre-serveur-ip:/opt/tedi/

# Ou avec rsync (plus fiable pour gros fichiers)
rsync -avz --progress backup_local.sql.gz tedi@votre-serveur-ip:/opt/tedi/
```

### 10.3 Sur le serveur de production

```bash
# Se connecter au serveur
ssh tedi@votre-serveur-ip
cd /opt/tedi

# Décompresser le fichier
gunzip backup_local.sql.gz

# S'assurer que la base de données est vide (optionnel - ATTENTION: supprime les données existantes)
docker compose -f docker-compose.prod.yml exec postgres psql -U tedi_user -d tedi_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Importer les données
docker compose -f docker-compose.prod.yml exec -T postgres psql -U tedi_user -d tedi_db < backup_local.sql

# Vérifier l'importation
docker compose -f docker-compose.prod.yml exec postgres psql -U tedi_user -d tedi_db -c "SELECT COUNT(*) FROM communes;"

# Supprimer le fichier d'import
rm backup_local.sql
```

### 10.4 Commande tout-en-un (depuis la machine locale)

```bash
# Export + Transfert + Import en une seule commande
cd /home/dimita/Documents/project/TEDI_data && \
docker exec tedi_postgres pg_dump -U tedi_user -d tedi_db | gzip | \
ssh tedi@votre-serveur-ip "cd /opt/tedi && gunzip | docker compose -f docker-compose.prod.yml exec -T postgres psql -U tedi_user -d tedi_db"
```

---

## Étape 11 : Déploiement complet

```bash
cd /opt/tedi

# Construire toutes les images
docker compose -f docker-compose.prod.yml build

# Démarrer tous les services
docker compose -f docker-compose.prod.yml up -d

# Vérifier que tous les conteneurs sont en cours d'exécution
docker compose -f docker-compose.prod.yml ps

# Voir les logs
docker compose -f docker-compose.prod.yml logs -f
```

---

## Étape 11 : Initialisation de la base de données

```bash
# Attendre que la base de données soit prête
sleep 10

# Exécuter les migrations
docker compose -f docker-compose.prod.yml exec backend flask db upgrade

# Initialiser les données de base
docker compose -f docker-compose.prod.yml exec backend python scripts/seed_database.py

# (Optionnel) Ajouter les données post-MVP
docker compose -f docker-compose.prod.yml exec backend python scripts/seed_all_post_mvp.py
```

---

## Étape 12 : Configuration du renouvellement SSL automatique

```bash
# Créer un script de renouvellement
cat > /opt/tedi/renew-ssl.sh << 'EOF'
#!/bin/bash
cd /opt/tedi
docker compose -f docker-compose.prod.yml run --rm certbot renew
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
EOF

chmod +x /opt/tedi/renew-ssl.sh

# Ajouter au crontab (renouvellement tous les jours à 3h du matin)
(crontab -l 2>/dev/null; echo "0 3 * * * /opt/tedi/renew-ssl.sh >> /var/log/ssl-renew.log 2>&1") | crontab -
```

---

## Étape 13 : Monitoring et maintenance

### 13.1 Script de sauvegarde automatique

```bash
cat > /opt/tedi/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/tedi/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Sauvegarde de la base de données
docker compose -f /opt/tedi/docker-compose.prod.yml exec -T postgres \
    pg_dump -U tedi_user tedi_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Supprimer les sauvegardes de plus de 7 jours
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/db_$DATE.sql.gz"
EOF

chmod +x /opt/tedi/backup.sh

# Ajouter au crontab (sauvegarde tous les jours à 2h du matin)
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/tedi/backup.sh >> /var/log/tedi-backup.log 2>&1") | crontab -
```

### 13.2 Commandes utiles

```bash
# Voir les logs en temps réel
docker compose -f docker-compose.prod.yml logs -f

# Voir les logs d'un service spécifique
docker compose -f docker-compose.prod.yml logs -f backend

# Redémarrer un service
docker compose -f docker-compose.prod.yml restart backend

# Redémarrer tous les services
docker compose -f docker-compose.prod.yml restart

# Arrêter tous les services
docker compose -f docker-compose.prod.yml down

# Mettre à jour l'application
cd /opt/tedi
git pull
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# Vérifier l'espace disque
df -h

# Nettoyer les images Docker non utilisées
docker system prune -af
```

---

## Étape 14 : Vérification du déploiement

```bash
# Tester l'API
curl https://tedi.bj/api/v1/public/stats

# Tester le frontend
curl -I https://tedi.bj

# Vérifier le certificat SSL
openssl s_client -connect tedi.bj:443 -servername tedi.bj < /dev/null 2>/dev/null | openssl x509 -noout -dates
```

---

## 🔧 Dépannage

### Problème : Les conteneurs ne démarrent pas

```bash
# Vérifier les logs
docker compose -f docker-compose.prod.yml logs

# Vérifier l'espace disque
df -h

# Vérifier la mémoire
free -m
```

### Problème : Erreur de base de données

```bash
# Vérifier la connexion à la base
docker compose -f docker-compose.prod.yml exec postgres psql -U tedi_user -d tedi_db -c "SELECT 1"

# Recréer la base de données (ATTENTION: perte de données)
docker compose -f docker-compose.prod.yml down -v
docker compose -f docker-compose.prod.yml up -d
```

### Problème : Certificat SSL expiré

```bash
# Forcer le renouvellement
docker compose -f docker-compose.prod.yml run --rm certbot renew --force-renewal
docker compose -f docker-compose.prod.yml restart nginx
```

### Problème : Rate limiting trop agressif

```bash
# Vider le cache Redis
docker compose -f docker-compose.prod.yml exec redis redis-cli FLUSHALL
```

---

## 📊 Résumé de l'architecture

```
                                    ┌─────────────────┐
                                    │   Internet      │
                                    └────────┬────────┘
                                             │
                                    ┌────────▼────────┐
                                    │  Nginx (80/443) │
                                    │  + SSL + Gzip   │
                                    └────────┬────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
           ┌────────▼────────┐      ┌────────▼────────┐      ┌────────▼────────┐
           │   Frontend      │      │    Backend      │      │  Static Files   │
           │   (Vue.js)      │      │    (Flask)      │      │   (Nginx)       │
           │   Port 80       │      │   Port 5000     │      │                 │
           └─────────────────┘      └────────┬────────┘      └─────────────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
           ┌────────▼────────┐      ┌────────▼────────┐      ┌────────▼────────┐
           │   PostgreSQL    │      │     Redis       │      │  Celery Worker  │
           │   + PostGIS     │      │     Cache       │      │  (Background)   │
           │   Port 5432     │      │   Port 6379     │      │                 │
           └─────────────────┘      └─────────────────┘      └─────────────────┘
```

---

## ✅ Checklist de déploiement

- [ ] Serveur Debian configuré
- [ ] Docker et Docker Compose installés
- [ ] Firewall configuré (ports 22, 80, 443)
- [ ] Code cloné dans /opt/tedi
- [ ] Fichier .env configuré avec mots de passe sécurisés
- [ ] Certificat SSL obtenu
- [ ] Tous les conteneurs en cours d'exécution
- [ ] Base de données initialisée
- [ ] Sauvegardes automatiques configurées
- [ ] Renouvellement SSL automatique configuré
- [ ] Tests de l'API et du frontend réussis

---

## 📞 Support

En cas de problème :
1. Consulter les logs : `docker compose -f docker-compose.prod.yml logs`
2. Vérifier le statut : `docker compose -f docker-compose.prod.yml ps`
3. Redémarrer les services : `docker compose -f docker-compose.prod.yml restart`

**Bonne chance avec votre déploiement ! 🎉**
