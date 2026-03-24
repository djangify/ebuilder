# shop/views/downloads.py
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta
import os
import mimetypes
import logging

from ..models import OrderItem, Order, DownloadLog

logger = logging.getLogger("shop")


@login_required
@require_http_methods(["GET"])
def secure_download(request, order_item_id, download_id):
    """
    Secure download handler (FINAL VERSION)

    - Validates ownership
    - Validates purchased variant
    - Uses download_count (no downloads_remaining)
    - Prevents duplicate increments
    - Logs activity
    - Returns file safely
    """

    # Get order item
    order_item = get_object_or_404(OrderItem, id=order_item_id)

    # Ownership check
    if order_item.order.user != request.user:
        messages.error(request, "You do not have permission to access this file.")
        return redirect("shop:purchases")

    # Get requested download
    download = get_object_or_404(order_item.product.downloads, id=download_id)

    # Ensure correct variant was purchased
    if (
        order_item.purchased_download
        and order_item.purchased_download.id != download.id
    ):
        messages.error(request, "This file was not part of your purchase.")
        return redirect("shop:purchases")

    # Validate file exists
    file_field = download.file
    if not file_field:
        logger.error(f"No file attached to download id={download.id}")
        raise Http404("File not available.")

    file_path = file_field.path
    if not os.path.exists(file_path):
        logger.error(f"Missing file on server: {file_path}")
        raise Http404("File missing on server.")

    # ===== DOWNLOAD LIMIT CHECK =====
    if order_item.download_count >= order_item.product.download_limit:
        logger.warning(
            f"Download limit reached: order_item={order_item.id}, user={request.user.id}"
        )
        messages.error(request, "You have reached your download limit.")
        return redirect("shop:purchases")

    # ===== DUPLICATE REQUEST PROTECTION =====
    recent_download = DownloadLog.objects.filter(
        order_item=order_item,
        user=request.user,
        downloaded_at__gte=timezone.now() - timedelta(seconds=2),
    ).exists()

    if recent_download:
        logger.warning(
            f"Duplicate download prevented: order_item={order_item.id}, user={request.user.id}"
        )
        return redirect("shop:purchases")

    # ===== RECORD DOWNLOAD =====
    order_item.download_count += 1
    order_item.save()

    DownloadLog.objects.create(
        order_item=order_item,
        user=request.user,
    )

    logger.info(
        f"Download successful: order_item={order_item.id}, user={request.user.id}"
    )

    # ===== SERVE FILE =====
    filename = os.path.basename(file_path)
    content_type, _ = mimetypes.guess_type(filename)
    content_type = content_type or "application/octet-stream"

    response = FileResponse(
        open(file_path, "rb"),
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
