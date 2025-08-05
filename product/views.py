from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, SetPasswordForm, UserChangeForm
from django.contrib import messages
from django.core.files.base import ContentFile
from django.views.decorators.cache import never_cache
from django.http import HttpResponse
from django.conf import settings

import requests
import json
import re
from .models import HarmfulIngredient, ProductRating, IngredientReview
from .forms import IngredientReviewForm, UserUpdateForm

# Extended list of harmful ingredients to check against
ADDITIONAL_HARMFUL_INGREDIENTS = [
    # Preservatives
    'sodium benzoate', 'potassium benzoate', 'sodium nitrate', 'sodium nitrite',
    'bha', 'bht', 'tbhq', 'sulfur dioxide', 'sodium sulfite',
    
    # Artificial Colors
    'red 40', 'yellow 5', 'yellow 6', 'blue 1', 'blue 2', 'red 3',
    'tartrazine', 'sunset yellow', 'allura red', 'brilliant blue',
    
    # Artificial Sweeteners
    'aspartame', 'sucralose', 'acesulfame potassium', 'saccharin',
    'neotame', 'advantame',
    
    # Trans Fats
    'partially hydrogenated', 'hydrogenated oil', 'trans fat',
    'shortening', 'margarine',
    
    # High Sodium/Sugar Indicators
    'high fructose corn syrup', 'corn syrup', 'monosodium glutamate',
    'msg', 'sodium chloride',
    
    # Other Additives
    'carrageenan', 'sodium phosphate', 'propylene glycol',
    'artificial flavor', 'artificial flavoring', 'natural flavor'
]

# OCR Function
def send_image_to_ocr(image_file):
    api_key = "K86627853288957"
    api_url = "https://api.ocr.space/parse/image"
    files = {'file': (image_file.name, image_file, 'image/png')}
    data = {
        'apikey': api_key,
        'language': 'eng',
        'isTable': 'true',
        'OCREngine': 2
    }
    
    try:
        response = requests.post(api_url, files=files, data=data)
        if response.status_code == 200:
            result = response.json()
            if result.get('ParsedResults') and len(result['ParsedResults']) > 0:
                return result['ParsedResults'][0]['ParsedText']
        return None
    except Exception as e:
        print(f"OCR Error: {str(e)}")
        return None

# Ingredient Check - keeping original function name
def check_predefined_ingredients(text):
    """Check text against database harmful ingredients and additional list"""
    if not text:
        return []
    
    words = text.lower().split()
    text_lower = text.lower()
    matched = []
    
    # Check database ingredients
    harmful_ingredients = HarmfulIngredient.objects.all()
    for ingredient in harmful_ingredients:
        ingredient_name = ingredient.name.lower()
        if ingredient_name in text_lower:
            matched.append(ingredient.name)
    
    # Check additional harmful ingredients
    for ingredient in ADDITIONAL_HARMFUL_INGREDIENTS:
        if ingredient.lower() in text_lower:
            matched.append(ingredient.title())
    
    return list(set(matched))  # Remove duplicates

def clean_json_response(text):
    """Extract and clean JSON from Gemini response"""
    if not text:
        return None
    
    # Remove markdown code blocks
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    
    # Find JSON object
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
    
    if json_match:
        json_text = json_match.group(0)
        # Clean up common issues
        json_text = re.sub(r',\s*}', '}', json_text)  # Remove trailing commas
        json_text = re.sub(r',\s*]', ']', json_text)  # Remove trailing commas in arrays
        return json_text
    
    return None

def create_default_gemini_result(rating="🟡 Needs Caution"):
    """Create default result when Gemini analysis fails"""
    return {
        'rating': rating,
        'reason': 'Analysis completed with limited data',
        'recommendation': 'Check product labels carefully and consult healthcare professionals for personalized advice',
        'concerns': ['Limited analysis data available'],
        'harmful_ingredients': []
    }

# Gemini Analysis - keeping original function name
def get_gemini_analysis(full_text):
    """
    Analyze product ingredients using Google's Gemini API
    Returns data in format expected by result.html template
    """
    try:
        if not full_text or not full_text.strip():
            return create_default_gemini_result()
        
        ANALYSIS_PROMPT = f"""
        You are an expert food safety and nutrition analyst. Analyze the following product ingredient list and nutritional information.

        Your task:
        1. Identify potentially harmful ingredients
        2. Assess overall product safety
        3. Provide health recommendations
        4. Rate the product

        Product Information:
        {full_text}

        Respond ONLY with valid JSON in this exact format:
        {{
            "rating": "🟢 Likely Safe" | "🟡 Needs Caution" | "🔴 Avoid",
            "reason": "Brief explanation of the rating",
            "recommendation": "Specific recommendation for consumers",
            "concerns": ["concern1", "concern2", "concern3"],
            "harmful_ingredients": ["ingredient1", "ingredient2"]
        }}
        """
        
        api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        api_key = settings.GEMINI_API_KEY
        
        request_body = {
            "contents": [
                {
                    "parts": [
                        {"text": ANALYSIS_PROMPT}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "topK": 1,
                "topP": 0.8,
                "maxOutputTokens": 1024,
            }
        }
        
        response = requests.post(
            f"{api_url}?key={api_key}",
            headers={"Content-Type": "application/json"},
            json=request_body,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"Gemini API Error: {response.status_code}")
            return create_default_gemini_result()
        
        data = response.json()
        
        # Extract the response text
        candidates = data.get("candidates", [])
        if not candidates:
            return create_default_gemini_result()
            
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        
        if not parts:
            return create_default_gemini_result()
            
        generated_text = parts[0].get("text", "")
        
        if not generated_text:
            return create_default_gemini_result()
        
        
        
        # Clean and extract JSON from the response
        json_text = clean_json_response(generated_text)
        
        if not json_text:
            return create_default_gemini_result()
        
        try:
            result_object = json.loads(json_text)
            
            # Ensure all required fields exist with defaults
            if 'rating' not in result_object:
                result_object['rating'] = '🟡 Needs Caution'
            if 'reason' not in result_object:
                result_object['reason'] = 'Analysis completed'
            if 'recommendation' not in result_object:
                result_object['recommendation'] = 'Check product labels and consult healthcare professionals'
            if 'concerns' not in result_object or not isinstance(result_object['concerns'], list):
                result_object['concerns'] = ['Standard food safety precautions recommended']
            if 'harmful_ingredients' not in result_object or not isinstance(result_object['harmful_ingredients'], list):
                result_object['harmful_ingredients'] = []
                
            return result_object
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            return create_default_gemini_result()
    
    except requests.exceptions.Timeout:
        print("Gemini API timeout")
        return create_default_gemini_result()
    except requests.exceptions.RequestException as e:
        print(f"Gemini API request failed: {str(e)}")
        return create_default_gemini_result()
    except Exception as e:
        print(f"Unexpected error in get_gemini_analysis: {str(e)}")
        return create_default_gemini_result()

# Index View
def index(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('image')
        if not uploaded_file:
            return render(request, 'index.html', {'error_message': 'No file uploaded.'})

        try:
            image_content = uploaded_file.read()
            image_file = ContentFile(image_content, uploaded_file.name)

            parsed_text = send_image_to_ocr(image_file)
            if not parsed_text:
                return render(request, 'index.html', {'error_message': 'OCR failed. Please try again.'})

            harmful_matched = check_predefined_ingredients(parsed_text)
            gemini_result = get_gemini_analysis(parsed_text)
            

            product_name = request.POST.get('product_name', 'Unknown Product')
            
            try:
                ProductRating.objects.create(
                    product_name=product_name,
                    ingredients=parsed_text,
                    rating=0
                )
            except Exception as e:
                print(f"Error saving ProductRating: {str(e)}")

            request.session['product_name'] = product_name
            request.session['parsed_text'] = parsed_text
            request.session['rating'] = gemini_result

            return redirect('result')

        except Exception as e:
            print(f"Error in index view: {str(e)}")
            return render(request, 'index.html', {'error_message': 'OCR failed. Please try again.'})

    return render(request, 'index.html')

# Auth Views
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
        if user:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'login.html', {'error_message': 'Invalid credentials'})
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

# Password Views
@login_required
def change_password(request):
    if request.user.has_usable_password():
        if request.method == 'POST':
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password has been successfully updated!')
                return redirect('user_profile')
            else:
                messages.error(request, 'Please correct the error below.')
        else:
            form = PasswordChangeForm(request.user)
        return render(request, 'change_password.html', {'form': form})
    return redirect('set_password')

@login_required
def set_password(request):
    if not request.user.has_usable_password():
        if request.method == 'POST':
            form = SetPasswordForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password has been successfully set!')
                return redirect('user_profile')
            else:
                messages.error(request, 'Please correct the error below.')
        else:
            form = SetPasswordForm(request.user)
        return render(request, 'set_password.html', {'form': form})
    return redirect('change_password')

# Result View - keeping original variable names for template compatibility
@login_required
def result(request):
    product_name = request.session.get('product_name', 'Unknown Product')
    parsed_text = request.session.get('parsed_text')
    gemini_result = request.session.get('rating', {})  # Note: session key is 'rating' not 'gemini_result'
    
    

    if not parsed_text:
        messages.error(request, 'No analysis data found. Please upload an image first.')
        return redirect('index')

    # Get harmful ingredients from database matching the parsed text
    harmful_ingredients_from_db = []
    if parsed_text:
        words = parsed_text.lower().split()
        text_lower = parsed_text.lower()
        
        # Check database ingredients
        db_ingredients = HarmfulIngredient.objects.all()
        for ingredient in db_ingredients:
            if ingredient.name.lower() in text_lower:
                harmful_ingredients_from_db.append(ingredient.name)

    # Get harmful ingredients from Gemini
    harmful_ingredients_from_gemini = gemini_result.get('harmful_ingredients', [])
    
    # Calculate total harmful ingredients
    all_harmful = set(harmful_ingredients_from_db + harmful_ingredients_from_gemini)
    harmful_total = len(all_harmful)

    return render(request, 'result.html', {
        'product_name': product_name,
        'parsed_text': parsed_text,
        'rating': gemini_result.get('rating', 'Unknown'),
        'reason': gemini_result.get('reason', ''),
        'recommendation': gemini_result.get('recommendation', ''),
        'concerns': gemini_result.get('concerns', []),
        'harmful_ingredients_from_db': harmful_ingredients_from_db,
        'harmful_ingredients_from_gemini': harmful_ingredients_from_gemini,
        'harmful_total': harmful_total,
    })

# Profile Views
@login_required
def user_profile(request):
    return render(request, 'profile.html', {'user': request.user})

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

# Error Handlers
def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

def custom_500_view(request):
    return render(request, '500.html', status=500)

def custom_403_view(request, exception):
    return render(request, '403.html', status=403)

def custom_400_view(request, exception):
    return render(request, '400.html', status=400)

# Ingredient Views
def about(request):
    return render(request, 'about.html')

@login_required
def submit_review(request, pk):
    ingredient = get_object_or_404(HarmfulIngredient, pk=pk)
    user = request.user
    existing_review = IngredientReview.objects.filter(ingredient=ingredient, user=user).first()

    if existing_review:
        form = IngredientReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            updated_review = form.save(commit=False)
            updated_review.approved = False
            updated_review.save()
            messages.success(request, 'Your review has been updated and will be approved by the admin.')
        else:
            messages.error(request, 'There was a problem updating your review.')
    else:
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
    return render(request, 'ingredient_detail.html', {'ingredient': ingredient, 'reviews': reviews})

def ingredient_list(request):
    ingredients = HarmfulIngredient.objects.all()
    return render(request, 'ingredient_list.html', {'ingredients': ingredients})

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Sitemap: https://product-rating.me/sitemap.xml"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
