from django.urls import path
from menu.views import Atualizar_Foto

urlpatterns = [
    path('ajax/atualizar-foto',  Atualizar_Foto),

]