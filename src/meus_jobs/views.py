from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from solicitacoes.models import Demandas,Solicitacoes
# Create your views here.
@login_required(login_url='/')
def Minhas_Tarefas(request):
    solicitacoes = Solicitacoes.objects.filter(demandas__designante=request.user).all()
    a_fazer = Demandas.objects.filter(status=1, designante_id = request.user.id).all()
    return render(request,'meus_jobs.html',{'solicitacoes':solicitacoes})