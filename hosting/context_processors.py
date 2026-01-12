"""
Context processors for the hosting app.

Provides variables that need to be available in all hosting templates.
"""

from django.contrib.sites.models import Site


def current_site(request):
    """
    Add the current site to the template context.

    This makes {{ site }} and {{ site.name }} available in all templates
    that use this context processor.
    """
    try:
        site = Site.objects.get_current(request)
        return {"site": site}
    except Site.DoesNotExist:
        # Return empty dict to avoid breaking templates
        return {"site": None}
