# content/views.py

from django.shortcuts import render, get_object_or_404
from .models import GalleryImage
from .models import LinkHubBlock


def gallery_image_modal(request, pk):
    image = get_object_or_404(GalleryImage, pk=pk)

    images = list(GalleryImage.objects.order_by("id"))

    index = images.index(image)

    prev_image = images[index - 1] if index > 0 else None
    next_image = images[index + 1] if index < len(images) - 1 else None

    return render(
        request,
        "content/partials/gallery_modal.html",
        {
            "image": image,
            "prev_image": prev_image,
            "next_image": next_image,
        },
    )


def linkhub_page(request, slug):
    block = get_object_or_404(
        LinkHubBlock.objects.prefetch_related("links"), slug=slug, published=True
    )

    links = block.links.all()

    return render(
        request,
        "content/hublinks.html",
        {
            "block": block,
            "links": links,
        },
    )
