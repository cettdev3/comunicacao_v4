from django.urls import include, path
from solicitacoes.views import Solicitacao

urlpatterns = [
    path('solicitacoes',  Solicitacao)
]