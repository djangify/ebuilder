from django import template
from content.models import ThreeColumnBlock, FAQBlock, SectionBlock

register = template.Library()


@register.filter
def is_pagesection(obj):
    return isinstance(obj, SectionBlock)


@register.filter
def is_threecolumn(obj):
    return isinstance(obj, ThreeColumnBlock)


@register.filter
def is_faqblock(obj):
    return isinstance(obj, FAQBlock)
