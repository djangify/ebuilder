# pages/views.py

from django.shortcuts import render, get_object_or_404
from .models import Page, SiteSettings, HeroBanner, FAQBlock, GalleryImage, Hero
from blog.models import Post
from shop.models import Product


def _render_page(request, template_name):
    """Helper to render a page by template name with all content blocks."""
    page = get_object_or_404(Page, template=template_name, published=True)

    sections = list(page.sections.filter(published=True))
    three_columns = list(page.three_columns.filter(published=True))
    galleries = list(page.galleries.filter(published=True))
    faq_blocks = list(page.faqs.filter(published=True))

    content_blocks = sorted(
        sections + three_columns + galleries + faq_blocks,
        key=lambda x: x.order,
    )

    return render(
        request,
        f"pages/{template_name}.html",
        {
            "page": page,
            "sections": sections,  # Keep for backwards compatibility
            "content_blocks": content_blocks,
        },
    )


def home_view(request):
    """
    Render the homepage with all content blocks.
    Uses SiteSettings for configuration.
    """
    settings_obj = SiteSettings.objects.first()
    if not settings_obj:
        # Create default settings if none exist
        settings_obj = SiteSettings.objects.create()

    page = get_object_or_404(Page, template="home", published=True)

    # Collect all content blocks
    sections = list(page.sections.filter(published=True))
    three_columns = list(page.three_columns.filter(published=True))
    galleries = list(page.galleries.filter(published=True))

    content_blocks = sorted(
        sections + three_columns + galleries,
        key=lambda block: block.order,
    )

    # Optional blog posts
    blog_posts = None
    if settings_obj.show_blog_on_homepage:
        blog_posts = Post.objects.filter(status="published").order_by("-publish_date")[
            :3
        ]

    # Optional featured products
    featured_products = None
    if settings_obj.show_shop_on_homepage:
        featured_products = Product.objects.filter(
            is_active=True,
            status="publish",
            featured=True,
        ).order_by("order", "-created")[:4]

    context = {
        "page": page,
        "content_blocks": content_blocks,
        "hero": Hero.objects.filter(is_active=True).first(),
        "hero_banner": HeroBanner.objects.filter(is_active=True).first(),
        "blog_posts": blog_posts,
        "featured_products": featured_products,
    }

    return render(request, "pages/home.html", context)


def about_view(request):
    """Render the about page."""
    page = get_object_or_404(Page, template="about", published=True)

    sections = list(page.sections.filter(published=True))
    three_columns = list(page.three_columns.filter(published=True))
    galleries = list(page.galleries.filter(published=True))

    content_blocks = sorted(
        sections + three_columns + galleries,
        key=lambda block: block.order,
    )

    context = {
        "page": page,
        "content_blocks": content_blocks,
    }

    return render(request, "pages/about.html", context)


def gallery_view(request):
    """Render the gallery page."""
    page = get_object_or_404(Page, template="gallery", published=True)

    sections = list(page.sections.filter(published=True))
    three_columns = list(page.three_columns.filter(published=True))
    galleries = list(page.galleries.filter(published=True))

    content_blocks = sorted(
        sections + three_columns + galleries,
        key=lambda block: block.order,
    )

    context = {
        "page": page,
        "content_blocks": content_blocks,
    }

    return render(request, "pages/gallery.html", context)


def detail_view(request, slug):
    """Render a custom page by slug."""
    page = get_object_or_404(Page, slug=slug, published=True)

    # Redirect to proper view if not a custom page
    if page.template == "home":
        from django.shortcuts import redirect

        return redirect("pages:home")
    elif page.template == "about":
        from django.shortcuts import redirect

        return redirect("pages:about")
    elif page.template == "gallery":
        from django.shortcuts import redirect

        return redirect("pages:gallery")

    sections = list(page.sections.filter(published=True))
    three_columns = list(page.three_columns.filter(published=True))
    galleries = list(page.galleries.filter(published=True))
    faq_blocks = page.faqs.filter(published=True)

    content_blocks = sorted(
        list(sections) + list(three_columns) + list(galleries) + list(faq_blocks),
        key=lambda x: x.order,
    )

    context = {
        "page": page,
        "content_blocks": content_blocks,
    }

    return render(request, "pages/custom.html", context)


def gallery_image_modal(request, pk):
    """HTMX endpoint for gallery image modal."""
    image = get_object_or_404(GalleryImage, pk=pk)
    return render(request, "pages/partials/gallery_modal.html", {"image": image})
