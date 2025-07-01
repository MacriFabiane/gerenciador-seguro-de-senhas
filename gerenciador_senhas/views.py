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

    # if not chave_mestra:
    #     return redirect("exigirChaveMestra")  # ou página de erro

    chave_mestra = base64.b64decode(chave_mestra)

    # Se for envio de nova senha
    if request.method == "POST":
        apps_url = request.POST.get("apps_url")
        usuario = request.POST.get("usuario")
        senha = request.POST.get("senha")

        salt = os.urandom(16)
        iv = os.urandom(16)
        chave = gerar_chave_mestra(base64.b64encode(chave_mestra).decode(), salt)

        senha_segura = SenhaSegura.objects.create(
            usuario_dono=user,
            apps_url=criptografar(apps_url, chave, iv),
            usuario=criptografar(usuario, chave, iv),
            senha=criptografar(senha, chave, iv),
            salt=salt,
            iv=iv
        )
        senha_segura.save()

    # Carregar senhas
    senhas_salvas = []
    senhas = SenhaSegura.objects.filter(usuario_dono=user)
    for s in senhas:
        chave = base64.b64decode(chave_mestra)  # já derivada
        resultado = {
            "apps_url": descriptografar(s.apps_url, chave, s.iv),
            "usuario": descriptografar(s.usuario, chave, s.iv),
            "senha": descriptografar(s.senha, chave, s.iv),
        }
        senhas_salvas.append(resultado)
    return render(request, 'gerenciador_senhas/pag_principal.html', {'user': user, 'senhas_salvas': senhas_salvas})

    # return render(request, 'gerenciador_senhas/pag_principal.html', {
    # 'user': {'name':'Maria'},
    # 'senhas_salvas': [
    #     {'apps_url': 'https://facebook.com', 'usuario': 'maria_fb', 'senha': 'senha_fb123'},
    #     {'apps_url': 'https://gmail.com', 'usuario': 'maria.gm', 'senha': 'senha_gmail!'},
    #     {'apps_url': 'https://linkedin.com', 'usuario': 'maria_li', 'senha': 'senhaLinkedin2024'},
    #     {'apps_url': 'https://github.com', 'usuario': 'maria_git', 'senha': '1234segura'},
    # ]})

def pag_edicaoView(request):
    return render(request, 'gerenciador_senhas/pag_edicao.html')