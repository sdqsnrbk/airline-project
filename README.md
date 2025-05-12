## **Credentials**

**Airline System User Credentials**

* **Admin User:**
* **Username: lagrange**
* **Password: 551881**
##
* **Regular User:**
* **Username: ali**
* **Password: 123qazaq**

## **Code Reflection**

**1\. What does your custom middleware do, and how does it work?**

My custom middleware, named PromoCodeMiddleware and located in the flights/middleware.py file, serves a specific purpose: to greet first-time, unauthenticated visitors with a special offer.

What it does:  
The main goal of this middleware is to identify users who are visiting the website for the first time during their current browser session and haven't logged into an account. For these specific users, it generates a unique 8-character alphanumeric "promo code." This code isn't for actual discounts in the current version of the project; it's meant to be displayed in a banner on the homepage as a welcome gesture.  
How it works:  
The middleware is implemented as a Python class that integrates into Django's request-response processing system.

* **Initialization (\_\_init\_\_)**: When the Django server starts, it creates an instance of my PromoCodeMiddleware.  
* **Request Processing (\_\_call\_\_)**: For every HTTP request that comes to the server, the \_\_call\_\_ method of the middleware is executed.  
  * First, it checks if the user making the request is anonymous (i.e., not logged in) by looking at request.user.is\_authenticated.  
  * If the user is anonymous, it then checks their session data (using request.session) for a key I named has\_visited\_before. If this key doesn't exist in the session, it means this is the first request from this browser session for an anonymous user.  
  * If both conditions are met (anonymous user, first visit in session), the middleware generates a random 8-character string using uppercase letters and digits.  
  * This generated code is then attached to the request object itself, as request.promo\_code. This makes the promo code accessible in the templates.  
  * Crucially, after generating and attaching the code, the middleware sets request.session\['has\_visited\_before'\] \= True. This action ensures that for any subsequent requests from the same browser session, the has\_visited\_before flag will be true, and the promo code logic will be skipped, so the code is only shown once per session to new anonymous users.  
  * If the user is already logged in, or if they have the has\_visited\_before flag in their session, the middleware makes sure that request.promo\_code is not set, so the promo banner doesn't appear for them.  
* After this logic, the middleware passes the request to the next component in Django's processing chain (either another middleware or the view itself).

So, it uses Django's session framework to "remember" a visitor within a single browsing session and only offers the promo code on their initial anonymous visit.

**2\. What problems did you face with authentication or the API? How did you fix them?**

During the development of this project, I encountered a few challenges, particularly with the authentication flow and setting up the REST API.

**Authentication Problems:**

* **Problem: Redirect Error After Registration (NoReverseMatch for 'login'):**  
  * After setting up the user registration form, a successful registration would lead to an error. The system couldn't find the 'login' page to redirect to because I hadn't created its URL pattern yet.  
  * **Fix:** I solved this by defining the URL pattern for the login page in airline/urls.py. I used Django's built-in LoginView and gave its URL pattern the name login, which matched what the registration view was expecting for the redirect.  
* **Problem: CSRF Token Error on Form Submissions:**  
  * When I first tried submitting forms like the registration form, I got a "CSRF verification failed" error (403 Forbidden). This is a security feature in Django.  
  * **Fix:** I double-checked that {% csrf\_token %} was present inside my \<form\> tags in the HTML. I also made sure my browser was handling cookies correctly and that CSRF\_COOKIE\_SECURE in settings.py was False (since I was developing over HTTP). Restarting the server and testing in an incognito browser window helped ensure there wasn't a stale token issue.  
* **Problem: Logout Link Not Working as Expected (Method Not Allowed Error):**  
  * My initial attempt to create a logout link using a simple HTML \<a\> tag resulted in a "Method Not Allowed (GET)" error.  
  * **Fix:** I learned that Django's LogoutView requires a POST request for security. I changed the logout link into a small HTML form containing a button. Clicking this button submits a POST request to the logout URL, which then works correctly.  
* **Problem: Login Required Redirect to Wrong URL:**  
  * When I used the @login\_required decorator to protect certain views, users who weren't logged in were being sent to /accounts/login/, which wasn't where my login page was.  
  * **Fix:** I fixed this by adding LOGIN\_URL \= 'login' to my settings.py file. This told Django to use my /login/ URL (which is named 'login') when the @login\_required decorator needs to redirect an unauthenticated user.

**API Problems:**

* **Problem: Database Error \- Missing user\_id Column (OperationalError):**  
  * After I added a user field (a ForeignKey to the User model) to my Booking model, my API endpoint for creating bookings started failing with an OperationalError. The error message was table flights\_booking has no column named user\_id. This meant my database table didn't match my Django model.  
  * **Fix:** The issue was that the migration to add this new field hadn't been created or applied correctly. The makemigrations command wasn't detecting the change. To solve this, I had to reset the migrations for my flights app by running python manage.py migrate flights zero. This command "unapplies" the migrations for that app. After that, python manage.py makemigrations flights correctly generated a new initial migration file that included the user field in the Booking model. Running python manage.py migrate then applied this new migration, which successfully added the user\_id column to the database table. This did clear the existing data in the flights app tables, but that was acceptable in my development environment to get the schema correct.  
* **Problem: No "Log in" Link in DRF Browsable API for Testing:**  
  * When I first set up the API endpoints, I wanted to test the POST /api/bookings/ endpoint, which needs an authenticated user. However, the Django REST Framework's browsable API page wasn't showing any "Log in" link.  
  * **Fix:** This required two things:  
    1. I made sure that 'rest\_framework.authentication.SessionAuthentication' was listed in DEFAULT\_AUTHENTICATION\_CLASSES within the REST\_FRAMEWORK settings in settings.py. This allows DRF to use Django's session for authentication.  
    2. The main fix was adding the line path('api-auth/', include('rest\_framework.urls')) to my main airline/urls.py file. This includes DRF's own set of login and logout views that are specifically used by the browsable API interface. Once I added this and restarted the server, the "Log in" link appeared.

**3\. Pick one of the functions in the views.py that you wrote and explain it line-by-line what it does.**

I'll explain the manage\_booking view function from my flights/views.py file. This view is designed to allow a logged-in user to see a list of all their past bookings and also provides a form for them to look up a specific booking if they have the booking code.

\# flights/views.py

@login\_required 

\# This decorator ensures that only logged-in users can access this view.  
\# If a user isn't logged in, they'll be redirected to the login page.

def manage\_booking(request):  
    """  
    Handles displaying a list of the user's bookings (when the page is loaded via GET)  
    and looking up a specific booking by its code (when the form is submitted via POST).  
    """  
    \# Initialize variables that will be passed to the template.  
    user\_bookings \= None         \# This will store the list of all bookings for the current user.  
    searched\_booking \= None      \# This will store a specific booking if found via the lookup form.  
    search\_attempted \= False     \# A flag to tell the template if a search was made via POST.

    \# Check if the request method is POST. This happens when the user submits the form to find a specific booking.  
    if request.method \== "POST":  
        search\_attempted \= True  \# Mark that a search attempt was made.  
        \# Get the 'booking\_code' that the user typed into the form.  
        booking\_code \= request.POST.get('booking\_code')

        \# Check if the user actually entered a booking code.  
        if not booking\_code:  
            messages.error(request, "Please enter a booking code.") \# Show an error message.  
            \# Even if the POST fails here, we still want to show the list of all their bookings.  
            user\_bookings \= Booking.objects.filter(user=request.user).select\_related(  
                'passenger', 'flight', 'flight\_\_origin', 'flight\_\_destination'  
            ).order\_by('-id') \# Get all bookings for the logged-in user, ordered by most recent.  
                              \# .select\_related() helps optimize database queries.  
            \# Render the page again, showing the error message and the list of bookings.  
            return render(request, 'manage\_booking.html', {'user\_bookings': user\_bookings, 'searched': search\_attempted})

        \# If a booking code was entered, try to find it in the database.  
        try:  
            \# Attempt to retrieve a single Booking object that matches the entered code (case-insensitive).  
            booking \= Booking.objects.select\_related(  
                'user', 'passenger', 'flight', 'flight\_\_origin', 'flight\_\_destination'  
            ).get(unique\_booking\_code\_\_iexact=booking\_code)

            \# Security check: Ensure the logged-in user owns this booking or is an admin.  
            if not request.user.is\_staff and booking.user \!= request.user:  
                messages.error(request, "You do not have permission to view this booking code.")  
                \# If not authorized, searched\_booking remains None.  
            else:  
                \# If the booking is found and the user is authorized, store it in searched\_booking.  
                searched\_booking \= booking  
        except Booking.DoesNotExist:  
            \# If no booking with that code exists, show an error message.  
            messages.error(request, "Invalid booking code.")  
            \# searched\_booking remains None.

        \# If, after the try-except block, no booking was successfully retrieved for the searched code.  
        if not searched\_booking and booking\_code: \# (and a code was actually entered)  
             messages.info(request, f"Could not find details for booking code: {booking\_code}")

    \# This part of the code runs for every GET request (when the page is first loaded)  
    \# AND it also runs after a POST request (to ensure the list of all user bookings is always up-to-date).  
    \# Fetch all bookings associated with the currently logged-in user.  
    user\_bookings \= Booking.objects.filter(user=request.user).select\_related(  
        'passenger', 'flight', 'flight\_\_origin', 'flight\_\_destination'  
    ).order\_by('-id') \# Order them, for example, by the most recent ones first.

    \# Prepare the data (context) to be sent to the HTML template.  
    context \= {  
        'user\_bookings': user\_bookings,        \# The list of all bookings made by this user.  
        'searched\_booking': searched\_booking,  \# The specific booking found by code (will be None if not found/not searched).  
        'searched': search\_attempted           \# True if the lookup form was submitted, False otherwise.  
    }  
    \# Render the 'manage\_booking.html' template, passing it the context data.  
    return render(request, 'manage\_booking.html', context)

This view effectively combines two functionalities: listing all of a user's bookings and allowing them to search for a specific one. It ensures that users can only see their own data unless they are an admin, and uses Django's messages framework for user feedback.

**4\. If you had more time, what would you improve or what additional functionality would you add?**

If I had more time to work on this airline reservation project, I would focus on several areas to improve its robustness, user experience, and feature set.

**Improvements I'd Make:**

* **Comprehensive Testing:** I would write a full suite of tests, including unit tests for my models, forms, views, and middleware. I'd also add integration tests to cover key user flows like registration, login, booking a flight, and interacting with the API. This would make the application more reliable and easier to maintain or refactor in the future.  
* **Refined User Interface (UI) and User Experience (UX):** While the current styling is functional, I would dedicate time to making the website more visually appealing and intuitive. This could involve using a CSS framework like Bootstrap more consistently or developing a custom design. I'd also look into using JavaScript for client-side form validation and to make parts of the site more dynamic (e.g., updating flight availability without a full page reload).  
* **Optimized Database Queries:** Review all database queries (especially in views and serializers) to ensure they are as efficient as possible, using select\_related and prefetch\_related where appropriate to minimize database hits.  
* **Enhanced Error Handling:** Implement more specific error handling and provide clearer, more user-friendly error messages throughout the application, including for API responses.  
* **Security Hardening:** Conduct a more thorough security review. This would include things like setting up rate limiting on login attempts and sensitive API endpoints, ensuring all user inputs are properly sanitized, and reviewing all permission checks.

**Additional Functionality I'd Add:**

* **Password Reset:** A crucial feature for any site with user accounts is allowing users to reset their forgotten passwords, typically via an email link.  
* **Advanced Flight Search & Filtering:** Allow users to search for flights based on criteria like origin, destination, departure date, return date, and number of passengers. Filters for price or flight duration would also be useful.  
* **Pagination:** For pages that list many items (like the main flights list or the "My Bookings" list), I'd add pagination to improve performance and make it easier for users to navigate through large datasets.  
* **Functional Promo Code System:** The current promo code is just for display. I'd extend this to make it a real feature where codes could be stored in the database with specific discount values or percentages, and users could apply them during the booking process.  
* **Email Notifications:** Implement email notifications for key events, such as when a user successfully registers an account or when a flight booking is confirmed.  
* **Detailed User Profiles:** Expand the user profile page to show more information, perhaps a more detailed booking history, or allow users to save travel preferences.  
* **Admin Flight Management:** Enhance the Django admin panel (or build custom admin views if required) to give administrators more tools for managing flights, such as setting flight schedules, updating seat capacities, viewing passenger manifests for each flight, and managing airports.  
* **Booking Cancellation/Modification:** Provide functionality for users (and admins) to cancel or modify existing bookings, potentially with rules about deadlines or fees.  
* **Seat Selection:** A more advanced feature would be to allow users to select their seats from a visual map of the aircraft during the booking process.  
* **Payment Gateway Integration:** For a more complete booking experience, integrate a (mock or real) payment gateway to handle the payment part of booking a flight.

Implementing these improvements and features would make the airline system much more comprehensive and closer to a real-world application.
