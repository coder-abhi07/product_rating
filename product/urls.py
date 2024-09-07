
from django.urls import path

from . import views

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('upload/', views.upload_image, name='upload_image'),
    path('', views.index, name='index'),
    path('result/', views.result, name='result'),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("callback", views.callback, name="callback"),
    path('login2/', auth_views.LoginView.as_view(), name='login2'),
    path('logout2/', auth_views.LogoutView.as_view(), name='logout2'),
    path('signup/', views.signup_view, name="signup"),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

]
