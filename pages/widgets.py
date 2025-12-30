# pages/widgets.py
from tinymce.widgets import TinyMCE


class RichTextWidget(TinyMCE):
    """
    TinyMCE rich text editor widget.
    Uses configuration from settings.TINYMCE_DEFAULT_CONFIG
    """

    class Media:
        css = {"all": ("admin/css/admin-fixes.css",)}

    def __init__(self, attrs=None, mce_attrs=None):
        default_attrs = attrs or {}
        super().__init__(attrs=default_attrs, mce_attrs=mce_attrs)


# Backward compatibility alias
TrixWidget = RichTextWidget
