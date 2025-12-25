# accounts/adapters.py

from allauth.account.adapter import DefaultAccountAdapter
import logging

logger = logging.getLogger(__name__)


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter to save first_name during registration.
    """

    def save_user(self, request, user, form, commit=True):
        """
        Save the user with first_name from signup form.
        """
        # DEBUG: Log what we receive
        logger.warning(f"=== ADAPTER CALLED ===")
        logger.warning(f"Form type: {type(form)}")
        logger.warning(
            f"Form cleaned_data: {getattr(form, 'cleaned_data', 'NO CLEANED_DATA')}"
        )
        logger.warning(f"POST data: {dict(request.POST)}")

        # Let parent save the user first
        user = super().save_user(request, user, form, commit=False)

        logger.warning(f"After super(): user.first_name = '{user.first_name}'")

        # If parent didn't save first_name, get it from POST directly
        if not user.first_name:
            first_name = request.POST.get("first_name", "")
            logger.warning(f"Getting from POST: first_name = '{first_name}'")
            if first_name:
                user.first_name = first_name

        if commit:
            user.save()
            logger.warning(f"User saved with first_name: '{user.first_name}'")

        return user
