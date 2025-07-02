from allauth.account.adapter import DefaultAccountAdapter
from django.forms import ValidationError
from django.contrib.auth.models import User
from .models import ChaveMestraUsuario
from utils.crypto import gerar_chave_mestra, gerar_recovery_key, criptografar_chave_mestra
import os

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        # Primeiro salva o usuário normalmente
        user = super().save_user(request, user, form, commit=commit)

        # Pegando as chaves mestras digitadas
        chave1 = request.POST.get("mestra1")
        chave2 = request.POST.get("mestra2")

        if not chave1 or chave1 != chave2:
            raise ValidationError("As chaves mestras não coincidem ou estão vazias.") #tem que mandar esse erro pro front

        # Gerar salt, IV e chave mestra derivada
        salt = os.urandom(16)
        iv = os.urandom(16)
        chave_gerada = gerar_chave_mestra(chave1, salt)

        # Gerar dados de recuperação
        recovery_key = gerar_recovery_key()
        salt_rec = os.urandom(16)
        iv_rec = os.urandom(16)
        chave_rec = gerar_chave_mestra(recovery_key, salt_rec)
        chave_mestra_encriptada = criptografar_chave_mestra(chave_gerada, chave_rec, iv_rec)

        # Salvar a chave no banco
        ChaveMestraUsuario.objects.create(
            usuario=user,
            chave_mestra_encriptada=chave_mestra_encriptada,
            iv=iv,                      # salvar iv original
            salt=salt,                  # salvar salt original
            iv_recovery=iv_rec,
            salt_recovery=salt_rec,
        )

        # Salvar recovery_key na sessão para exibir
        request.session["recovery_key_gerada"] = recovery_key

        return user
