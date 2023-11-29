# Generated by Django 4.2.6 on 2023-11-28 00:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('censo', '0003_alter_habitante_apellido_alter_habitante_nombre'),
    ]

    operations = [
        migrations.AddField(
            model_name='cargafamiliar',
            name='parentesco',
            field=models.CharField(choices=[('Padre/Madre', 'Padre/Madre'), ('Hijo/Hija', 'Hijo/Hija'), ('Hermano/Hermana', 'Hermano/Hermana'), ('Abuelo/Abuela', 'Abuelo/Abuela'), ('Tio/Tia', 'Tio/Tia'), ('Sobrino/Sobrina', 'Sobrino/Sobrina'), ('Esposo/Esposa', 'Esposo/Esposa'), ('Primo/Prima', 'Primo/Prima'), ('Yerno/Yerna', 'Yerno/Yerna'), ('Cuñado/Cuñada', 'Cuñado/Cuñada'), ('Otro', 'Otro')], default='Otro', max_length=100, verbose_name='Parentesco'),
        ),
    ]
