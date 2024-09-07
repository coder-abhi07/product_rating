from django.shortcuts import render

import json
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from urllib.parse import quote_plus, urlencode



# 👆 We're continuing from the steps above. Append this to your webappexample/views.py file.

oauth = OAuth()

oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)

# 👆 We're continuing from the steps above. Append this to your webappexample/views.py file.

def login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )

# 👆 We're continuing from the steps above. Append this to your webappexample/views.py file.

def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    request.session["user"] = token
    return redirect(request.build_absolute_uri(reverse("index")))


# 👆 We're continuing from the steps above. Append this to your webappexample/views.py file.

def logout(request):
    request.session.clear()

    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("index")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )

# 👆 We're continuing from the steps above. Append this to your webappexample/views.py file.

def index(request):
    return render(
        request,
        "index.html",
        context={
            "session": request.session.get("user"),
            "pretty": json.dumps(request.session.get("user"), indent=4),
        },
    )

import requests
import requests

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

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm

def signup_view(request):
    form = UserCreationForm(request.POST)
    if form.is_valid():
        form.save()
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(request, user)
        return redirect('upload_image')
    return render(request, 'signup.html', {'form': form})


from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from .models import ProductRating, HarmfulIngredient
import io

def upload_image(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('image')
        if not uploaded_file:
            return render(request, 'index.html', {
                'error_message': 'No file uploaded. Please try again.'
            })

        # Create an in-memory file object
        image_content = uploaded_file.read()
        image_file = ContentFile(image_content, uploaded_file.name)

        # Send image to OCR.space for text extraction
        parsed_text = send_image_to_ocr(image_file)
        if not parsed_text:
            return render(request, 'index.html', {
                'error_message': 'Failed to process the image. Please try again.'
            })

        # Check harmful ingredients and calculate product rating
        rating = check_harmful_ingredients(parsed_text)

        # Save the product rating to the database
        product_name = request.POST.get('product_name', 'Unknown Product')
        ProductRating.objects.create(
            product_name=product_name,
            ingredients=parsed_text,
            rating=rating
        )

        # Store results in session
        request.session['product_name'] = product_name
        request.session['parsed_text'] = parsed_text
        request.session['rating'] = rating

        return redirect('result')

    return render(request, 'index.html')

def result(request):
    product_name = request.session.get('product_name')
    parsed_text = request.session.get('parsed_text')
    rating = request.session.get('rating')

    return render(request, 'result.html', {
        'product_name': product_name,
        'parsed_text': parsed_text,
        'rating': rating
    })