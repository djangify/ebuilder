# pages/widgets.py
from django import forms


class TrixWidget(forms.Textarea):
    """
    Custom textarea widget that loads Trix editor.
    Uses Django's Media class to inject CSS/JS only on pages that need it.
    """

    class Media:
        css = {
            "all": (
                "admin/css/trix.css",
                "admin/css/trix-admin.css",
            )
        }
        js = (
            "admin/js/trix.umd.min.js",
            "admin/js/trix-init.js",
        )

    def __init__(self, attrs=None):
        default_attrs = {
            "data-trix": "true",
            "style": "display:none;",  # Hide textarea, Trix editor shows instead
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
