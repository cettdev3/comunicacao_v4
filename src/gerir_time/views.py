from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from perfil.models import Perfil
from django.db import transaction
from django.contrib.auth.hashers import make_password

def get_und(und,usuario,request):
    unidade = Perfil.objects.filter(und = und).count()
    if unidade > 0:
        usuario_unidade = Perfil.objects.filter(und = und, user_profile = usuario).first()
        if usuario_unidade:
            usuario_unidade = usuario_unidade.user_profile_id
        else:
            cria_perfil = Perfil.objects.create(user_profile_id = usuario,und = 5,cargo = 6)
        if und < 5 and unidade > 0 and usuario_unidade != int(usuario):
            return True
        else:
            return False

# Create your views here.
@login_required(login_url='/')
def Gerir_Time(request):
    usuarios = User.objects.all()
    for usuario in usuarios:
        perfil = Perfil.objects.filter(user_profile_id = usuario.id).first()
        usuario.perfil = perfil
        usuario.save()
    foto = Perfil.objects.filter(user_profile_id = request.user.id).first()
    perm = foto.cargo

    cargo = Perfil.objects.filter(user_profile_id = request.user.id).values('cargo')
    cargo = cargo[0]['cargo']
    return render(request,'gerir_time.html',{'usuarios':usuarios,'foto':foto, 'perm':perm,'cargo':cargo})

@login_required(login_url='/')
def Cadastrar_Usuario(request):
    nome = request.POST.get('nome','')
    email = request.POST.get('email','')
    usuario = request.POST.get('usuario','')
    senha = request.POST.get('password','')
    cargo = request.POST.get('cargo','')
    unidade = request.POST.get('unidade','')

    und_cadastrada = Perfil.objects.filter(und=unidade).first()
    if und_cadastrada and int(unidade) < 5:
        return JsonResponse({'erro': 'Não foi possível criar o usuário. A unidade já está vinculada a um outro usuário!'}, status=400)
    else:
        try:
            with transaction.atomic():
                usuario = User.objects.create_user(
                    username = usuario,
                    email = email,
                    first_name = nome,
                    password = senha
                )
                perfil = Perfil.objects.create(
                    user_profile = usuario,
                    cargo = cargo,
                    und = unidade
                )
            
            usuarios = User.objects.all()
            for usuario in usuarios:
                perfil = Perfil.objects.filter(user_profile_id = usuario.id).first()
                usuario.perfil = perfil
                usuario.save()
            foto = Perfil.objects.filter(user_profile_id = request.user.id).first()
            return render(request,'ajax/ajax_tbl_user.html',{'usuarios':usuarios,'foto': foto})
        except:
            return JsonResponse({'erro': 'Usuário ja existe!'}, status=400)

@login_required(login_url='/')
def Get_User(request):
    user_id = request.GET.get('user_id','')
    usuario = User.objects.filter(id = user_id).first()

    perfil = Perfil.objects.filter(user_profile_id = usuario.id).first()
    usuario.perfil = perfil
    return render(request,'ajax/tbl_usuarios.html',{'usuario':usuario})

@login_required(login_url='/')
def Alterar_Usuario(request):
    user_id = request.POST.get('user_id','')
    nome = request.POST.get('nome_modal','')
    email = request.POST.get('email_modal','')
    usuario = request.POST.get('usuario_modal','')
    senha = request.POST.get('senha_modal','')
    cargo = request.POST.get('cargo_modal','')
    unidade = request.POST.get('unidade_modal','')

    status_und = get_und(int(unidade),user_id,request)
    if status_und:
        return JsonResponse({'erro': 'Não foi possível criar o usuário. A unidade já está vinculada a um outro usuário!'}, status=400)
    else:
        #VERIFICA SE POSSUI PERFIL CADASTRADO
        perfil_cadastrado = Perfil.objects.filter(user_profile_id=user_id).exists()
        
        #SE NÃO EXISTIR PERFIL CADASTRADO
        if not perfil_cadastrado:

            #CADASTRA PERFIL
            perfil = Perfil.objects.create(user_profile_id=user_id, cargo=cargo, und=unidade)

            usuario = User.objects.get(id=user_id)
            usuario.first_name = nome
            usuario.email = email
            if senha:
                usuario.set_password(senha)
            usuario.save()

        
        else:

            #ALTERA PERFIL
            perfil = Perfil.objects.filter(user_profile_id=user_id).update(cargo=cargo, und=unidade)

            usuario = User.objects.get(id=user_id)
            usuario.first_name = nome
            usuario.email = email
            if senha:
                usuario.set_password(senha)
            usuario.save()

        usuarios = User.objects.all()
        for usuario in usuarios:
            perfil = Perfil.objects.filter(user_profile_id = usuario.id).first()
            usuario.perfil = perfil
            usuario.save()
        foto = Perfil.objects.filter(user_profile_id = request.user.id).first()
        return render(request,'ajax/ajax_tbl_user.html',{'usuarios':usuarios,'foto': foto})

    