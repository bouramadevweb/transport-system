# Generated migration for salary management

from django.db import migrations, models
import django.db.models.deletion
from uuid import uuid4


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0015_conteneur_statut'),
    ]

    operations = [
        # Modèle Salaire (Bulletin de paie)
        migrations.CreateModel(
            name='Salaire',
            fields=[
                ('pk_salaire', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('mois', models.IntegerField(choices=[(1, 'Janvier'), (2, 'Février'), (3, 'Mars'), (4, 'Avril'), (5, 'Mai'), (6, 'Juin'), (7, 'Juillet'), (8, 'Août'), (9, 'Septembre'), (10, 'Octobre'), (11, 'Novembre'), (12, 'Décembre')])),
                ('annee', models.IntegerField()),
                ('salaire_base', models.DecimalField(decimal_places=2, max_digits=10, default=0)),
                ('heures_supplementaires', models.DecimalField(decimal_places=2, max_digits=6, default=0)),
                ('taux_heure_supp', models.DecimalField(decimal_places=2, max_digits=10, default=0)),
                ('total_primes', models.DecimalField(decimal_places=2, max_digits=10, default=0)),
                ('total_deductions', models.DecimalField(decimal_places=2, max_digits=10, default=0)),
                ('salaire_net', models.DecimalField(decimal_places=2, max_digits=10, default=0)),
                ('date_paiement', models.DateField(null=True, blank=True)),
                ('statut', models.CharField(max_length=20, choices=[('brouillon', 'Brouillon'), ('valide', 'Validé'), ('paye', 'Payé')], default='brouillon')),
                ('mode_paiement', models.CharField(max_length=20, choices=[('especes', 'Espèces'), ('virement', 'Virement'), ('cheque', 'Chèque'), ('mobile', 'Paiement Mobile')], null=True, blank=True)),
                ('notes', models.TextField(blank=True, default='')),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_modification', models.DateTimeField(auto_now=True)),
                ('chauffeur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='salaires', to='transport.chauffeur', null=True, blank=True)),
                ('utilisateur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='salaires_employe', to='transport.utilisateur', null=True, blank=True)),
                ('cree_par', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='salaires_crees', to='transport.utilisateur', null=True)),
            ],
            options={
                'verbose_name': 'Salaire',
                'verbose_name_plural': 'Salaires',
                'ordering': ['-annee', '-mois'],
            },
        ),

        # Modèle Prime
        migrations.CreateModel(
            name='Prime',
            fields=[
                ('pk_prime', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('type_prime', models.CharField(max_length=100)),
                ('montant', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.TextField(blank=True, default='')),
                ('date_attribution', models.DateField(auto_now_add=True)),
                ('salaire', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='primes', to='transport.salaire')),
            ],
            options={
                'verbose_name': 'Prime',
                'verbose_name_plural': 'Primes',
            },
        ),

        # Modèle Deduction
        migrations.CreateModel(
            name='Deduction',
            fields=[
                ('pk_deduction', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('type_deduction', models.CharField(max_length=100)),
                ('montant', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.TextField(blank=True, default='')),
                ('date_deduction', models.DateField(auto_now_add=True)),
                ('salaire', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deductions', to='transport.salaire')),
            ],
            options={
                'verbose_name': 'Déduction',
                'verbose_name_plural': 'Déductions',
            },
        ),

        # Index pour améliorer les performances
        migrations.AddIndex(
            model_name='salaire',
            index=models.Index(fields=['mois', 'annee'], name='transport_s_mois_idx'),
        ),
        migrations.AddIndex(
            model_name='salaire',
            index=models.Index(fields=['statut'], name='transport_s_statut_idx'),
        ),
        migrations.AddConstraint(
            model_name='salaire',
            constraint=models.CheckConstraint(
                check=models.Q(chauffeur__isnull=False) | models.Q(utilisateur__isnull=False),
                name='salaire_has_employee'
            ),
        ),
    ]
