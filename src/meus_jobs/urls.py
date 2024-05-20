from django.urls import include, path
from .views import Minhas_Tarefas,Show_Modal_Task,Concluir_Demanda,Revisar_Demanda,removeFilesSolicitacao,aprovarDemanda,concluirDemanda,backlogUser,alteraSolicitacao,concluirJob,showtaskusers,revisajob

urlpatterns = [
    path('meus-jobs',  Minhas_Tarefas),
    path('ajax/show-modal-task',  Show_Modal_Task),
    path('ajax/concluir-demanda',  Concluir_Demanda),
    path('ajax/revisao-demanda',  Revisar_Demanda),
    path('ajax/remove-file',  removeFilesSolicitacao),
    path('ajax/aprovar-demanda',  aprovarDemanda),
    path('ajax/finalizar-demanda',  concluirDemanda),
    path('ajax/backlog-user',  backlogUser),
    path('ajax/altera-solicitacao',  alteraSolicitacao),
    path('ajax/concluir-job',  concluirJob),
    path('ajax/show-tasks-for-user',  showtaskusers),
    path('ajax/revisa-job',  revisajob),

]
