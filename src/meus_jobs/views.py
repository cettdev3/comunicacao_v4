from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from solicitacoes.models import Demandas,Solicitacoes,Arquivos_Demandas,Arquivos_Solicitacoes,Pastas
from django.db import transaction
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse

# Create your views here.
@login_required(login_url='/')
def Minhas_Tarefas(request):

    # Filtra todas as demandas do usuário logado
    demandas_do_usuario = Demandas.objects.filter(designante=request.user.id)
    
    # Obtém as solicitações correspondentes às demandas do usuário
    solicitacoes_com_demandas_do_usuario = Solicitacoes.objects.filter(id__in=demandas_do_usuario.values('solicitacao_id')).distinct()

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
    return render(request,'meus_jobs.html',{'solicitacoes':solicitacoes_com_demandas_do_usuario})

@login_required(login_url='/')
def Show_Modal_Task(request):
    req_solicitacao = request.GET.get('solicitacao_id','')
    solicitacao = Solicitacoes.objects.filter(id=req_solicitacao).first()
    arquivos_solicitacao = Arquivos_Solicitacoes.objects.filter(solicitacao_id = solicitacao.id).all()
    pastas = Pastas.objects.filter(solicitacao = solicitacao).all()

    demandas = Demandas.objects.filter(solicitacao = solicitacao).all()
    for demanda in demandas:
        demanda.demandas_arquivos = Arquivos_Demandas.objects.filter(demanda = demanda).all()
    return render(request,'ajax/ajax_task_detail.html',{'solicitacao':solicitacao,'demandas':demandas,'arquivos_solicitacao':arquivos_solicitacao,'pastas':pastas})

@login_required(login_url='/')
def Concluir_Demanda(request):
    print(request.POST)
    print(request.FILES)

    with transaction.atomic():
        try:
            descricao = request.POST.get('editordata','')
            demandaId = request.POST.get('demandaId','')
            pasta = request.POST.get('pasta','')

            
            arquivos = request.FILES.getlist('files[]')
            for arquivo in arquivos:
                fs1 = FileSystemStorage()
                filename1 = fs1.save(arquivo.name, arquivo)
                arquivo_url = fs1.url(filename1)
                arquivos = Arquivos_Demandas.objects.create(rota = arquivo_url,autor_id = request.user.id, demanda_id = demandaId)
            

            demanda = Demandas.objects.get(id=demandaId)
            demanda.descricao_entrega = descricao
            demanda.status = 3
            demanda.pasta_id = pasta
            demanda.save()

            demandas_revisao = Demandas.objects.filter(autor = demanda.autor, solicitacao_id = demanda.solicitacao_id, designante = demanda.autor, descricao_entrega = "Revisão da demanda").first()
            if demandas_revisao:
                demandas_revisao.status = 1
                demandas_revisao.save()
            else:
                #Cria demanda de revisão para o solicitante
                demandas_revisao = Demandas.objects.create(autor = demanda.autor, status = 1,solicitacao_id = demanda.solicitacao_id , designante = demanda.autor,descricao_entrega = "Revisão da demanda")


            return JsonResponse({"success":True,"success_message": "Demanda concluída com sucesso!"}, status=200)
        except Exception as e:
            return JsonResponse({"error":True,"error_message": str(e)}, status=400)

@login_required(login_url='/')        
def Revisar_Demanda(request):
    with transaction.atomic():
        try:
            id_demanda = request.POST.get('demanda_id','')
            motivo = request.POST.get('motivo_devolucao','')

            demanda = Demandas.objects.get(id=id_demanda)
            demanda.status = 1
            demanda.devolutiva = motivo
            demanda.save()

            #Obter o id da solicitação e buscar pela demanda a qual possui a descrição de entrega como Revisão da demanda e que o autor for o solicitante
            solicitacao_id = demanda.solicitacao_id
            demanda_revisao = Demandas.objects.filter(solicitacao_id=solicitacao_id,descricao_entrega="Revisão da demanda",autor=demanda.autor).first()
            demanda = Demandas.objects.get(id=demanda_revisao.id)
            demanda.status = 4
            demanda.save()
            return JsonResponse({"success":True,"success_message": "Demanda revisada com sucesso!"}, status=200)
        
        except Exception as e:
            return JsonResponse({"error":True,"error_message": str(e)}, status=400)

@login_required(login_url='/')        
def removeFilesSolicitacao(request):
    try:
        file_id = request.POST.get('arquivo_id','')
        solicitacao_id = request.POST.get('solicitacao_id','')
        arquivos = Arquivos_Demandas.objects.get(id=file_id)
        arquivos.delete()
        arquivos_solicitacao = Arquivos_Demandas.objects.filter(demanda_id = arquivos.demanda_id).all()
        print(len(arquivos_solicitacao))
        return render(request,'ajax/ajax_remove_file_demand.html',{'arquivos':arquivos_solicitacao})
    except Exception as e:
        return JsonResponse({"error_message": str(e)}, status=400)