from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator #pra gerar token
from django.core.mail import send_mail #pra enviar emails
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http import HttpResponse  #necessário pro uid
from django.utils.encoding import force_bytes, force_str #necessário pro uid
from django.urls import reverse
from django.template.loader import render_to_string
from allauth.account.views import ConfirmEmailView
class CustomConfirmEmailView(ConfirmEmailView):
    def get_redirect_url(self):
        # Modifique para a URL desejada
        return redirect('account_login') 

def logoutView(request):
    logout(request)
    return redirect('loginView')

def chaveRestauracao(request):
    return render(request, 'usuario/chave_restauracao.html')

def exigirChaveMestra(request):
    return render(request, 'usuario/exigir_chave_mestra.html')

def recuperarChaveMestra(request):
    return render(request, 'usuario/recuperar_chave_mestra.html')

def redefinirChaveMestra(request):
    return render(request, 'usuario/redefinir_chave_mestra.html')

