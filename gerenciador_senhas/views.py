from django.shortcuts import render
from django.contrib.auth.models import User

# Create your views here.
def pag_principalView(request):
    # user = request.user  # pega o usuário logado
    # senhas_salvas = []
    

    # return render(request, 'gerenciador_senhas/pag_principal.html', {'user':user, 'senhas_salvas': senhas_salvas})
    return render(request, 'gerenciador_senhas/pag_principal.html', {
    'user': {'name':'Maria'},
    'senhas_salvas': [
        {'apps_url': 'https://facebook.com/', 'usuario': 'maria_fb', 'senha': 'senha_fb123'},
        {'apps_url': 'https://gmail.com/', 'usuario': 'maria.gm', 'senha': 'senha_gmail!'},
        {'apps_url': 'https://linkedin.com/', 'usuario': 'maria_li', 'senha': 'senhaLinkedin2024'},
        {'apps_url': 'https://github.com/', 'usuario': 'maria_git', 'senha': '1234segura'},
    ]
    })

def pag_edicaoView(request):
    return(request, 'gerenciador_senhas/pag_edicao.html')