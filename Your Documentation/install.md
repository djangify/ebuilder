# eBuilder Installation Guide

Complete guide to deploying your self-hosted eBuilder store.

---

## Requirements

Before starting, ensure you have:

| Requirement | Minimum | Recommended |
|------------|---------|-------------|
| **VPS/Server** | 1 CPU, 1GB RAM | 2 CPU, 2GB RAM |
| **OS** | Ubuntu 22.04+ | Ubuntu 24.04 LTS |
| **Docker** | v24+ | Latest |
| **Docker Compose** | v2.20+ | Latest |
| **Domain** | Required | With SSL |
| **Stripe Account** | Required | Live mode for production |

**Recommended VPS providers:** Hetzner, DigitalOcean, Linode, Vultr

---

## Quick Start (5 minutes)

### 1. Upload Files

Upload the eBuilder folder to your server:

```bash
# Using scp from your local machine
scp -r ebuilder-selfhosted/ user@yourserver:/home/user/ebuilder
```

Or upload via SFTP using FileZilla, WinSCP, etc.

### 2. Configure Environment

```bash
cd /home/user/ebuilder
cp .env.example .env
nano .env
```

**Minimum required changes:**

```bash
SECRET_KEY=generate-a-long-random-string-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
STRIPE_PUBLIC_KEY=pk_live_xxx
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
```

Generate a secret key:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 3. Build and Start

```bash
docker compose build
docker compose up -d
```

### 4. Create Admin User

```bash
docker compose exec web python manage.py createsuperuser
```

### 5. Set Up Reverse Proxy

See [Reverse Proxy Setup](#reverse-proxy-setup) section below.

### 6. Access Your Store

- **Frontend:** https://yourdomain.com
- **Admin:** https://yourdomain.com/admin

---

## Detailed Installation

### Step 1: Prepare Your Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker (if not installed)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Log out and back in, then verify
docker --version
docker compose version
```

### Step 2: Create Directory Structure

```bash
mkdir -p /home/$USER/ebuilder
cd /home/$USER/ebuilder

# Create data directories
mkdir -p data/db data/media data/logs
```

### Step 3: Upload and Extract

Upload your eBuilder zip file, then:

```bash
unzip ebuilder-selfhosted-v1.0.zip
cd ebuilder-selfhosted
```

### Step 4: Configure Environment

```bash
cp .env.example .env
nano .env
```

See [ENV_REFERENCE.md](ENV_REFERENCE.md) for all available options.

### Step 5: Build Container

```bash
# First build
docker compose build

# Start in background
docker compose up -d

# Check it's running
docker compose ps
docker compose logs -f
```

### Step 6: Initial Setup

```bash
# Run migrations (usually automatic, but just in case)
docker compose exec web python manage.py migrate

# Create superuser
docker compose exec web python manage.py createsuperuser

# Collect static files (usually automatic)
docker compose exec web python manage.py collectstatic --no-input
```

---

## Reverse Proxy Setup

eBuilder runs on port 8000 by default. You need a reverse proxy for SSL.

### Option A: Caddy (Recommended - Easiest)

Create `/etc/caddy/Caddyfile`:

```
yourdomain.com {
    reverse_proxy localhost:8000
}
```

```bash
sudo systemctl reload caddy
```

Caddy automatically handles SSL certificates.

### Option B: Nginx

Create `/etc/nginx/sites-available/ebuilder`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    client_max_body_size 100M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/user/ebuilder/staticfiles/;
    }

    location /media/ {
        alias /home/user/ebuilder/data/media/;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/ebuilder /etc/nginx/sites-enabled/
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
sudo systemctl reload nginx
```

### Option C: HestiaCP/cPanel

If using a control panel, create a proxy domain pointing to `localhost:8000`.

---

## Post-Installation Setup

### 1. Configure Site Settings

1. Go to `/admin`
2. Navigate to **Pages → Site Settings**
3. Set:
   - Business name
   - Site URL (https://yourdomain.com)
   - Support email
   - Upload logo
   - Default currency

### 2. Set Up Stripe

See [STRIPE_SETUP.md](STRIPE_SETUP.md) for complete instructions.

### 3. Configure Email

Update `.env` with your SMTP settings:

```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=app-specific-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

Restart after changes:
```bash
docker compose restart
```

### 4. Create Content

1. **Products:** Admin → Shop → Products
2. **Blog posts:** Admin → Blog → Posts
3. **Pages:** Admin → Pages → Pages
4. **Info pages:** Admin → Info Pages (for Terms, Privacy, etc.)

---

## Updating eBuilder

When a new version is released:

```bash
cd /home/user/ebuilder

# Backup first!
docker compose exec web python manage.py dumpdata > backup-$(date +%Y%m%d).json
tar -czf media-backup-$(date +%Y%m%d).tar.gz data/media/

# Stop container
docker compose down

# Replace files (keep your .env and data folder!)
# Upload new version...

# Rebuild and start
docker compose build --no-cache
docker compose up -d

# Run any new migrations
docker compose exec web python manage.py migrate
```

---

## Backup and Restore

### Automated Daily Backup

Create `/home/user/backup-ebuilder.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/user/backups"
DATE=$(date +%Y%m%d)

mkdir -p $BACKUP_DIR

# Database
docker compose -f /home/user/ebuilder/docker-compose.yml exec -T web \
    python manage.py dumpdata > $BACKUP_DIR/db-$DATE.json

# Media files
tar -czf $BACKUP_DIR/media-$DATE.tar.gz /home/user/ebuilder/data/media/

# Keep only last 7 days
find $BACKUP_DIR -mtime +7 -delete
```

Add to crontab:
```bash
crontab -e
# Add line:
0 3 * * * /home/user/backup-ebuilder.sh
```

### Restore from Backup

```bash
# Database
docker compose exec web python manage.py loaddata backup.json

# Media
tar -xzf media-backup.tar.gz -C /
```

---

## Troubleshooting

### Container won't start

```bash
# Check logs
docker compose logs -f

# Common fixes
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Static files not loading

```bash
docker compose exec web python manage.py collectstatic --no-input
docker compose restart
```

### Permission errors on media files

```bash
sudo chown -R 1000:1000 data/
```

### Database locked errors

SQLite can lock under heavy load. For high-traffic sites, consider PostgreSQL.

### Can't access admin

```bash
# Reset password
docker compose exec web python manage.py changepassword admin
```

---

## Getting Help

- **Documentation:** Check the `docs/` folder
- **Issues:** Search existing issues first
- **Contact:** djangify@djangify.com

**Note:** This is a self-hosted product. Support is limited to documentation and bug fixes. Custom modifications and server setup assistance are not included.

---

## Next Steps

1. [Set up Stripe payments](STRIPE_SETUP.md)
2. [Customise your store](CUSTOMISATION.md)
3. [Environment variables reference](ENV_REFERENCE.md)