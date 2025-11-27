from django.core.management.base import BaseCommand
from transport.models import Affectation, Chauffeur, Camion


class Command(BaseCommand):
    help = 'Synchronise les statuts est_affecter des chauffeurs et camions en fonction des affectations actives'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Début de la synchronisation...'))

        # 1. Réinitialiser tous les statuts à False
        nb_chauffeurs = Chauffeur.objects.update(est_affecter=False)
        nb_camions = Camion.objects.update(est_affecter=False)

        self.stdout.write(f'✓ {nb_chauffeurs} chauffeurs réinitialisés')
        self.stdout.write(f'✓ {nb_camions} camions réinitialisés')

        # 2. Récupérer toutes les affectations actives
        affectations_actives = Affectation.objects.filter(date_fin_affectation__isnull=True)
        nb_affectations = affectations_actives.count()

        self.stdout.write(f'\n{nb_affectations} affectations actives trouvées')

        # 3. Marquer les chauffeurs et camions affectés
        chauffeurs_affecter = []
        camions_affecter = []

        for affectation in affectations_actives:
            # Marquer le chauffeur comme affecté
            affectation.chauffeur.est_affecter = True
            affectation.chauffeur.save(update_fields=['est_affecter'])
            chauffeurs_affecter.append(affectation.chauffeur)

            # Marquer le camion comme affecté
            affectation.camion.est_affecter = True
            affectation.camion.save(update_fields=['est_affecter'])
            camions_affecter.append(affectation.camion)

            self.stdout.write(
                f'  • Affectation: {affectation.chauffeur.nom} {affectation.chauffeur.prenom} → '
                f'{affectation.camion.immatriculation} (depuis {affectation.date_affectation})'
            )

        self.stdout.write(self.style.SUCCESS(f'\n✅ Synchronisation terminée!'))
        self.stdout.write(self.style.SUCCESS(f'   - {len(set(chauffeurs_affecter))} chauffeur(s) affecté(s)'))
        self.stdout.write(self.style.SUCCESS(f'   - {len(set(camions_affecter))} camion(s) affecté(s)'))

        # 4. Afficher les chauffeurs et camions disponibles
        chauffeurs_disponibles = Chauffeur.objects.filter(est_affecter=False).count()
        camions_disponibles = Camion.objects.filter(est_affecter=False).count()

        self.stdout.write(f'\n📊 Résumé:')
        self.stdout.write(f'   - {chauffeurs_disponibles} chauffeur(s) disponible(s)')
        self.stdout.write(f'   - {camions_disponibles} camion(s) disponible(s)')
