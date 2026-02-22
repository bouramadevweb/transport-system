# Generated manually on 2026-02-22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0029_add_prime_deduction_unique_constraints'),
    ]

    operations = [
        # =========================================================
        # 1. Supprimer les anciennes contraintes avant modification
        # =========================================================
        migrations.RemoveConstraint(
            model_name='transitaire',
            name='unique_transitaire',
        ),
        migrations.RemoveConstraint(
            model_name='client',
            name='unique_client',
        ),

        # =========================================================
        # 2. Modifier les champs unique=True existants (Mecanicien, Fournisseur)
        # =========================================================
        migrations.AlterField(
            model_name='mecanicien',
            name='telephone',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='mecanicien',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='fournisseur',
            name='telephone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),

        # =========================================================
        # 3. Ajouter le champ entreprise (FK nullable) à chaque modèle
        # =========================================================
        migrations.AddField(
            model_name='mecanicien',
            name='entreprise',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='transport.entreprise',
            ),
        ),
        migrations.AddField(
            model_name='fournisseur',
            name='entreprise',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='transport.entreprise',
            ),
        ),
        migrations.AddField(
            model_name='transitaire',
            name='entreprise',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='transport.entreprise',
            ),
        ),
        migrations.AddField(
            model_name='client',
            name='entreprise',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='transport.entreprise',
            ),
        ),

        # =========================================================
        # 4. Ajouter les nouvelles contraintes incluant entreprise
        # =========================================================
        migrations.AddConstraint(
            model_name='mecanicien',
            constraint=models.UniqueConstraint(
                fields=('nom', 'telephone', 'entreprise'),
                name='unique_mecanicien',
            ),
        ),
        migrations.AddConstraint(
            model_name='fournisseur',
            constraint=models.UniqueConstraint(
                fields=('nom', 'telephone', 'entreprise'),
                name='unique_fournisseur',
            ),
        ),
        migrations.AddConstraint(
            model_name='transitaire',
            constraint=models.UniqueConstraint(
                fields=('nom', 'telephone', 'entreprise'),
                name='unique_transitaire',
            ),
        ),
        migrations.AddConstraint(
            model_name='client',
            constraint=models.UniqueConstraint(
                fields=('nom', 'type_client', 'telephone', 'entreprise'),
                name='unique_client',
            ),
        ),
    ]
