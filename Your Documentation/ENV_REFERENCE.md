# Environment Variables Reference

Complete reference for all eBuilder environment variables.

---

## Required Variables

These must be set for eBuilder to function:

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key (50+ chars) | `abc123...` |
| `ALLOWED_HOSTS` | Comma-separated domains | `example.com,www.example.com` |
| `STRIPE_PUBLIC_KEY` | Stripe publishable key | `pk_live_...` |
| `STRIPE_SECRET_KEY` | Stripe secret key | `sk_live_...` |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing | `whsec_...` |

---

## All Variables

### Django Core

```bash
# REQUIRED: Generate with: python -c "import secrets; print(secrets.token_urlsafe(50))"
SECRET_KEY=your-long-random-secret-key

# REQUIRED: Your domain(s), comma-separated
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Development only - never True in production
DEBUG=False
```

### Security

```bash
# REQUIRED for HTTPS: Must include https://
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Optional: CORS settings for API access
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

### Database

```bash
# Default: SQLite (recommended for most users)
# No configuration needed - uses /app/db/db.sqlite3

# Optional: PostgreSQL (for high-traffic sites)
DATABASE_URL=postgresql://user:password@localhost:5432/ebuilder
```

### Stripe Payments

```bash
# REQUIRED: Get from Stripe Dashboard → Developers → API Keys
STRIPE_PUBLIC_KEY=pk_live_xxxxxxxxxxxxx
STRIPE_SECRET_KEY=sk_live_xxxxxxxxxxxxx

# REQUIRED: Get from Stripe Dashboard → Developers → Webhooks
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
```

### Email

```bash
# Recommended for order confirmations, password resets
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

**Gmail users:** Use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.

### Branding

```bash
# Set to False to remove "Powered by eBuilder" footer
SHOW_EBUILDER_BRANDING=True
```

---

## Example .env File

```bash
# =================================================================
# eBuilder Configuration
# =================================================================

# Django
SECRET_KEY=Xt7k9Lm2nPq4rS6uV8wY1zA3bC5dE7fG9hI0jK2lM4nO6pQ8rS0t
DEBUG=False
ALLOWED_HOSTS=mystore.com,www.mystore.com
CSRF_TRUSTED_ORIGINS=https://mystore.com,https://www.mystore.com

# Stripe
STRIPE_PUBLIC_KEY=pk_live_51ABC123DEF456
STRIPE_SECRET_KEY=sk_live_51ABC123DEF456
STRIPE_WEBHOOK_SECRET=whsec_ABC123DEF456

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=mystore@gmail.com
EMAIL_HOST_PASSWORD=abcd-efgh-ijkl-mnop
DEFAULT_FROM_EMAIL=orders@mystore.com

# Branding
SHOW_EBUILDER_BRANDING=False
```

---

## Generating a Secret Key

### Option 1: Python

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

### Option 2: OpenSSL

```bash
openssl rand -base64 50
```

### Option 3: Online

Use a password generator with 50+ characters, letters, numbers, symbols.

---

## Environment-Specific Configs

### Development

```bash
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

### Production

```bash
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
```

---

## Applying Changes

After editing `.env`:

```bash
docker compose restart
```

Or for a full rebuild (if changing system settings):

```bash
docker compose down
docker compose up -d
```

---

## Troubleshooting

### "Invalid HTTP_HOST header"

Your domain isn't in ALLOWED_HOSTS:
```bash
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### "CSRF verification failed"

Add https:// to CSRF_TRUSTED_ORIGINS:
```bash
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
```

### Stripe payments failing

1. Check you're using live keys (not test keys) for production
2. Verify webhook secret matches your Stripe dashboard
3. Check webhook URL is accessible: `https://yourdomain.com/shop/stripe/webhook/`

### Emails not sending

1. Check EMAIL_HOST_PASSWORD is correct
2. Gmail requires App Password, not regular password
3. Test with: `docker compose exec web python manage.py sendtestemail your@email.com`