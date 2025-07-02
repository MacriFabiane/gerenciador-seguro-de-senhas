from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from allauth.account.views import ConfirmEmailView
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ChaveMestraUsuario
from gerenciador_senhas.models import SenhaSegura
import os
from utils.crypto import derivar_chave_da_recovery, descriptografar, gerar_chave_mestra, criptografar, criptografar_chave_mestra
import base64
class CustomConfirmEmailView(ConfirmEmailView):
    def get_redirect_url(self):
        # Modifique para a URL desejada
        return redirect('account_login') 

def logoutView(request):
    logout(request)
    return redirect('loginView')

def chaveRestauracao(request):
     # Garante que só entre se houver recovery_key na sessão
    recovery_key = request.session.get("recovery_key_gerada")

    if not recovery_key:
        messages.error(request, "Recovery key não disponível.")
        return redirect('account_login')

    if request.method == "POST":
        # Remove da sessão depois de exibida (boa prática)
        del request.session["recovery_key_gerada"]
        messages.success(request, "Recovery key salva com sucesso.")
        return redirect('account_login')

    return render(request, 'usuario/chave_restauracao.html', {
        'recovery_key': recovery_key
    })

def exigirChaveMestra(request):
    if request.method == 'POST':
        chave_digitada = request.POST.get("chave_mestra")
        user = request.user

        try:
            obj = ChaveMestraUsuario.objects.get(usuario=user)

            # Deriva a chave AES da chave mestra digitada e salt salvo
            chave_derivada = gerar_chave_mestra(chave_digitada, obj.salt)

            # Testa a descriptografia com a chave derivada
            _ = descriptografar(obj.chave_mestra_encriptada, chave_derivada, obj.iv)
            print(f"Tipo chave_mestra_encriptada: {type(obj.chave_mestra_encriptada)}")

            # Se der certo, salva a chave na sessão
            request.session["user_key"] = base64.b64encode(chave_derivada).decode()
            messages.success(request, "Chave mestra validada com sucesso.")
            return redirect('pag_principalView')

        except Exception as e:
            messages.error(request, f"Chave mestra incorreta. Erro: {str(e)}")

    return render(request, 'usuario/exigir_chave_mestra.html')

def recuperarChaveMestra(request):
    if request.method == 'POST':
        recovery_key = request.POST.get("recovery_key")
        user = request.user

        try:
            obj = ChaveMestraUsuario.objects.get(usuario=user)
            chave_rec = derivar_chave_da_recovery(recovery_key, obj.salt_recovery)
            chave_antiga = descriptografar(obj.chave_mestra_encriptada, chave_rec, obj.iv_recovery)

            # Salva a chave e recovery na sessão
            request.session["chave_mestra_antiga"] = base64.b64encode(chave_antiga).decode()
            request.session["recovery_key"] = recovery_key

            messages.success(request, "Recovery key validada. Agora defina uma nova chave mestra.")
            return redirect('redefinirChaveMestra')  

        except Exception:
            messages.error(request, "Recovery key inválida.")

    return render(request, 'usuario/recuperar_chave_mestra.html')

def redefinirChaveMestra(request):
    if request.method == 'POST':
        nova_chave = request.POST.get("nova_chave")
        user = request.user

        # Recupera dados temporários
        chave_antiga = base64.b64decode(request.session.get("chave_mestra_antiga"))
        recovery_key = request.session.get("recovery_key")

        # Deriva nova chave mestra + salt/iv
        salt_nova = os.urandom(16)
        iv_nova = os.urandom(16)
        chave_nova = gerar_chave_mestra(nova_chave, salt_nova)

        # Carrega e recriptografa todos os dados do usuário
        senhas = SenhaSegura.objects.filter(usuario_dono=user)
        for s in senhas:
            s.apps_url = criptografar(descriptografar(s.apps_url, chave_antiga, s.iv), chave_nova, iv_nova)
            s.usuario = criptografar(descriptografar(s.usuario, chave_antiga, s.iv), chave_nova, iv_nova)
            s.senha = criptografar(descriptografar(s.senha, chave_antiga, s.iv), chave_nova, iv_nova)
            s.iv = iv_nova  # novo IV
            s.save()

        # Atualiza chave_mestra_encriptada
        obj = ChaveMestraUsuario.objects.get(usuario=user)
        salt_rec = obj.salt_recovery
        iv_rec = obj.iv_recovery
        chave_rec = derivar_chave_da_recovery(recovery_key, salt_rec)
        chave_mestra_encriptada = criptografar_chave_mestra(chave_nova, chave_rec, iv_rec)

        obj.chave_mestra_encriptada = chave_mestra_encriptada
        obj.save()

        # Limpa sessões
        request.session["user_key"] = base64.b64encode(chave_nova).decode()
        del request.session["chave_mestra_antiga"]
        del request.session["recovery_key"]

        messages.success(request, "Nova chave mestra definida com sucesso.")
        return redirect('pag_principal')

    return render(request, 'usuario/redefinir_chave_mestra.html')

