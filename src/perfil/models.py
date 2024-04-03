from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class Perfil(models.Model):
    choice_cargo = [(1,'Gerente'),(2,'Cordenador'),(3,'Produtor'),(4,'Redator'),(5,'Designer'),(6,'Externo')]
    choice_und = [(1,'EFG'),(2,'COTEC'),(3,'CETT'),(4,'BASILEU'),(5,'INTERNO'),(6,'GERAL')]
    id = models.AutoField(primary_key=True)
    user_profile = models.ForeignKey(User,on_delete=models.CASCADE)
    cargo = models.IntegerField(choices=choice_cargo,null=False,blank=False)
    foto = models.TextField(null=False,blank=False)
    permissoes = models.TextField(null=False,blank=False)
    und = models.IntegerField(choices=choice_und,null=False,blank=False,default=5)

    def get_cargo_display(self):
        return dict(self.choice_cargo)[self.cargo]
    
    def get_und_display(self):
        return dict(self.choice_und)[self.und]
    class Meta:
        db_table = 'perfil'