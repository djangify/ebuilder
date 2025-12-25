from django import template
import re

register = template.Library()


@register.filter
def youtube_id(url):
    """Extract YouTube video ID from URL."""
    if not url:
        return ""
    patterns = [
        r"(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return ""
