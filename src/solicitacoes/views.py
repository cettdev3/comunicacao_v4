from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from perfil.models import Perfil
from django.contrib.auth.models import User

@login_required(login_url='/')
def Solicitacao(request):
    cargo = Perfil.objects.filter(user_profile_id = request.user.id).values('cargo')
    cargo = cargo[0]['cargo']

    #OBTÉM TODOS OS USUÁRIOS
    usuarios = User.objects.all()

    #OBTÉM OS USUÁRIOS CORDENADORES
    usuarios_cordenadores = User.objects.filter(id__in = Perfil.objects.filter(cargo = 2).values('user_profile_id'))
    print(usuarios_cordenadores)
    return render(request,'solicitacoes.html',{'cargo':cargo,'usuarios':usuarios,'usuarios_cordenadores':usuarios_cordenadores})