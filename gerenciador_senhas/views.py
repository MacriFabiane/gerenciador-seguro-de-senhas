from django.shortcuts import render
from django.contrib.auth.models import User

# Create your views here.
def pag_principalView(request):
    user = request.user  # pega o usuário logado
    senhas_salvas = []
    

    return render(request, 'gerenciador_senhas/pag_principal.html', {'user':user, 'senhas_salvas': senhas_salvas})

def pag_edicaoView(request):
    return(request, 'gerenciador_senhas/pag_edicao.html')