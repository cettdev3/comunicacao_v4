from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from perfil.models import Perfil


class Solicitacoes(models.Model):
    choice_projeto = [(1,'EFG'),(2,'COTEC'),(3,'CETT'),(4,'BASILEU')]
    choices_status = [(1,'A FAZER'),(2,'FAZENDO'),(3,'EM APROVAÇÃO'),(4,'CONCLUÍDA')]
    choice_prioridade = [(1,'NORMAL'),(2,'URGENTE')]
    id = models.AutoField(primary_key=True)
    titulo = models.TextField(null=False,blank=False)
    motivo_devolucao = models.TextField(null=True,blank=True)
    tipo_projeto = models.IntegerField(choices=choice_projeto,null=False,blank=False)
    autor = models.ForeignKey(User,on_delete=models.CASCADE)
    data_solicitacao = models.DateTimeField(default=timezone.now,null=False,blank=False)
    prazo_entrega = models.DateField(null=False,blank=False)
    briefing = models.TextField(null=False,blank=False)
    prioridade = models.IntegerField(choices=choice_prioridade,null=False,blank=False,default=1)
    status = models.IntegerField(choices=choices_status,null=False,blank=False)

    def get_prioridade_display(self):
        return dict(self.choice_prioridade)[self.prioridade]
    
    def get_status_display(self):
        return dict(self.choices_status)[self.status]

    def get_projeto_display(self):
        return dict(self.choice_projeto)[self.tipo_projeto]

    def is_prazo_vencido(self):
        return self.prazo_entrega < timezone.now().date()
    
    class Meta:
        db_table = 'solicitacoes'

class Pastas(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.TextField(null=False,blank=False)
    solicitacao = models.ForeignKey(Solicitacoes,on_delete=models.CASCADE)

    class Meta:
        db_table = 'pastas'

class Demandas(models.Model):
    choice_status = [(1,'A Fazer'),(2,'Fazendo'),(3,'Em Aprovação'),(4,'Concluído')]
    choice_prioridade = [(1,'Normal'),(2,'Urgente')]
    id = models.AutoField(primary_key=True)
    pasta = models.ForeignKey(Pastas,on_delete=models.CASCADE,null=True,blank=True)
    designante = models.ForeignKey(User,on_delete=models.CASCADE)
    autor = models.ForeignKey(User, related_name='designante',on_delete=models.CASCADE)
    data_designacao = models.DateField(default=timezone.now, null=True, blank=True) 
    prioridade = models.IntegerField(choices=choice_prioridade,null=False,blank=False,default=1)
    descricao_entrega = models.TextField(null=False,blank=False,default="Nenhuma Descrição de Entrega")
    data_entrega = models.DateField(default=timezone.now, null=True, blank=True) 
    devolutiva = models.TextField(null=False,blank=False,default="")
    status = models.IntegerField(choices=choice_status,null=False,blank=False)

    def get_status_display(self):
        return dict(self.choice_status)[self.status]
    
    def get_prioridade_display(self):
        return dict(self.choice_prioridade)[self.prioridade]
    class Meta:
        db_table = 'demandas'