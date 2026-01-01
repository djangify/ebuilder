# ebuilder/sitemaps.py

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from blog.models import Post, Category as BlogCategory
from shop.models import Product, Category as ShopCategory
from pages.models import Page
from infopages.models import InfoPage


class StaticSitemap(Sitemap):
    """Static/core pages that don't come from models."""

    priority = 0.9
    changefreq = "weekly"

    def items(self):
        return [
            "pages:home",
            "pages:about",
            "pages:gallery",
            "shop:product_list",
            "shop:category_hub",
            "blog:list",
            "infopages:docs_index",
            "infopages:policy_index",
        ]

    def location(self, item):
        return reverse(item)


class PagesSitemap(Sitemap):
    """Dynamic custom pages created in admin."""

    changefreq = "monthly"
    priority = 0.7

    def items(self):
        # Only custom pages, exclude home/about/gallery (they're in StaticSitemap)
        return Page.objects.filter(published=True, template="custom")

    def lastmod(self, obj):
        return obj.updated


class BlogSitemap(Sitemap):
    """Published blog posts."""

    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Post.objects.filter(status="published")

    def lastmod(self, obj):
        return obj.updated if hasattr(obj, "updated") else obj.created


class BlogCategorySitemap(Sitemap):
    """Blog category listing pages."""

    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return BlogCategory.objects.all()


class ProductSitemap(Sitemap):
    """Active products in shop."""

    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Product.objects.filter(is_active=True, status="publish")

    def lastmod(self, obj):
        return obj.updated if hasattr(obj, "updated") else None


class ShopCategorySitemap(Sitemap):
    """Shop category listing pages."""

    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return ShopCategory.objects.all()


class InfoPageSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return InfoPage.objects.filter(published=True)

    def lastmod(self, obj):
        return obj.last_updated


# Register all sitemaps
sitemaps = {
    "static": StaticSitemap,
    "pages": PagesSitemap,
    "blog": BlogSitemap,
    "blog_categories": BlogCategorySitemap,
    "products": ProductSitemap,
    "shop_categories": ShopCategorySitemap,
    "infopages": InfoPageSitemap,
}
