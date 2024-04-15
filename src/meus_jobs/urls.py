from django.urls import include, path
from .views import Minhas_Tarefas,Show_Modal_Task,Concluir_Demanda,Revisar_Demanda,removeFilesSolicitacao

urlpatterns = [
    path('meus-jobs',  Minhas_Tarefas),
    path('ajax/show-modal-task',  Show_Modal_Task),
    path('ajax/concluir-demanda',  Concluir_Demanda),
    path('ajax/revisao-demanda',  Revisar_Demanda),
    path('ajax/remove-file',  removeFilesSolicitacao),

]
