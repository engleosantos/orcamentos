# Generated by Django 2.2.12 on 2020-04-21 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='option_prop',
            field=models.PositiveIntegerField(blank=True, help_text='Cada orçamento pode ter opções 1, 2, 3 ...', null=True, verbose_name='opção'),
        ),
    ]
