# ebuilder/sitemaps.py

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from blog.models import Post
from shop.models import Product, Category as ShopCategory


class StaticSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            "pages:home",
            "ai_search",
            "independent_software",
        ]

    def location(self, item):
        return reverse(item)


class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Post.objects.filter(status="published")

    def lastmod(self, obj):
        return obj.updated if hasattr(obj, "updated") else obj.created


class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Product.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated if hasattr(obj, "updated") else None


class ShopCategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return ShopCategory.objects.all()


sitemaps = {
    "static": StaticSitemap,
    "blog": BlogSitemap,
    "products": ProductSitemap,
    "shop_categories": ShopCategorySitemap,
}
