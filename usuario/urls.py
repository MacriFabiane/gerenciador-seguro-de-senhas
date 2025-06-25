from django.urls import path
from . import views
from allauth.account.views import LoginView

urlpatterns = [
    path('', LoginView.as_view(), name='account_login'),    
]