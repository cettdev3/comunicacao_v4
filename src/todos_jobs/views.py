from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from solicitacoes.models import Demandas,Solicitacoes,Arquivos_Demandas,Arquivos_Solicitacoes,Pastas,Perfil
from django.db import transaction
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import redirect

# Create your views here.
@login_required(login_url='/')
def All_Jobs(request):
    demandas_do_usuario = Demandas.objects.all()
    
    # Obtém as solicitações correspondentes às demandas do usuário
    solicitacoes_com_demandas_do_usuario = Solicitacoes.objects.filter(id__in=demandas_do_usuario.values('solicitacao_id')).distinct()

    #Obtenho todos os usuários com perfil a qual o cargo seja menor que 2
    usuarios_com_perfil_menor_que_2 = User.objects.filter(perfil__cargo__lte=2).all()

    cargo_do_usuario_logado = Perfil.objects.filter(user_profile_id=request.user.id).first()
    # Itera sobre cada solicitação e adiciona os totais de demandas e demandas concluídas
    for solicitacao in solicitacoes_com_demandas_do_usuario:
        # Calcula o total de demandas da solicitação
        total_demandas_solicitacao = demandas_do_usuario.filter(solicitacao=solicitacao).count()

        demandas_a_fazer = demandas_do_usuario.filter(solicitacao=solicitacao, status= 1).count()

        # Calcula o total de demandas em aprovação dentro da solicitação
        demandas_em_aprovacao_solicitacao = demandas_do_usuario.filter(solicitacao=solicitacao, status=3).count()

        # Calcula o total de demandas concluídas da solicitação
        demandas_concluidas_solicitacao = demandas_do_usuario.filter(solicitacao=solicitacao, status=4).count()
        
        # Adiciona os totais à solicitação
        solicitacao.total_demandas = total_demandas_solicitacao
        solicitacao.demandas_concluidas = demandas_concluidas_solicitacao
        solicitacao.demandas_em_aprovacao = demandas_em_aprovacao_solicitacao
        solicitacao.demandas_a_fazer = demandas_a_fazer
    return render(request,'todos_jobs.html',{'solicitacoes':solicitacoes_com_demandas_do_usuario,'usuario':cargo_do_usuario_logado,'superiores':usuarios_com_perfil_menor_que_2})

def backlogUserAll(request):
    usuario = request.GET.get('usuario','')
    demanda = request.GET.get('demanda','')

    if demanda == '0':
        if usuario != '0':	

            cargo_do_usuario_logado = Perfil.objects.filter(user_profile_id=usuario).first()
            usuarios = User.objects.all()

            # Filtra todas as demandas do usuário logado
            demandas_do_usuario = Demandas.objects.all()
            
            # Obtém as solicitações correspondentes às demandas do usuário
            solicitacoes_com_demandas_do_usuario = Solicitacoes.objects.filter(id__in=demandas_do_usuario.values('solicitacao_id'),autor_id=usuario).distinct()

            # Itera sobre cada solicitação e adiciona os totais de demandas e demandas concluídas
            for solicitacao in solicitacoes_com_demandas_do_usuario:
                # Calcula o total de demandas da solicitação
                total_demandas_solicitacao = demandas_do_usuario.filter(solicitacao=solicitacao).count()

                demandas_a_fazer = demandas_do_usuario.filter(solicitacao=solicitacao, status= 1).count()

                # Calcula o total de demandas em aprovação dentro da solicitação
                demandas_em_aprovacao_solicitacao = demandas_do_usuario.filter(solicitacao=solicitacao, status=3).count()

                # Calcula o total de demandas concluídas da solicitação
                demandas_concluidas_solicitacao = demandas_do_usuario.filter(solicitacao=solicitacao, status=4).count()
                
                # Adiciona os totais à solicitação
                solicitacao.total_demandas = total_demandas_solicitacao
                solicitacao.demandas_concluidas = demandas_concluidas_solicitacao
                solicitacao.demandas_em_aprovacao = demandas_em_aprovacao_solicitacao
                solicitacao.demandas_a_fazer = demandas_a_fazer
            return render(request,'ajax/allbacklog.html',{'solicitacoes':solicitacoes_com_demandas_do_usuario,'usuario':cargo_do_usuario_logado,'usuarios':usuarios})
        else:
            demandas_do_usuario = Demandas.objects.all()
    
            # Obtém as solicitações correspondentes às demandas do usuário
            solicitacoes_com_demandas_do_usuario = Solicitacoes.objects.filter(id__in=demandas_do_usuario.values('solicitacao_id')).distinct()

            #Obtenho todos os usuários com perfil a qual o cargo seja menor que 2
            usuarios_com_perfil_menor_que_2 = User.objects.filter(perfil__cargo__lte=2).all()

            cargo_do_usuario_logado = Perfil.objects.filter(user_profile_id=request.user.id).first()
            # Itera sobre cada solicitação e adiciona os totais de demandas e demandas concluídas
            for solicitacao in solicitacoes_com_demandas_do_usuario:
                # Calcula o total de demandas da solicitação
                total_demandas_solicitacao = demandas_do_usuario.filter(solicitacao=solicitacao).count()

                demandas_a_fazer = demandas_do_usuario.filter(solicitacao=solicitacao, status= 1).count()

                # Calcula o total de demandas em aprovação dentro da solicitação
                demandas_em_aprovacao_solicitacao = demandas_do_usuario.filter(solicitacao=solicitacao, status=3).count()

                # Calcula o total de demandas concluídas da solicitação
                demandas_concluidas_solicitacao = demandas_do_usuario.filter(solicitacao=solicitacao, status=4).count()
                
                # Adiciona os totais à solicitação
                solicitacao.total_demandas = total_demandas_solicitacao
                solicitacao.demandas_concluidas = demandas_concluidas_solicitacao
                solicitacao.demandas_em_aprovacao = demandas_em_aprovacao_solicitacao
                solicitacao.demandas_a_fazer = demandas_a_fazer
            return render(request,'ajax/allbacklog.html',{'solicitacoes':solicitacoes_com_demandas_do_usuario,'usuario':cargo_do_usuario_logado,'superiores':usuarios_com_perfil_menor_que_2})
    else:
        if usuario:

            cargo_do_usuario_logado = Perfil.objects.filter(user_profile_id=usuario).first()
            usuarios = User.objects.all()

            # Filtra todas as demandas do usuário logado
            demandas_do_usuario = Demandas.objects.filter(designante=usuario,solicitacao_id=demanda)
            print(len(demandas_do_usuario))
            # Obtém as solicitações correspondentes às demandas do usuário
            solicitacoes_com_demandas_do_usuario = Solicitacoes.objects.filter(id__in=demandas_do_usuario.values('solicitacao_id'),autor_id=usuario).distinct()
            print(len(solicitacoes_com_demandas_do_usuario))
            # Itera sobre cada solicitação e adiciona os totais de demandas e demandas concluídas
            for solicitacao in solicitacoes_com_demandas_do_usuario:
                # Calcula o total de demandas da solicitação
                total_demandas_solicitacao = demandas_do_usuario.filter(solicitacao=solicitacao).count()

                # Calcula o total de demandas em aprovação dentro da solicitação
                demandas_em_aprovacao_solicitacao = demandas_do_usuario.filter(solicitacao=solicitacao, status=3).count()

                # Calcula o total de demandas concluídas da solicitação
                demandas_concluidas_solicitacao = demandas_do_usuario.filter(solicitacao=solicitacao, status=4).count()
                
                # Adiciona os totais à solicitação
                solicitacao.total_demandas = total_demandas_solicitacao
                solicitacao.demandas_concluidas = demandas_concluidas_solicitacao
                solicitacao.demandas_em_aprovacao = demandas_em_aprovacao_solicitacao
            return render(request,'ajax/allbacklog.html',{'solicitacoes':solicitacoes_com_demandas_do_usuario,'usuario':cargo_do_usuario_logado,'usuarios':usuarios})
        else:
            return render(request,'todos_jobs.html')
        
@login_required(login_url='/') 
def showtaskusersAll(request):
    userid = request.GET.get('userid','')
    demandas_do_usuario = Demandas.objects.filter(designante=userid)
    

    # Obtém as solicitações correspondentes às demandas do usuário
    solicitacoes_com_demandas_do_usuario = Solicitacoes.objects.filter(id__in=demandas_do_usuario.values('solicitacao_id')).distinct()

    return render(request,'ajax/select_task_for_user.html',{'demandas':solicitacoes_com_demandas_do_usuario})