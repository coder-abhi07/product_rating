from django.urls import path
from . import views
from django.contrib.auth import views as auth_views  # Import Django's built-in auth views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('result/', views.result, name='result'),
    path('profile/', views.user_profile, name='user_profile'),  # User profile
    path('profile/update/', views.update_profile, name='update_profile'),  # Update profile
    path('profile/change-password/', auth_views.PasswordChangeView.as_view(
        template_name='change_password.html',
        success_url='/profile/'
    ), name='change_password'),  # Password change
]
