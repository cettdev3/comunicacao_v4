from django.urls import include, path
from solicitacoes.views import Solicitacao,Realizar_Solicitacao

urlpatterns = [
    path('solicitacoes',  Solicitacao),
    path('realizar-solicitacao',  Realizar_Solicitacao)
]
