# shop/forms.py
from django import forms
from .models import ProductReview
from .models import ProductDownload


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.RadioSelect(attrs={"class": "hidden peer"}),
            "comment": forms.Textarea(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-700",
                    "rows": 4,
                    "placeholder": "Only verified buyers can review. Thank you, for sharing your thoughts about this product...",
                }
            ),
        }


class DownloadSelectionForm(forms.Form):
    download_id = forms.ModelChoiceField(
        queryset=ProductDownload.objects.none(),
        widget=forms.HiddenInput,
    )

    def __init__(self, *args, **kwargs):
        product = kwargs.pop("product", None)
        super().__init__(*args, **kwargs)

        if product:
            self.fields["download_id"].queryset = product.downloads.all()
