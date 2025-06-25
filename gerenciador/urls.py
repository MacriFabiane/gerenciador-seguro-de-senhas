"""
URL configuration for gerenciador project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from allauth.account.views import LoginView, LogoutView, PasswordResetView, SignupView, PasswordResetFromKeyView, PasswordResetDoneView, PasswordResetFromKeyDoneView, ConfirmEmailView, EmailVerificationSentView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('usuario.urls')),
    path('', include('gerenciador_senhas.urls')),
    path('usuarios/login/', LoginView.as_view(), name='account_login'),
    path('usuarios/logout/', LogoutView.as_view(), name='account_logout'),
    path('usuarios/cadastro/', SignupView.as_view(), name='account_signup'),
    path('usuarios/password/reset/', PasswordResetView.as_view(), name='account_reset_password'),
    re_path(r"^usuarios/password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",PasswordResetFromKeyView.as_view(), name="account_reset_password_from_key"),
    path('usuarios/password/reset/done/', PasswordResetDoneView.as_view(), name='account_reset_password_done'),
    path('usuarios/password/reset/key/done/', PasswordResetFromKeyDoneView.as_view(),name='account_reset_password_from_key_done'),
    re_path(r'^usuarios/confirm-email/(?P<key>[-:\w]+)/$', ConfirmEmailView.as_view(), name='account_confirm_email'),
    path('usuarios/verification-sent/', EmailVerificationSentView.as_view(), name='account_email_verification_sent'),
    path('accounts/', include('allauth.urls')),
    path('session_security/', include('session_security.urls')),
]
