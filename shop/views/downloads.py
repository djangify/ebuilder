# shop/views/downloads.py
from ..models import Order, OrderItem
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404
from django.views.decorators.http import require_http_methods
import os
import mimetypes
from wsgiref.util import FileWrapper
import logging

logger = logging.getLogger("shop")


@login_required
@require_http_methods(["GET"])
def secure_download(request, order_item_id, download_id):
    """
    Secure download view that serves files for purchased products.
    Only allows downloading the specific variant that was purchased.
    """
    order_item = get_object_or_404(OrderItem, id=order_item_id)

    # Only the owner can download
    if order_item.order.user != request.user:
        raise PermissionDenied

    # Get the specific download file
    download = get_object_or_404(order_item.product.downloads, id=download_id)

    # Verify user purchased this specific download variant
    if (
        order_item.purchased_download
        and order_item.purchased_download.id != download.id
    ):
        raise PermissionDenied("You did not purchase this download variant.")

    file_field = download.file
    if not file_field:
        raise Http404("No downloadable file found.")

    file_path = file_field.path
    if not os.path.exists(file_path):
        raise Http404("File missing on server.")

    # Check download limit
    if order_item.downloads_remaining <= 0:
        raise PermissionDenied("Your download limit has been reached.")

    # Update download counts
    order_item.downloads_remaining -= 1
    order_item.download_count += 1
    order_item.save()

    # Serve the file
    filename = os.path.basename(file_path)
    content_type, _ = mimetypes.guess_type(filename)
    content_type = content_type or "application/octet-stream"

    response = FileResponse(
        FileWrapper(open(file_path, "rb")),
        as_attachment=True,
        content_type=content_type,
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response


@login_required
def purchases(request):
    """
    Display all purchases for the logged-in user.
    Includes download links for each product's downloads.
    """
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related("items__product__downloads")
        .order_by("-created")
    )
    return render(request, "shop/purchases.html", {"orders": orders})


@login_required
def order_history(request):
    """Display order history for the logged-in user."""
    orders = Order.objects.filter(user=request.user).order_by("-created")
    return render(request, "shop/order_history.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    """Display details for a specific order."""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, "shop/purchases.html", {"order": order})
