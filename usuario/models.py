from django.db import models
from django.contrib.auth.models import User

class ChaveMestraUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    chave_mestra_encriptada = models.BinaryField()
    iv_recovery = models.BinaryField()
    salt_recovery = models.BinaryField()
    iv = models.BinaryField()
    salt = models.BinaryField()
    dado_teste_criptografado = models.BinaryField()
    dado_teste2_criptografado = models.BinaryField()

