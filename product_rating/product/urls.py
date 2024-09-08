<<<<<<< Updated upstream:product_rating/product/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.signup_view, name='signup'),
]
=======
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('result/', views.result, name='result'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
>>>>>>> Stashed changes:product/urls.py
