from django.urls import path,include
from . import views
from django.contrib.auth import views as auth_views  # Import Django's built-in auth views
from django.conf import settings
from django.conf.urls.static import static
from allauth.account.views import PasswordChangeView as AllauthPasswordChangeView
from django.contrib.sitemaps.views import sitemap
from .sitemaps import HarmfulIngredientSitemap, IngredientReviewSitemap, ProductRatingSitemap, StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'harmful-ingredients': HarmfulIngredientSitemap,
    'ingredient-reviews': IngredientReviewSitemap,
    'product-ratings': ProductRatingSitemap,
}



urlpatterns = [ 
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('password/change/', views.change_password, name='password_change'),
    path('password/set/', views.set_password, name='set_password'),
    path('accounts/', include('allauth.urls')),
    path('', views.index, name='index'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('result/', views.result, name='result'),
    path('profile/', views.user_profile, name='user_profile'),  # User profile
    path('profile/update/', views.update_profile, name='update_profile'),  # Update profile
    path('about/', views.about, name='about'),

    path('ingredient/<int:pk>/', views.ingredient_detail, name='ingredient_detail'),  # View ingredient details and reviews
    path('ingredient/<int:pk>/review/', views.submit_review, name='submit_review'),    # Submit a review for an ingredient
    path('ingredients/', views.ingredient_list, name='ingredient_list'), 
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)