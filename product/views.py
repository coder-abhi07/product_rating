from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.core.files.base import ContentFile
import io
import requests
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator



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



# def check_harmful_ingredients(text):
#     ingredients = text.split()  # Split the OCR text into words
#     harmful_ingredients = HarmfulIngredient.objects.all()

#     harmful_count = 0
#     total_ingredients = len(ingredients)

#     for word in ingredients:
#         if harmful_ingredients.filter(name__icontains=word).exists():
#             harmful_count += 1

#     # Calculate product rating (goodness percentage)
#     if total_ingredients > 0:
#         rating = 100 - ((harmful_count / total_ingredients) * 100)
#     else:
#         rating = 100

#     return rating

# def check_harmful_ingredients(text):
#     ingredients = text.split()  # Split the OCR text into words
#     harmful_ingredients = HarmfulIngredient.objects.all()
    
#     harmful_ingredients_set = set(ingredient.name.lower() for ingredient in harmful_ingredients)
    
#     harmful_matched = []
#     harmful_count = 0
#     total_ingredients = len(ingredients)

#     for word in ingredients:
#         if word.lower() in harmful_ingredients_set:
#             harmful_matched.append(word)
#             harmful_count += 1

#     # Calculate product rating (goodness percentage)
#     if total_ingredients > 0:
#         rating = 100 - ((harmful_count / total_ingredients) * 100)
#     else:
#         rating = 100

#     return rating, harmful_matched

def check_harmful_ingredients(text):
    ingredients = text.split()  # Split the OCR text into words
    harmful_ingredients = HarmfulIngredient.objects.all()
    
    harmful_ingredients_set = set(ingredient.name.lower() for ingredient in harmful_ingredients)
    
    harmful_matched = []
    harmful_count = 0
    total_ingredients = len(ingredients)

    for word in ingredients:
        if word.lower() in harmful_ingredients_set:
            harmful_matched.append(word)
            harmful_count += 1

    # Calculate product rating (goodness percentage)
    if total_ingredients > 0:
        rating = 100 - ((harmful_count / total_ingredients) * 100)
    else:
        rating = 100

    return rating, harmful_matched


# def index(request):
#     if request.method == 'POST':
#         uploaded_file = request.FILES.get('image')
#         if not uploaded_file:
#             return render(request, 'index.html', {
#                 'error_message': 'No file uploaded. Please try again.'
#             })

#         image_content = uploaded_file.read()
#         image_file = ContentFile(image_content, uploaded_file.name)

#         parsed_text = send_image_to_ocr(image_file)
#         if not parsed_text:
#             return render(request, 'index.html', {
#                 'error_message': 'Failed to process the image. Please try again.'
#             })

#         rating = check_harmful_ingredients(parsed_text)

#         product_name = request.POST.get('product_name', 'Unknown Product')
#         ProductRating.objects.create(
#             product_name=product_name,
#             ingredients=parsed_text,
#             rating=rating
#         )

#         # Store result in session
#         request.session['product_name'] = product_name
#         request.session['parsed_text'] = parsed_text
#         request.session['rating'] = rating

#         # Redirect to result page
#         return redirect('result')

#     return render(request, 'index.html')
from .models import ProductRating
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

        rating, harmful_matched = check_harmful_ingredients(parsed_text)

        product_name = request.POST.get('product_name', 'Unknown Product')
        ProductRating.objects.create(
            product_name=product_name,
            ingredients=parsed_text,
            rating=rating  # Ensure this is a float or Decimal
        )

        # Store result in session
        request.session['product_name'] = product_name
        request.session['parsed_text'] = parsed_text
        request.session['rating'] = rating
        request.session['harmful_matched'] = harmful_matched

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

    # Example data - replace with actual harmful ingredient count and total count
    harmful_ingredients_count = sum(1 for word in parsed_text.split() if HarmfulIngredient.objects.filter(name__icontains=word).exists())
    total_ingredients_count = len(parsed_text.split())

    if not product_name or not parsed_text or not rating:
        return redirect('index')  # Redirect back if there's no data

    return render(request, 'result.html', {
        'product_name': product_name,
        'parsed_text': parsed_text,
        'rating': rating,
        'harmful_ingredients_count': harmful_ingredients_count,
        'total_ingredients_count': total_ingredients_count
    })


from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def user_profile(request):
    user = request.user  # Get the current logged-in user
    return render(request, 'profile.html', {'user': user})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm
from django.contrib import messages

@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('user_profile')
    else:
        form = UserUpdateForm(instance=request.user)
    
    return render(request, 'update_profile.html', {'form': form})

from django.shortcuts import render

def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

def custom_500_view(request):
    return render(request, '500.html', status=500)

def custom_403_view(request, exception):
    return render(request, '403.html', status=403)

def custom_400_view(request, exception):
    return render(request, '400.html', status=400)


def about(request):
    return render(request, 'about.html')
 


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.core.files.base import ContentFile
from django.views.decorators.cache import never_cache

from .models import HarmfulIngredient,  IngredientReview
from .forms import IngredientReviewForm, UserUpdateForm
import requests

# views.py
from django.shortcuts import render, redirect
# from .models import Review
# from .forms import ReviewForm

from django.shortcuts import render, redirect
# from .models import Review
# from .forms import ReviewForm

# views.py
from django.shortcuts import render, redirect, get_object_or_404
# from .models import  Ingredient, Review
# from .forms import ReviewForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .models import HarmfulIngredient
from .forms import IngredientReviewForm

from django.contrib import messages



@login_required
def submit_review(request, pk):
    ingredient = get_object_or_404(HarmfulIngredient, pk=pk)
    user = request.user
    
    # Check if the user has already reviewed this ingredient
    existing_review = IngredientReview.objects.filter(ingredient=ingredient, user=user).first()

    if existing_review:
        # Update the existing review
        form = IngredientReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            updated_review = form.save(commit=False)
            updated_review.approved = False 
            updated_review.save()
            messages.success(request, 'Your review has been updated and will be approved by the admin.')
        else:
            messages.error(request, 'There was a problem updating your review.')
    else:
        # Create a new review
        form = IngredientReviewForm(request.POST)
        if form.is_valid():
            new_review = form.save(commit=False)
            new_review.ingredient = ingredient
            new_review.user = user
            new_review.approved = False
            new_review.save()
            messages.success(request, 'Your review has been submitted and will be approved by the admin.')
        else:
            messages.error(request, 'There was a problem submitting your review.')

    return redirect('ingredient_detail', pk=pk)


def ingredient_detail(request, pk):
    ingredient = get_object_or_404(HarmfulIngredient, pk=pk)
    reviews = IngredientReview.objects.filter(ingredient=ingredient, approved=True).order_by('-created_at')

    
    return render(request, 'ingredient_detail.html', {
        'ingredient': ingredient,
        'reviews': reviews,
    })

def ingredient_list(request):
    ingredients = HarmfulIngredient.objects.all()
    return render(request, 'ingredient_list.html', {'ingredients': ingredients})
