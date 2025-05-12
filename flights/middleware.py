# flights/middleware.py
import random
import string

class PromoCodeMiddleware:
    """
    Middleware to assign a random promo code to first-time, unauthenticated visitors.

    Checks the session for a 'has_visited_before' flag. If the flag is not set
    and the user is not authenticated, it generates an 8-character alphanumeric
    promo code, attaches it to the request object as 'promo_code', and sets
    the session flag.
    """
    SESSION_KEY = 'has_visited_before'
    PROMO_CODE_LENGTH = 8

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        # --- Promo Code Logic ---
        # Only run for anonymous users who haven't visited before in this session
        if not request.user.is_authenticated and not request.session.get(self.SESSION_KEY, False):
            # Generate a random promo code
            characters = string.ascii_uppercase + string.digits
            promo_code = ''.join(random.choice(characters) for _ in range(self.PROMO_CODE_LENGTH))

            # Attach the promo code to the request object so views/templates can access it
            request.promo_code = promo_code
            print(f"DEBUG: First visit detected. Generated promo code: {promo_code}") # Debug print

            # Mark this session as having visited
            request.session[self.SESSION_KEY] = True
            print(f"DEBUG: Session key '{self.SESSION_KEY}' set to True.") # Debug print
        else:
            # Ensure request.promo_code doesn't exist for returning/auth users
            # to avoid accidental display in templates
            if hasattr(request, 'promo_code'):
                delattr(request, 'promo_code')

        # --- End Promo Code Logic ---

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

