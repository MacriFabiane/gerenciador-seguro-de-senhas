from allauth.account.adapter import DefaultAccountAdapter
from django.forms import ValidationError
from django.contrib import messages
from django.contrib.auth.models import User
from .models import ChaveMestraUsuario
from utils.crypto import gerar_chave_mestra, gerar_recovery_key, criptografar_chave_mestra
import os

class CustomAccountAdapter(DefaultAccountAdapter):
    def clean_password(self, password, user=None):
        # Validação adicional da senha se necessário
        return super().clean_password(password, user)
    
    def save_user(self, request, user, form, commit=True):
        # Primeiro valide as chaves mestras
        chave1 = request.POST.get("mestra1")
        chave2 = request.POST.get("mestra2")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        errors = {}
        
        # Validação das senhas
        if password1 != password2:
            errors['password2'] = _("As senhas não coincidem.")
        
        # Validação das chaves mestras
        if not chave1 or not chave2:
            errors['mestra2'] = _("As chaves mestras não podem estar vazias.")
        elif chave1 != chave2:
            errors['mestra2'] = _("As chaves mestras não coincidem.")
        
        if errors:
            raise ValidationError(errors)

        # Só continua se não houver erros
        user = super().save_user(request, user, form, commit=False)

        salt = os.urandom(16)
        iv = os.urandom(16)
        chave_gerada = gerar_chave_mestra(chave1, salt)
        recovery_key = gerar_recovery_key()
        salt_rec = os.urandom(16)
        iv_rec = os.urandom(16)
        chave_rec = gerar_chave_mestra(recovery_key, salt_rec)
        chave_mestra_encriptada = criptografar_chave_mestra(chave_gerada, chave_rec, iv_rec)

        ChaveMestraUsuario.objects.create(
            usuario=user,
            chave_mestra_encriptada=chave_mestra_encriptada,
            iv_recovery=iv_rec,
            salt_recovery=salt_rec,
        )
        
        request.session["recovery_key_gerada"] = recovery_key

        if commit:
            user.save()
        return user