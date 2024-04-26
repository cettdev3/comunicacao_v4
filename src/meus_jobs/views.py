from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from solicitacoes.models import Demandas,Solicitacoes,Arquivos_Demandas,Arquivos_Solicitacoes,Pastas,Perfil
from django.db import transaction
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.contrib.auth.models import User
from datetime import datetime

def convert_data_formatada(data):

    data = data.split('/')
    data = data[2]+'-'+data[1]+'-'+data[0]
    return data

# Create your views here.
@login_required(login_url='/')
def Minhas_Tarefas(request):

    #obtem o cargo do usuário logado
    cargo_do_usuario_logado = Perfil.objects.filter(user_profile_id=request.user.id).first()
    usuarios = User.objects.all()
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
    return render(request,'meus_jobs.html',{'solicitacoes':solicitacoes_com_demandas_do_usuario,'usuario':cargo_do_usuario_logado,'usuarios':usuarios})

@login_required(login_url='/')
def Show_Modal_Task(request):
    req_solicitacao = request.GET.get('solicitacao_id','')
    solicitacao = Solicitacoes.objects.filter(id=req_solicitacao).first()
    arquivos_solicitacao = Arquivos_Solicitacoes.objects.filter(solicitacao_id = solicitacao.id).all()
    pastas = Pastas.objects.filter(solicitacao = solicitacao).all()

    gerentes = Perfil.objects.filter(cargo=1).all()
    usuario_logado = Perfil.objects.filter(user_profile_id = request.user.id).first()

    #obtenho a quantidade de demandas que não estão concluidas
    demandas_nao_concluidas = Demandas.objects.filter(solicitacao = solicitacao, status__lt = 4).count()

    usuarios = User.objects.all()
    demandas = Demandas.objects.filter(solicitacao = solicitacao).all()
    for demanda in demandas:
        demanda.demandas_arquivos = Arquivos_Demandas.objects.filter(demanda = demanda).all()
    return render(request,'ajax/ajax_task_detail.html',{'solicitacao':solicitacao,'demandas':demandas,'arquivos_solicitacao':arquivos_solicitacao,'pastas':pastas,'gerentes':gerentes,'usuario_logado':usuario_logado,'usuarios':usuarios,'demandas_pendentes':demandas_nao_concluidas})	

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
        meu_perfil  = Perfil.objects.filter(user_profile_id = request.user.id).first()
        id_demanda = request.POST.get('demanda_id','')
        motivo = request.POST.get('motivo_devolucao','')
        
        #Se o solicitante for o gerente apenas preencher o motivo, caso contrário executa o código abaixo

        if meu_perfil.cargo == 1:

            #altero a demanda revisionada preenchendo o motivo para que o cordenador solicite a revisão
            demanda = Demandas.objects.get(id=id_demanda)
            demanda.devolutiva = motivo
            demanda.save()

            #Busco a demanda do cordenador de revisão e reabro a demanda para que ele solicite a revisão
            demanda_revisao = Demandas.objects.filter(solicitacao_id=demanda.solicitacao_id,descricao_entrega="Revisão da demanda",autor=demanda.autor).first()
            demanda = Demandas.objects.get(id=demanda_revisao.id)
            demanda.status = 1
            demanda.save()

            #busco a demanda do gerente e concluo
            demanda_gerente = Demandas.objects.filter(descricao_entrega="Aprovação da demanda",solicitacao_id=demanda.solicitacao_id).first()
            demanda_gerente.status = 4
            demanda_gerente.save()

            return JsonResponse({"success":True,"success_message": "Demanda devolvida ao cordenador responsável!"}, status=200)

        else:
            try:
            

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
    
@login_required(login_url='/')        
def aprovarDemanda(request):
    gerente = request.POST.get('gerente','')
    demanda_id = request.POST.get('demanda_id','')

    demanda = Demandas.objects.filter(id=demanda_id).first()

    #Verifica se há uma demanda para este gerente com a descrição "Aprovação da Demanda, se tiver altera o status para 1 se não cria a demanda para o gerente"
    demanda_gerente = Demandas.objects.filter(designante=gerente,descricao_entrega="Aprovação da demanda",solicitacao_id=demanda.solicitacao_id).first()

    demanda_cordendador = Demandas.objects.filter(descricao_entrega="Revisão da demanda",solicitacao_id=demanda.solicitacao_id).first()

    if demanda_gerente:
        demanda_gerente.status = 1
        demanda_gerente.save()
        demanda_cordendador.status = 4
        demanda_cordendador.save()
        return JsonResponse({"success":True,"success_message": "Demanda encaminhada com sucesso!"}, status=200)
    else:
        #gera uma demanda para o gerente para aprovação
        demanda = Demandas.objects.create(autor_id=request.user.id, status=1,solicitacao_id=demanda.solicitacao_id, designante_id=int(gerente),descricao_entrega="Aprovação da demanda")
        demanda_cordendador.status = 4
        demanda_cordendador.save()
        return JsonResponse({"success":True,"success_message": "Demanda encaminhada com sucesso!"}, status=200)
    
@login_required(login_url='/') 
def concluirDemanda(request):
    demanda_id = request.POST.get('demanda_id','')
    
    with transaction.atomic():
        try:
            #obtenho a demanda referente a aprovação e marco ela com status de concluido (4)
            demanda = Demandas.objects.get(id=demanda_id)
            demanda.status = 4
            demanda.save()

            #Conta quantas demandas com status 3 possuim na solicitação
            qtd_demandas_solicitacao = Demandas.objects.filter(solicitacao_id=demanda.solicitacao_id,status=3).count()

            if qtd_demandas_solicitacao == 0:
                #busco a demanda do gerente e concluo
                demanda_gerente = Demandas.objects.filter(descricao_entrega="Aprovação da demanda",solicitacao_id=demanda.solicitacao_id).first()
                demanda_gerente.status = 4
                demanda_gerente.save()

                #Reabro a demanda do cordenador
                demanda_cordenador = Demandas.objects.filter(descricao_entrega="Revisão da demanda",solicitacao_id=demanda.solicitacao_id).first()
                demanda_cordenador.status = 1
                demanda_cordenador.save()


        except Exception as e:
            return JsonResponse({"error":True,"error_message": str(e)}, status=400)
        
        return JsonResponse({"success":True,"success_message": "Demanda concluída com sucesso!"}, status=200)

@login_required(login_url='/') 
def backlogUser(request):
    usuario = request.GET.get('usuario','')
    if usuario:

        cargo_do_usuario_logado = Perfil.objects.filter(user_profile_id=usuario).first()
        usuarios = User.objects.all()
        # Filtra todas as demandas do usuário logado
        demandas_do_usuario = Demandas.objects.filter(designante=usuario)
        
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
        return render(request,'ajax/backlog.html',{'solicitacoes':solicitacoes_com_demandas_do_usuario,'usuario':cargo_do_usuario_logado,'usuarios':usuarios})
    else:
        return render(request,'meus_jobs.html')
    
@login_required(login_url='/') 
def alteraSolicitacao(request):

    print(request.POST)
    #DADOS DA SOLICITAÇÃO
    titulo = request.POST.get('titulo','')
    prazo_entrega = request.POST.get('prazo_entrega','')
    prazo_entrega = convert_data_formatada(prazo_entrega)
    prioridade = request.POST.get('prioridade','')
    solicitante = request.POST.get('solicitante','')
    briefing = request.POST.get('briefing','')
    pastas = request.POST.getlist('pastas','')
    usuarios = request.POST.getlist('usuarios','')

    perfil = Perfil.objects.filter(user_profile_id = request.user.id).first()
    unidade = perfil.und

    solicitacao_id = request.POST.get('solicitacaoId','')
    
    if briefing:
        if usuarios:
            try:
                with transaction.atomic():
                    solicitacao = Solicitacoes.objects.get(id=solicitacao_id)
                    briefing_antigo = solicitacao.briefing
                    solicitacao.titulo = titulo
                    solicitacao.prioridade = prioridade
                    solicitacao.prazo_entrega = prazo_entrega
                    solicitacao.ultima_atualizacao = datetime.now()
                    data_atual = datetime.now()
                    data_formatada = data_atual.strftime('%d/%m/%Y %H:%M')
                    novo_breafing = f'<hr><b>{data_formatada} - {request.user.first_name}</b><br>{briefing}<br><br>{briefing_antigo}'
                    solicitacao.briefing = novo_breafing
                    solicitacao.save()

                    try:
                        arquivos = request.FILES.getlist('files[]')
                        for arquivo in arquivos:
                            fs1 = FileSystemStorage()
                            filename1 = fs1.save(arquivo.name, arquivo)
                            arquivo_url = fs1.url(filename1)
                            arquivos = Arquivos_Solicitacoes.objects.create(rota = arquivo_url,autor_id = request.user.id, solicitacao_id = solicitacao.id)

                    except:
                        pass

                    #Cria as pastas
                    for pasta in pastas:
                        pastas_existentes = Pastas.objects.filter(solicitacao = solicitacao, nome = pasta).all()
                        if pasta not in pastas_existentes:
                            pasta_criada = Pastas.objects.create(nome = pasta, solicitacao = solicitacao)

                    for usuario in usuarios:
                        demandas = Demandas.objects.create(autor = request.user, status = 1,solicitacao_id = solicitacao.id, designante = User.objects.get(id = int(usuario)))

                    return JsonResponse({"success_message": "Solicitação Alterada!"}, status=200)
                
            except Exception as e:
                return JsonResponse({"error":True,"error_message": str(e)}, status=400)

            
        else:
            return JsonResponse({"error":True,"error_message": "Ops! Algo deu errado. É necessário designar pelo menos um usuário!"}, status=400)
    else:
        solicitacao = Solicitacoes.objects.get(id=solicitacao_id)
        solicitacao.titulo = titulo
        solicitacao.prioridade = prioridade
        solicitacao.prazo_entrega = prazo_entrega
        solicitacao.save()
        if usuarios:
            for usuario in usuarios:
                    demandas = Demandas.objects.create(autor = request.user, status = 1,solicitacao_id = solicitacao.id, designante = User.objects.get(id = int(usuario)))
            
            #obtenho a solicitação e altero o status dela para a fazer
            solicitacao = Solicitacoes.objects.get(id=solicitacao_id)
            if solicitacao.status == 4:
                solicitacao.status = 2
                solicitacao.save()

        if pastas:
            for pasta in pastas:
                pastas_existentes = Pastas.objects.filter(solicitacao = solicitacao, nome = pasta).all()
                if pasta not in pastas_existentes:
                    pasta_criada = Pastas.objects.create(nome = pasta, solicitacao = solicitacao)

    return JsonResponse({"success_message": "Solicitação Alterada!"}, status=200)

@login_required(login_url='/') 
def concluirJob(request):
    solicitacao_id = request.POST.get('solicitacao_id','')
    try:
        with transaction.atomic():
            #obtenho a solicitação e altero o status dela para concluido
            solicitacao = Solicitacoes.objects.get(id=solicitacao_id)
            solicitacao.status = 4
            solicitacao.save()

            demanda_cordenador = Demandas.objects.filter(descricao_entrega="Revisão da demanda",solicitacao_id=solicitacao_id).first()
            demanda_cordenador.status = 4
            demanda_cordenador.save()
            return JsonResponse({"success":True,"success_message": "Solicitação concluída com sucesso!"}, status=200)
    except Exception as e:
        return JsonResponse({"error":True,"error_message": str(e)}, status=400)
    