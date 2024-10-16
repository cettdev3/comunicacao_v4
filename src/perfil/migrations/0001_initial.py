# Generated by Django 4.0.6 on 2024-04-03 08:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Perfil',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('cargo', models.IntegerField(choices=[(1, 'Gerente'), (2, 'Cordenador'), (3, 'Produtor'), (4, 'Redator'), (5, 'Designer'), (6, 'Externo')])),
                ('foto', models.TextField()),
                ('permissoes', models.TextField()),
                ('und', models.IntegerField(choices=[(1, 'EFG'), (2, 'COTEC'), (3, 'CETT'), (4, 'BASILEU'), (5, 'INTERNO'), (6, 'GERAL')], default=5)),
                ('user_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'perfil',
            },
        ),
    ]
