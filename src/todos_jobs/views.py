from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from solicitacoes.models import Demandas,Solicitacoes,Arquivos_Demandas,Arquivos_Solicitacoes,Pastas,Perfil
from django.db import transaction
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.contrib.auth.models import User
# Create your views here.
@login_required(login_url='/')
def All_Jobs(request):
    demandas_do_usuario = Demandas.objects.all()
    # Obtém as solicitações correspondentes às demandas do usuário
    solicitacoes_com_demandas_do_usuario = Solicitacoes.objects.filter(id__in=demandas_do_usuario.values('solicitacao_id')).distinct()

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
    return render(request,'todos_jobs.html',{'solicitacoes':solicitacoes_com_demandas_do_usuario})