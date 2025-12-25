from django import template
from pages.models import PageSection, ThreeColumnBlock

register = template.Library()


@register.filter
def is_pagesection(obj):
    return isinstance(obj, PageSection)


@register.filter
def is_threecolumn(obj):
    return isinstance(obj, ThreeColumnBlock)
