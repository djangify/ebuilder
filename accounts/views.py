# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from allauth.account.models import EmailAddress
from shop.models import WishList

from .forms import SupportForm, ProfileForm
from .models import MemberResource
from shop.models import OrderItem


@login_required
def dashboard_view(request):
    user = request.user

    # Check email verification via allauth
    is_verified = EmailAddress.objects.filter(
        user=user,
        verified=True,
    ).exists()

    if not is_verified:
        messages.warning(
            request, "Please verify your email address to access all features."
        )

    purchased_count = (
        OrderItem.objects.filter(order__user=user).values("product").distinct().count()
    )

    member_resources = MemberResource.objects.filter(is_active=True)

    wishlist_items = WishList.objects.filter(user=user).select_related("product")
    favourite_products = [item.product for item in wishlist_items]

    context = {
        "is_verified": is_verified,
        "purchased_count": purchased_count,
        "member_resources": member_resources,
        "favourite_products": favourite_products,
    }

    return render(request, "accounts/dashboard.html", context)


@login_required
def profile_view(request):
    """
    Allow users to update their name.
    Email changes go through allauth's email management.
    """
    user = request.user

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=user)

    context = {
        "form": form,
        "user": user,
    }

    return render(request, "accounts/profile.html", context)


@login_required
def delete_account_view(request):
    """
    Allow users to delete their account.
    Requires confirmation via POST.
    """
    user = request.user

    if request.method == "POST":
        confirm = request.POST.get("confirm_delete", "")
        if confirm == "DELETE":
            user.delete()
            logout(request)
            messages.success(request, "Your account has been permanently deleted.")
            return redirect("core:home")
        else:
            messages.error(request, "Please type DELETE to confirm account deletion.")

    return render(request, "accounts/delete_account.html")


@login_required
def support(request):
    user = request.user

    if request.method == "POST":
        form = SupportForm(request.POST)
        if form.is_valid():
            support_request = form.save(commit=False)
            support_request.user = user
            support_request.save()
            messages.success(
                request,
                "Thanks — your message has been sent. We'll get back to you soon.",
            )
            return redirect("accounts:support")
    else:
        form = SupportForm()

    context = {
        "form": form,
        "user_name": user.get_full_name() or user.first_name or "Member",
        "user_email": user.email,
    }

    return render(request, "accounts/support.html", context)
