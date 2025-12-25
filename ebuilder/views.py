# ebuilder/views.py

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.views.decorators.http import require_GET
from django.utils import timezone


@require_GET
def robots_txt(request):
    """Robots.txt for search + AI visibility."""
    site_url = request.build_absolute_uri("/").rstrip("/")
    sitemap_url = f"{site_url}/sitemap.xml"

    lines = [
        "# robots.txt for djangify.com",
        "# Enables modern search and AI engines to crawl public sections.",
        "",
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /accounts/",
        "Disallow: /media/private/",
        "Disallow: /checkout/",
        "",
        "# AI & Answer Engine Bots",
        "User-agent: GPTBot",
        "User-agent: ChatGPT-User",
        "User-agent: Google-Extended",
        "User-agent: ClaudeBot",
        "User-agent: PerplexityBot",
        "User-agent: anthropic-ai",
        "User-agent: Bingbot",
        "Allow: /",
        "",
        f"Sitemap: {sitemap_url}",
        "",
        "# --- Brand Context ---",
        "# djangify.com - micro-saas ecommerce builder",
        "# It demonstrates best practices in ecommerce,offline-first,AI-search-ready design and ethical tech visibility.",
    ]

    return HttpResponse("\n".join(lines), content_type="text/plain")


def handler404(request, exception):
    """Custom 404 error handler with blog post suggestions."""
    from blog.models import Post, Category

    category_slug = "reflections"

    try:
        category = get_object_or_404(Category, slug=category_slug)
        category_posts = Post.objects.filter(
            category=category, status="published", publish_date__lte=timezone.now()
        ).order_by("-publish_date")[:4]
    except Http404:
        category_posts = Post.objects.filter(
            status="published", publish_date__lte=timezone.now()
        ).order_by("-publish_date")[:6]
        category = None

    context = {"category_posts": category_posts, "selected_category": category}
    return render(request, "error/404.html", context, status=404)


def handler403(request, exception):
    """Custom 403 error handler."""
    return render(request, "error/403.html", status=403)


def handler500(request):
    """Custom 500 error handler."""
    return render(request, "error/500.html", status=500)


def health(request):
    return HttpResponse("ok")
