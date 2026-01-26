# Customization Guide

How to personalize your eCommerce store.

---

## Quick Customizations (No Code)

These changes are made through the Django admin panel.

### Site Settings

1. Go to `/admin`
2. Navigate to **Pages → Site Settings**
3. Configure:
   - **Business Name** - Appears in header, emails, invoices
   - **Site URL** - Your full domain with https://
   - **Support Email** - Where customer queries go
   - **Logo** - Upload your logo image
   - **Favicon** - Upload a favicon (.ico or .png)
   - **Default Currency** - GBP, USD, EUR, etc.
   - **SEO Description** - Default meta description

### Homepage Layout

1. Go to **Pages → Pages**
2. Edit the page marked as homepage
3. Configure which sections display:
   - Hero section
   - Featured products
   - Latest blog posts
   - Testimonials

---

## Branding: Remove Footer Attribution

Remove footer atrribution from templates/includes/footer.html

---

## Colour Customization

The eCommerce builder uses Tailwind CSS with CSS custom properties for theming.

### Method 1: CSS Variables (Easiest)

Edit `static/css/custom.css` (create if doesn't exist):

```css
:root {
    /* Primary brand colour */
    --color-primary: #4f46e5;
    --color-primary-hover: #4338ca;
    
    /* Secondary colour */
    --color-secondary: #0ea5e9;
    
    /* Accent colour */
    --color-accent: #f59e0b;
    
    /* Text colours */
    --color-text: #1f2937;
    --color-text-light: #6b7280;
    
    /* Background */
    --color-background: #ffffff;
    --color-background-alt: #f9fafb;
}
```


Then rebuild CSS:
```bash
npm run build
docker compose restart
```

---

## Logo and Images

### Logo

1. Upload via Admin → Pages → Site Settings → Logo
2. Or replace `static/images/logo.png`
3. Recommended size: 200x50px (or your preference)

### Favicon

1. Upload via Admin → Site Settings → Favicon
2. Or replace `static/favicon.ico`
3. Recommended: 32x32px .ico or .png

### Default OG Image

For social media sharing:

1. Create image: 1200x630px
2. Save as `static/images/default-og-image.jpg`
3. Update in Site Settings if needed

---

## Template Customization

### Template Location

All templates are in the `templates/` folder:

```
templates/
├── base.html              # Main layout
├── home.html              # Homepage
├── shop/
│   ├── product_list.html  # Product listing
│   ├── product_detail.html # Single product
│   └── cart.html          # Shopping cart
├── blog/
│   ├── post_list.html     # Blog listing
│   └── post_detail.html   # Single post
├── accounts/
│   ├── login.html
│   └── dashboard.html
└── includes/
    ├── header.html
    ├── footer.html
    └── navigation.html
```

### Safe Edits

These are safe to modify without breaking functionality:

- `templates/includes/header.html` - Header layout
- `templates/includes/footer.html` - Footer content
- `templates/includes/navigation.html` - Menu structure
- Any HTML structure and styling
- Adding new sections to pages

### Careful With

- Template tags `{% %}` - Breaking these breaks the site
- Context variables `{{ }}` - These display dynamic data
- Block tags `{% block %}{% endblock %}` - Template inheritance

### Example: Custom Header

Edit `templates/includes/header.html`:

```django
<header class="bg-white shadow-sm">
    <div class="container mx-auto px-4 py-4">
        <div class="flex items-center justify-between">
            <!-- Logo -->
            <a href="{% url 'pages:home' %}" class="flex items-center">
                {% if site_settings.logo %}
                    <img src="{{ site_settings.logo.url }}" alt="{{ site_settings.business_name }}" class="h-10">
                {% else %}
                    <span class="text-2xl font-bold text-primary-600">
                        {{ site_settings.business_name|default:"My Store" }}
                    </span>
                {% endif %}
            </a>
            
            <!-- Your custom navigation here -->
            <nav class="hidden md:flex space-x-6">
                <a href="{% url 'shop:product_list' %}">Shop</a>
                <a href="{% url 'blog:post_list' %}">Blog</a>
                <a href="{% url 'pages:page_detail' 'about' %}">About</a>
            </nav>
        </div>
    </div>
</header>
```

---

## Adding Custom Pages

### Via Admin (Recommended)

1. Go to **Pages → Pages**
2. Click **Add Page**
3. Set title, slug, content
4. Use the page builder blocks for layout

### Via Code

Create `templates/pages/custom_page.html`:

```django
{% extends "base.html" %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold">Your Custom Page</h1>
    <!-- Your content here -->
</div>
{% endblock %}
```

Add to `pages/urls.py`:
```python
path('your-page/', views.your_view, name='your_page'),
```

---

## Custom CSS

### Add Custom Stylesheet

1. Create `static/css/custom.css`
2. Add to `templates/base.html` before `</head>`:

```django
<link rel="stylesheet" href="{% static 'css/custom.css' %}">
```

### Override Existing Styles

```css
/* Custom button style */
.btn-primary {
    background-color: #your-brand-color;
}

/* Custom header background */
header {
    background: linear-gradient(to right, #color1, #color2);
}

/* Custom footer */
footer {
    background-color: #1a1a1a;
    color: #ffffff;
}
```

---

## Custom JavaScript

### Add Custom Script

1. Create `static/js/custom.js`
2. Add to `templates/base.html` before `</body>`:

```django
<script src="{% static 'js/custom.js' %}"></script>
```

---

## Email Templates

Customise transactional emails in `templates/emails/`:

- `order_confirmation.html` - Sent after purchase
- `download_ready.html` - Download link email
- `password_reset.html` - Password reset

---

## After Making Changes

### Template Changes

No rebuild needed - just refresh the page.

### Static File Changes (CSS/JS)

```bash
docker compose exec web python manage.py collectstatic --no-input
```

Then hard refresh browser (Ctrl+F5).

### Python Code Changes

```bash
docker compose restart
```

---

## Important Notes

1. **Backup before editing** - Keep copies of files you modify
2. **Test thoroughly** - Check all pages after changes
3. **Mobile responsive** - Test on mobile devices
4. **Don't edit core files** - Extend or override instead
5. **Document your changes** - For future updates

---

## Getting Help

If you break something:

1. Restore from backup
2. Check git diff if using version control
3. Review Django template documentation
4. Check browser console for JavaScript errors