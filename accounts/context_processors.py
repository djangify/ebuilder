# accounts/context_processors.py
import time


def form_timestamp(request):
    """Add current timestamp for form timing validation."""
    return {"form_timestamp": str(time.time())}
