from django.db import models
from django.contrib.auth.models import User
class SenhaSegura(models.Model):
    usuario_dono = models.ForeignKey(User, on_delete=models.CASCADE)
    
    apps_url = models.BinaryField()
    usuario = models.BinaryField()
    senha = models.BinaryField()

    salt = models.BinaryField()  # usado para derivar a chave mestra com PBKDF2
    iv = models.BinaryField()    # usado na criptografia AES

    def __str__(self):
        return f"Senha salva para {self.usuario_dono.username}"