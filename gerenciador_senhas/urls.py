from django.urls import path
from . import views

urlpatterns = [
    path('gerenciador_senhas/pag_principal', views.pag_principalView, name='pag_principalView'),
    path('gerenciador_senhas/pag_edicao', views.pag_edicaoView, name='pag_edicaoView')
]
