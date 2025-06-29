from django.urls import path
from . import views
from allauth.account.views import LoginView

urlpatterns = [
    path('', LoginView.as_view(), name='account_login'),    
    path('usuarios/chave_restauracao', views.chaveRestauracao, name='chaveRestauracao'),    
    path('usuarios/chave_mestra', views.exigirChaveMestra, name='exigirChaveMestra'),    
    path('usuarios/recuperar_chave_mestra', views.recuperarChaveMestra, name='recuperarChaveMestra'),    
    path('usuarios/redefinir_chave_mestra', views.redefinirChaveMestra, name='redefinirChaveMestra'),    
]