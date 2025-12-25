from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from bs4 import BeautifulSoup
from .models import InfoPage, Category
from django.views.generic import TemplateView


class DocListView(TemplateView):
    template_name = "infopages/docs_index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        categories = Category.objects.prefetch_related("pages")

        categories_with_counts = []
        for category in categories:
            docs_qs = category.pages.filter(page_type="doc", published=True).order_by(
                "title"
            )

            categories_with_counts.append(
                {
                    "category": category,
                    "doc_count": docs_qs.count(),
                    "docs": list(docs_qs[:7]),
                }
            )

        context["categories_with_counts"] = categories_with_counts

        context["pages"] = (
            InfoPage.objects.filter(page_type="doc", published=True)
            .select_related("category")
            .order_by("title")
        )

        return context


class CategoryDetailView(ListView):
    """Shows all doc pages within a specific category."""

    model = InfoPage
    template_name = "infopages/category_detail.html"
    context_object_name = "pages"

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs["slug"])
        return InfoPage.objects.filter(
            category=self.category, page_type="doc", published=True
        ).order_by("title")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class PolicyListView(ListView):
    model = InfoPage
    template_name = "infopages/policy_index.html"
    context_object_name = "pages"

    def get_queryset(self):
        return InfoPage.objects.filter(page_type="policy", published=True)


class InfoPageDetailView(DetailView):
    model = InfoPage
    template_name = "infopages/detail.html"
    context_object_name = "page"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # --- Build Table of Contents ---
        soup = BeautifulSoup(self.object.content or "", "html.parser")
        toc = []
        for heading in soup.find_all(["h2", "h3"]):
            text = heading.get_text(strip=True)
            if not text:
                continue
            if "id" not in heading.attrs:
                heading["id"] = text.lower().replace(" ", "-").replace(".", "")
            toc.append({"title": text, "id": heading["id"]})

        context["toc"] = toc
        context["rendered_content"] = str(soup)

        # --- Related Pages Logic ---
        page = self.object
        if page.category:
            related_pages = (
                InfoPage.objects.filter(
                    category=page.category, page_type=page.page_type, published=True
                )
                .exclude(id=page.id)
                .order_by("title")[:5]
            )
        else:
            related_pages = (
                InfoPage.objects.filter(page_type=page.page_type, published=True)
                .exclude(id=page.id)
                .order_by("title")[:5]
            )

        context["related_pages"] = related_pages
        return context
