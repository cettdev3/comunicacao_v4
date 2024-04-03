from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from perfil.models import Perfil
from .models import Notificacoes
from django.http import JsonResponse
import requests
from django.contrib.auth.models import User
from django.db import transaction
from django.core.files.storage import FileSystemStorage

@login_required(login_url='/')
def Atualizar_Foto(request):
    foto = request.FILES.getlist('files[]')
    foto_url = ""
    for arquivo in foto:
        fs1 = FileSystemStorage()
        filename1 = fs1.save(arquivo.name, arquivo)
        foto_url = fs1.url(filename1)

    perfil = Perfil.objects.get(user_profile_id = request.user.id)
    perfil.foto = foto_url
    perfil.save()

    return JsonResponse({"success":True,"success_message": "Foto atualizada com sucesso!"}, status=200)

