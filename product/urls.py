from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

from . import views
from .sitemaps import (
    HarmfulIngredientSitemap,
    IngredientReviewSitemap,
    ProductRatingSitemap,
    StaticViewSitemap
)

# Define all sitemaps used in sitemap.xml
sitemaps = {
    'static': StaticViewSitemap,
    'harmful-ingredients': HarmfulIngredientSitemap,
    'ingredient-reviews': IngredientReviewSitemap,
    'product-ratings': ProductRatingSitemap,
}

urlpatterns = [
    # Static/meta files
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap, {'sitemaps': sitemaps}, name='sitemap'),

    # Auth routes
    path("accounts/", include("allauth.urls")),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("signup/", views.signup_view, name="signup"),
    path("password/change/", views.change_password, name="password_change"),
    path("password/set/", views.set_password, name="set_password"),

    # Main site routes
    path("", views.index, name="index"),
    path("result/", views.result, name="result"),
    path("about/", views.about, name="about"),

    # User profile
    path("profile/", views.user_profile, name="user_profile"),
    path("profile/update/", views.update_profile, name="update_profile"),

    # Ingredient detail and reviews
    path("ingredients/", views.ingredient_list, name="ingredient_list"),
    path("ingredient/<int:pk>/", views.ingredient_detail, name="ingredient_detail"),
    path("ingredient/<int:pk>/review/", views.submit_review, name="submit_review"),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
