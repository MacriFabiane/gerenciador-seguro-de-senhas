from django.db import models
from django.contrib.auth.models import User

class ChaveMestraUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    chave_mestra_encriptada = models.BinaryField()
    iv_recovery = models.BinaryField()
    salt_recovery = models.BinaryField()