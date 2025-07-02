from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import SenhaSegura
from utils.crypto import derivar_chave_da_recovery, descriptografar, gerar_chave_mestra, criptografar, criptografar_chave_mestra
from django.views.decorators.csrf import csrf_protect
import os
import base64

@csrf_protect
def pag_principalView(request):
    user = request.user
    chave_mestra = request.session.get("user_key")
    # Carregar senhas
    senhas_salvas = []

    # Se for envio de nova senha
    if request.method == "POST":
        apps_url = request.POST.get("apps_url")
        usuario = request.POST.get("usuario")
        senha = request.POST.get("senha")

        salt = os.urandom(16)
        iv = os.urandom(16)
        chave = gerar_chave_mestra(chave_mestra, salt)

        senha_segura = SenhaSegura.objects.create(
            usuario_dono=user,
            apps_url=criptografar(apps_url, chave, iv),
            usuario=criptografar(usuario, chave, iv),
            senha=criptografar(senha, chave, iv),
            salt=salt,
            iv=iv
        )
        senha_segura.save()

    senhas = SenhaSegura.objects.filter(usuario_dono=user)
    for s in senhas:
        chave = gerar_chave_mestra(chave_mestra, s.salt)
        resultado = {
            "apps_url": descriptografar(s.apps_url, chave, s.iv),
            "usuario": descriptografar(s.usuario, chave, s.iv),
            "senha": descriptografar(s.senha, chave, s.iv),
        }
        senhas_salvas.append(resultado)
    return render(request, 'gerenciador_senhas/pag_principal.html', {'user': user, 'senhas_salvas': senhas_salvas})


def pag_edicaoView(request):
    return render(request, 'gerenciador_senhas/pag_edicao.html')
