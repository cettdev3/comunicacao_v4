from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from perfil.models import Perfil
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from .models import Arquivos_Demandas,Arquivos_Solicitacoes,Solicitacoes,Pastas,Demandas,Perfil
from django.db import transaction

def convert_data_formatada(data):

    data = data.split('/')
    data = data[2]+'-'+data[1]+'-'+data[0]
    return data


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

@login_required(login_url='/')
def Realizar_Solicitacao(request):
  
    #DADOS DA SOLICITAÇÃO
    titulo = request.POST.get('titulo','')
    prazo_entrega = request.POST.get('prazo_entrega','')
    prazo_entrega = convert_data_formatada(prazo_entrega)
    prioridade = request.POST.get('prioridade','')
    solicitante = request.POST.get('solicitante','')
    briefing = request.POST.get('editordata','')
    pastas = request.POST.getlist('pastas','')
    usuarios = request.POST.getlist('usuarios','')

    perfil = Perfil.objects.filter(user_profile_id = request.user.id).first()
    unidade = perfil.und

    if titulo:
        pass
    else:
        return JsonResponse({"error":True,"error_message": "Ops! Algo deu errado. Verifique se o título foi preenchido."}, status=400)
    
    if prazo_entrega:
        pass
    else:
        return JsonResponse({"error":True,"error_message": "Ops! Algo deu errado. Verifique se o prazo de entrega foi preenchido."}, status=400)

    if briefing:
        pass
    else:
        return JsonResponse({"error":True,"error_message": "Ops! Algo deu errado. Verifique se o briefing foi preenchido."}, status=400)

    if pastas:
        pass
    else:
        return JsonResponse({"error":True,"error_message": "Ops! Algo deu errado. Você precisa adicionar pelo menos uma pasta!"}, status=400)

    if usuarios:
        pass
    else:
        return JsonResponse({"error":True,"error_message": "Ops! Algo deu errado. É necessário designar pelo menos um usuário!"}, status=400)
    
    #CRIA A SOLICITAÇÃO
    with transaction.atomic():
        try:
            solicitar = Solicitacoes.objects.create(
                    titulo = titulo,
                    prioridade = prioridade,
                    tipo_projeto = unidade,
                    prazo_entrega = prazo_entrega,
                    briefing = briefing,
                    autor = request.user,
                    status = 1

                )

            try:
                arquivos = request.FILES.getlist('files[]')
                for arquivo in arquivos:
                    fs1 = FileSystemStorage()
                    filename1 = fs1.save(arquivo.name, arquivo)
                    arquivo_url = fs1.url(filename1)
                    arquivos = Arquivos_Solicitacoes.objects.create(rota = arquivo_url,autor_id = request.user.id, solicitacao_id = solicitar.id)

            except:
                pass

            #Cria as pastas
            for pasta in pastas:
                pasta_criada = Pastas.objects.create(nome = pasta, solicitacao = solicitar)

            #Cria demanda para os usuários
            for usuario in usuarios:
                demandas = Demandas.objects.create(autor = request.user, status = 1,solicitacao_id = solicitar.id, designante = User.objects.get(id = int(usuario)))
        
        except Exception as e:
             return JsonResponse({"error":True,"error_message": str(e)}, status=400)
    
    return JsonResponse({"success_message": "Solicitação Alterada!"}, status=200)