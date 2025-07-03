from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from allauth.account.views import ConfirmEmailView
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ChaveMestraUsuario
from gerenciador_senhas.models import SenhaSegura
import os
from utils.crypto import derivar_chave_da_recovery, descriptografar, gerar_chave_mestra, criptografar, criptografar_chave_mestra, descriptografar_chave_mestra
import base64
import logging
logger = logging.getLogger(__name__)

class CustomConfirmEmailView(ConfirmEmailView):
    def get_redirect_url(self):
        # Modifique para a URL desejada
        return redirect('account_login') 
    
@login_required
def logoutView(request):
    logout(request)
    return redirect('loginView')

@login_required
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
    
@login_required
def exigirChaveMestra(request):
    if request.method == 'POST':
        chave_digitada = request.POST.get("chave_mestra")
        user = request.user

        try:
            obj = ChaveMestraUsuario.objects.get(usuario=user)
            print(f"Salt original: {obj.salt}") 
            
            # Deriva a chave a partir da senha digitada
            chave_digitada_derivada = gerar_chave_mestra(chave_digitada, obj.salt)

            # Tenta descriptografar um valor de teste (ex: "test")
            dado_teste_criptografado = obj.dado_teste_criptografado  # Você precisa armazenar isso antes
            teste = 'Teste'  # Mesma codificação
            dado_teste_criptografado2 = criptografar(teste, chave_digitada_derivada, obj.iv)
            print( dado_teste_criptografado)
            print( dado_teste_criptografado2)
            print(chave_digitada_derivada)
            
            if dado_teste_criptografado == dado_teste_criptografado2:
                messages.success(request, "Chave correta!")
                request.session["user_key"]=chave_digitada
                return redirect('pag_principalView')
            else:
                messages.error(request, "Chave incorreta.")

        except Exception as e:
            messages.error(request, f"Erro: {str(e)}")

    return render(request, 'usuario/exigir_chave_mestra.html')

@login_required
def recuperarChaveMestra(request):
    if request.method == 'POST':
        
        recovery_key = request.POST.get("recovery_key")
        user = request.user
               
        try:
            obj = ChaveMestraUsuario.objects.get(usuario=user)
            chave_rec = gerar_chave_mestra(recovery_key, obj.salt_recovery)  
               
            dado_teste2_criptografado = obj.dado_teste2_criptografado  # Você precisa armazenar isso antes
            teste2 = 'Teste'  # Mesma codificação
            dado_teste2_criptografado2 = criptografar(teste2, chave_rec, obj.iv_recovery)
            print( dado_teste2_criptografado)
            print( dado_teste2_criptografado2)
            print(chave_rec)
            
            if dado_teste2_criptografado == dado_teste2_criptografado2:
                print("entrou")
                chave_antiga = descriptografar_chave_mestra(obj.chave_mestra_encriptada, chave_rec, obj.iv_recovery)
                request.session["chave_mestra_antiga"] = base64.b64encode(chave_antiga)
                print(request.session.get("chave_mestra_antiga"))
                request.session["recovery_key"] = recovery_key

                messages.success(request, "Recovery key validada. Agora defina uma nova chave mestra.")
                return redirect('redefinirChaveMestra') 
            else:
                messages.error(request, "Recovery key inválida.")

        except Exception as e:
            logger.warning(f"Erro ao recuperar chave mestra: {e}")
            messages.error(request, "Recovery key inválida.")

    return render(request, 'usuario/recuperar_chave_mestra.html')

@login_required
def redefinirChaveMestra(request):
    if request.method == 'POST':
        nova_chave = request.POST.get("nova_chave")
        user = request.user

        # Recupera dados temporários da sessão
        
        chave_antiga = request.session.get("chave_mestra_antiga")
        print(chave_antiga)
        recovery_key = request.session.get("recovery_key")

        # Deriva nova chave mestra com novo salt/iv
        salt_nova = os.urandom(16)
        chave_nova = gerar_chave_mestra(nova_chave, salt_nova)
        iv_nova = os.urandom(16)

        # Carrega e recriptografa todos os dados do usuário
        senhas = SenhaSegura.objects.filter(usuario_dono=user)
        for s in senhas:
            try:
                chave = gerar_chave_mestra(chave_antiga.decode(), s.salt)
                # Descriptografa os dados
                apps_url = descriptografar(s.apps_url, chave, s.iv)
                usuario = descriptografar(s.usuario, chave, s.iv)
                senha = descriptografar(s.senha, chave, s.iv)
                
                # Criptografa com a nova chave
                s.apps_url = criptografar(apps_url, chave_nova, iv_nova)
                s.usuario = criptografar(usuario, chave_nova, iv_nova)
                s.senha = criptografar(senha, chave_nova, iv_nova)
                s.salt = salt_nova  # Atualiza o salt para o novo
                s.iv = iv_nova      # Atualiza o IV para o novo
                s.save()
            except Exception as e:
                print(f"Erro ao processar senha ID {s.id}: {str(e)}")
                continue

        # Atualiza chave_mestra_encriptada usando a recovery key
        obj = ChaveMestraUsuario.objects.get(usuario=user)
        salt_rec = obj.salt_recovery
        iv_rec = obj.iv_recovery
        chave_rec = derivar_chave_da_recovery(recovery_key, salt_rec)
        chave_mestra_encriptada = criptografar_chave_mestra(chave_nova, chave_rec, iv_rec)
        teste = 'Teste'  # Mesma codificação
        dado_teste_criptografado = criptografar(teste, chave_mestra_encriptada, obj.iv)

        obj.chave_mestra_encriptada = chave_mestra_encriptada
        obj.dado_teste_criptografado=dado_teste_criptografado
        obj.save()

        # Atualiza a sessão e limpa dados temporários
        request.session["user_key"] = nova_chave  # Armazena a senha em texto, não a chave
        del request.session["chave_mestra_antiga"]
        del request.session["recovery_key"]

        messages.success(request, "Nova chave mestra definida com sucesso.")
        return redirect('account_login')

    return render(request, 'usuario/redefinir_chave_mestra.html')