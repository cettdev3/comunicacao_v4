from django.urls import include, path
from gerir_time.views import Gerir_Time,Cadastrar_Usuario,Get_User,Alterar_Usuario

urlpatterns = [
    path('gerir-time',  Gerir_Time),
    path('cadastrar-usuario',  Cadastrar_Usuario),
    path('ajax/modal-user',  Get_User),
    path('altera-usuario',  Alterar_Usuario),

]