# eBuilder - Self-Hosted eCommerce Platform

![eBuilder eCommerce Platform](https://github.com/djangify/ebuilder/blob/de5c5bdf79ca79e21384fd12d863a849fe124da5/open-source-ecommerce-builder.png)

<p align="center">
  <a href="https://www.djangoproject.com/">
    <img src="https://img.shields.io/badge/Django_5.2-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django 5.2">
  </a>
  <a href="https://tailwindcss.com/">
    <img src="https://img.shields.io/badge/Tailwind_CSS_4-06B6D4?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS">
  </a>
  <a href="https://www.docker.com/">
    <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  </a>
  <a href="https://stripe.com/">
    <img src="https://img.shields.io/badge/Stripe-008CDD?style=for-the-badge&logo=stripe&logoColor=white" alt="Stripe">
  </a>
</p>

**A Docker-first, self-hosted eCommerce platform for digital downloads.** Built for creators who want ownership, simplicity, and no SaaS lock-in.

---

## 🎯 What is eBuilder?

eBuilder is a complete digital product shop with integrated content management, designed for the self-hosting community. It's not a page builder - it's a fully-functional eCommerce system that you own and control.

**Perfect for:**
- Digital product creators
- Course sellers
- Template designers
- Asset creators
- Anyone selling downloadable products

---

## ✨ Features

### 🛒 **Complete Shop System**
- Digital product management - limit downloads per product
- Category organization
- Product reviews and ratings
- Wishlist functionality
- Stripe checkout integration
- Customer dashboard with order history
- Secure download delivery

### 📝 **Content Management**
- **Blog** - Full blogging system with categories, featured posts, and YouTube embeds
- **Custom Pages** - Create any page structure (About, Gallery, Contact, etc.)
- **InfoPages** - Documentation and policy pages with category organization
- **Dynamic Homepage** - Choose between shop-focused or content-focused layouts

### 🎨 **Design & UI**
- Fully responsive mobile-first design
- Tailwind CSS 4 with CSS variables for easy theming
- Adminita Django admin theme for beautiful backend
- Dark mode compatible admin interface
- Accessible (ARIA compliant)

### 🔍 **SEO & Discovery**
- **NEW:** Complete Schema.org structured data
  - Product schema with pricing and reviews
  - Article schema for blog posts
  - ItemList schema for listing pages
  - Organization schema for brand identity
- **NEW:** Open Graph tags for social sharing
- **NEW:** Twitter Card integration
- AI Search ready with page-type metadata
- Automatic sitemap generation
- Robots.txt with AI bot support
- Canonical URLs on all pages

### ⚙️ **Technical Features**
- Docker-first distribution
- SQLite by default (with WAL mode for performance)
- Optional PostgreSQL support
- File-based media storage (no S3 required)
- Automatic thumbnail generation
- django-allauth for authentication
- HTMX for dynamic interactions
- Alpine.js for lightweight JavaScript

---

## 🚀 Quick Start

### **Prerequisites**
- Docker & Docker Compose
- 512MB RAM minimum
- Any Linux VPS (Ubuntu recommended)

### **Installation (2 minutes)**

```bash
# 1. Clone the repository
git clone https://github.com/djangify/ebuilder.git
cd ebuilder

# 2. Copy environment file
cp .env.example .env

# 3. Edit .env with your settings
nano .env  # Set SECRET_KEY, STRIPE_KEYS, etc.

# 4. Start the containers
docker compose up -d

# 5. Create admin user
docker compose exec web python manage.py createsuperuser

# 6. Visit your site
open http://localhost:8000
```

**That's it!** Your shop is running.

---

## Creating Your Admin Account

After starting the container, create your superuser with this command:

```bash
docker compose exec web python manage.py createsuperuser_verified
```

This creates an admin account AND automatically verifies the email address so you can log in immediately.

You'll be prompted for:
- Email address
- Password (minimum 8 characters)

Once complete, log in at `https://yourdomain.com/admin/`

### Why not the standard createsuperuser?

The standard Django `createsuperuser` command doesn't verify the email address. Since eBuilder uses django-allauth with mandatory email verification, you wouldn't be able to log in without the extra verification step.

The `createsuperuser_verified` command handles both steps automatically.

### Manual Verification (Alternative)

If you used the standard `createsuperuser` command, you can verify the email manually:

```bash
docker compose exec web python manage.py shell
```

Then run:

```python
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(email="your-email@example.com")
EmailAddress.objects.create(
    user=user,
    email=user.email,
    verified=True,
    primary=True
)
exit()
```
---

## 📋 First Steps After Installation



### 1. **Configure Site Settings**
Visit `/admin` and go to **Pages → Site Settings**:
- Set your business name
- Add your site URL
- Configure support email
- Upload your logo
- Set default SEO metadata

### 2. **Create Your First Product**
Go to **Shop → Products**:
- Add product title and description
- Upload product image and files
- Set price
- Publish when ready

### 3. **Customize Homepage**
Go to **Pages → Pages**:
- Edit the "Homepage" entry
- Add hero sections
- Configure which content shows (products, blog, gallery)

### 4. **Add SEO Images**
Create a default Open Graph image:
- Size: 1200x630px
- Save as: `static/images/default-og-image.jpg`
- See `templates/includes/seo/OG_IMAGE_GUIDE.md` for details

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | Django 5.2 LTS |
| **Frontend** | Tailwind CSS 4, Alpine.js, HTMX |
| **Database** | SQLite (default) / PostgreSQL (optional) |
| **Payments** | Stripe |
| **Authentication** | django-allauth |
| **Rich Text** | Trix Editor |
| **Admin Theme** | Adminita |
| **Container** | Docker + Gunicorn + Caddy |
| **Storage** | Local filesystem (media/) |

---

## 📁 Project Structure

```
ebuilder/
├── docker-compose.yml       # Container orchestration
├── Dockerfile              # Application container
├── requirements.txt        # Python dependencies
├── manage.py              # Django management
├── ebuilder/              # Project settings
│   ├── settings.py        # Main configuration
│   ├── urls.py           # URL routing
│   └── sitemaps.py       # SEO sitemap
├── accounts/             # User authentication
├── blog/                 # Blog system
├── shop/                 # Product & cart system
├── pages/                # Dynamic page builder
├── infopages/            # Documentation/policies
├── templates/            # HTML templates
│   └── includes/seo/    # SEO includes (NEW)
├── static/              # CSS, JS, images
└── data/               # Persistent data
    ├── media/          # Uploaded files
    └── db/            # SQLite database
```

---

## 🔐 Environment Variables

Required `.env` settings:

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (optional - defaults to SQLite)
# DATABASE_URL=postgresql://user:pass@db:5432/ebuilder

# Stripe
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email (optional)
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your@email.com
EMAIL_HOST_PASSWORD=your-password


```

---

## 🔄 Updating to Latest Version

```bash
# Pull latest code
git pull origin main

# Rebuild containers
docker compose build

# Apply migrations
docker compose exec web python manage.py migrate

# Restart
docker compose restart
```

---

## 💾 Backup & Restore

### **Backup**
```bash
# Backup database
docker compose exec web python manage.py dumpdata > backup.json

# Backup media files
tar -czf media-backup.tar.gz data/media/
```

### **Restore**
```bash
# Restore database
docker compose exec web python manage.py loaddata backup.json

# Restore media
tar -xzf media-backup.tar.gz
```

---

## 🐘 PostgreSQL (Optional)

To use PostgreSQL instead of SQLite:

1. **Uncomment PostgreSQL service** in `docker-compose.yml`
2. **Add to .env:**
   ```bash
   DATABASE_URL=postgresql://ebuilder:ebuilder@db:5432/ebuilder
   ```
3. **Restart:**
   ```bash
   docker compose down
   docker compose up -d
   docker compose exec web python manage.py migrate
   ```

---

## 🎨 Customization

### **Changing Colors**
Edit `static/css/base.css`:
```css
:root {
  --color-primary: #1e3a8a;
  --color-secondary: #3b82f6;
  --color-accent: #60a5fa;
}
```

### **Custom Templates**
Templates are in `templates/`:
- Shop: `shop/templates/`
- Blog: `blog/templates/`
- Pages: `pages/templates/`

### **Adding Features**
Create new Django apps in `ebuilder/`:
```bash
docker compose exec web python manage.py startapp myapp
```

---

## 📊 SEO Configuration

eBuilder includes comprehensive SEO tools:

### **Schema.org Structured Data**
Reusable includes in `templates/includes/seo/`:
- `og_meta.html` - Open Graph & Twitter Cards
- `schema_product.html` - Product rich snippets
- `schema_article.html` - Blog post markup
- `schema_itemlist.html` - Listing pages
- `schema_webpage.html` - Generic pages
- `schema_organization.html` - Site-wide org data

**Usage:**
```django
{% include "includes/seo/og_meta.html" with og_type="product" %}
{% include "includes/seo/schema_product.html" with product=product %}
```

See `templates/includes/seo/README.md` for complete documentation.

---

## 🧪 Testing

### **Run Tests**
```bash
docker compose exec web python manage.py test
```

### **Check Migrations**
```bash
docker compose exec web python manage.py makemigrations --check
```

### **Validate SEO**
- [Google Rich Results Test](https://search.google.com/test/rich-results)
- [Facebook Sharing Debugger](https://developers.facebook.com/tools/debug/)
- [Twitter Card Validator](https://cards-dev.twitter.com/validator)

---

## ❓ Common Issues

### **Port 8000 already in use?**
Edit `docker-compose.yml` and change `8000:8000` to `8001:8000`

### **Permission errors on media files?**
```bash
sudo chown -R 1000:1000 data/
```

### **Static files not loading?**
```bash
docker compose exec web python manage.py collectstatic --no-input
```

### **Admin styling broken?**
Make sure Adminita is installed:
```bash
docker compose exec web pip list | grep adminita
```

---

## 🚫 What eBuilder Is NOT

- ❌ **Not for shared hosting** - Requires Docker/VPS
- ❌ **Not a page builder** - It's an eCommerce system with CMS
- ❌ **Not for physical products** - Digital downloads only (v1)
- ❌ **Not a SaaS** - You host and own everything
- ❌ **Not a marketplace** - Single-vendor store

---

## 🗺️ Roadmap

### **v1.0 (Current)**
- ✅ Docker-first distribution
- ✅ Complete digital product shop
- ✅ Blog & content system
- ✅ Stripe integration
- ✅ Full SEO implementation
- ✅ Mobile responsive

### **Future Considerations**
- [ ] Multi-currency support
- [ ] Subscription products
- [ ] Newsletter integration
- [ ] Advanced analytics
- [ ] Plugin system
- [ ] Managed hosting service

---

## 📜 License

eBuilder is open source software released under the MIT License.

You are free to use, modify, and self-host it. See LICENSE file for details.

**Footer Branding:** The "Powered by eBuilder" footer appears by default and can be removed with a license key. This supports ongoing development while keeping the core platform free.

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📞 Support & Contact

- **Documentation:** See `templates/includes/seo/` for SEO guides
- **Issues:** [GitHub Issues](https://github.com/djangify/ebuilder/issues)
- **Creator:** [Diane Corriette](https://www.todiane.com)
- **LinkedIn:** [@todianedev](https://www.linkedin.com/in/todianedev)

---

## 🙏 Credits

Built with:
- [Django](https://www.djangoproject.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Stripe](https://stripe.com/)
- [Adminita](https://github.com/djangify/adminita)
- [Alpine.js](https://alpinejs.dev/)
- [HTMX](https://htmx.org/)

---


*Own your store. Own your data. Own your future.*


**Coffee Always Welcome**: https://ko-fi.com/todianedev ❤️


Maintained by [Diane Corriette](https://github.com/todiane)