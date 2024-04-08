from django.urls import include, path
from .views import Minhas_Tarefas

urlpatterns = [
    path('meus-jobs',  Minhas_Tarefas),
]
