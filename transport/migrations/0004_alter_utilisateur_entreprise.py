# Generated by Django 5.2.3 on 2025-06-29 16:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0003_alter_utilisateur_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='utilisateur',
            name='entreprise',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='transport.entreprise'),
        ),
    ]
