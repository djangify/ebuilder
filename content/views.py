# content/views.py

from django.shortcuts import render, get_object_or_404
from .models import GalleryImage


def gallery_image_modal(request, pk):
    image = get_object_or_404(GalleryImage, pk=pk)
    return render(
        request,
        "content/partials/gallery_modal.html",
        {"image": image},
    )
