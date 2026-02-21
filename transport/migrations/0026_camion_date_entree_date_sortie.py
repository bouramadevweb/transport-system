from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0025_add_utilisateur_to_chauffeur'),
    ]

    operations = [
        migrations.AddField(
            model_name='camion',
            name='date_entree',
            field=models.DateField(blank=True, null=True, verbose_name="Date d'entrée dans la flotte"),
        ),
        migrations.AddField(
            model_name='camion',
            name='date_sortie',
            field=models.DateField(blank=True, null=True, verbose_name='Date de sortie de la flotte'),
        ),
    ]
