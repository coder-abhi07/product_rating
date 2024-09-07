# from django.shortcuts import render

# import json
# from authlib.integrations.django_client import OAuth
# from django.conf import settings
# from django.shortcuts import redirect, render
# from django.urls import reverse
# from urllib.parse import quote_plus, urlencode



# # 👆 We're continuing from the steps above. Append this to your webappexample/views.py file.

# oauth = OAuth()

# oauth.register(
#     "auth0",
#     client_id=settings.AUTH0_CLIENT_ID,
#     client_secret=settings.AUTH0_CLIENT_SECRET,
#     client_kwargs={
#         "scope": "openid profile email",
#     },
#     server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
# )

# # 👆 We're continuing from the steps above. Append this to your webappexample/views.py file.

# def login(request):
#     return oauth.auth0.authorize_redirect(
#         request, request.build_absolute_uri(reverse("callback"))
#     )

# # 👆 We're continuing from the steps above. Append this to your webappexample/views.py file.

# def callback(request):
#     token = oauth.auth0.authorize_access_token(request)
#     request.session["user"] = token
#     return redirect(request.build_absolute_uri(reverse("index")))


# # 👆 We're continuing from the steps above. Append this to your webappexample/views.py file.

# def logout(request):
#     request.session.clear()

#     return redirect(
#         f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
#         + urlencode(
#             {
#                 "returnTo": request.build_absolute_uri(reverse("index")),
#                 "client_id": settings.AUTH0_CLIENT_ID,
#             },
#             quote_via=quote_plus,
#         ),
#     )

# 👆 We're continuing from the steps above. Append this to your webappexample/views.py file.

# def index(request):
#     return render(
#         request,
#         "index.html",
#         context={
#             "session": request.session.get("user"),
#             "pretty": json.dumps(request.session.get("user"), indent=4),
#         },
#     )
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from .models import ProductRating, HarmfulIngredient
from django.core.files.base import ContentFile
import io
import requests
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

 # Add this to prevent caching




def send_image_to_ocr(image_file):
    api_key = "K86627853288957"
    api_url = "https://api.ocr.space/parse/image"

    # Create a dictionary for the file upload
    files = {'file': (image_file.name, image_file, 'image/png')}
    
    # Prepare data payload
    data = {
        'apikey': api_key,
        'language': 'eng',
        'isTable' : 'true',
        'OCREngine' : 2  # You can specify other languages if needed
    }
    
    # Make the request
    response = requests.post(api_url, files=files, data=data)
    
    # Check response and parse JSON
    if response.status_code == 200:
        result = response.json()
        return result['ParsedResults'][0]['ParsedText']
    else:
        return None



from .models import HarmfulIngredient, ProductRating

def check_harmful_ingredients(text):
    ingredients = text.split()  # Split the OCR text into words
    harmful_ingredients = HarmfulIngredient.objects.all()

    harmful_count = 0
    total_ingredients = len(ingredients)

    for word in ingredients:
        if harmful_ingredients.filter(name__icontains=word).exists():
            harmful_count += 1

    # Calculate product rating (goodness percentage)
    if total_ingredients > 0:
        rating = 100 - ((harmful_count / total_ingredients) * 100)
    else:
        rating = 100

    return rating


# Login required decorator to protect the page
@login_required
@never_cache 
def index(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('image')
        if not uploaded_file:
            return render(request, 'index.html', {
                'error_message': 'No file uploaded. Please try again.'
            })

        image_content = uploaded_file.read()
        image_file = ContentFile(image_content, uploaded_file.name)

        parsed_text = send_image_to_ocr(image_file)
        if not parsed_text:
            return render(request, 'index.html', {
                'error_message': 'Failed to process the image. Please try again.'
            })

        rating = check_harmful_ingredients(parsed_text)

        product_name = request.POST.get('product_name', 'Unknown Product')
        ProductRating.objects.create(
            product_name=product_name,
            ingredients=parsed_text,
            rating=rating
        )

        # Store result in session
        request.session['product_name'] = product_name
        request.session['parsed_text'] = parsed_text
        request.session['rating'] = rating

        # Redirect to result page
        return redirect('result')

    return render(request, 'index.html')



def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'login.html', {'error_message': 'Invalid credentials'})
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def result(request):
    product_name = request.session.get('product_name')
    parsed_text = request.session.get('parsed_text')
    rating = request.session.get('rating')

    if not product_name or not parsed_text or not rating:
        return redirect('index')  # Redirect back if there's no data

    return render(request, 'result.html', {
        'product_name': product_name,
        'parsed_text': parsed_text,
        'rating': rating
    })
