from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import HarmfulIngredient, IngredientReview, ProductRating

# Sitemap for HarmfulIngredient model
class HarmfulIngredientSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return HarmfulIngredient.objects.all().order_by('id')  # Order by ID or another relevant field

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else None  # Assumes `updated_at` field exists

    def location(self, item):
        return reverse('ingredient_detail', args=[item.pk])  # Using reverse for URL generation

# Sitemap for IngredientReview model (only approved reviews)
class IngredientReviewSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.6

    def items(self):
        return IngredientReview.objects.filter(approved=True).select_related('ingredient').order_by('created_at')  # Order by created_at

    def lastmod(self, obj):
        return obj.created_at

    def location(self, item):
        return reverse('submit_review', args=[item.ingredient.pk])  # Link to the review page of the ingredient

# Sitemap for ProductRating model (only approved ratings)
class ProductRatingSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return ProductRating.objects.filter(approved=True).order_by('created_at')  # Order by created_at

    def lastmod(self, obj):
        return obj.created_at

    def location(self, item):
        return reverse('ingredient_detail', args=[item.product.id])  # Assuming the product has a link to its detail

# Sitemap for static pages
class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return [
            'index', 
            'about', 
            'user_profile', 
            'update_profile', 
            'result', 
            'login', 
            'signup', 
            'logout',
        ]

    def location(self, item):
        return reverse(item)  # Directly use the name of the URL pattern

    def lastmod(self, item):
        # You can set a fixed date or implement logic to fetch the last modified date
        return None  # Static pages often do not have a last modified date
