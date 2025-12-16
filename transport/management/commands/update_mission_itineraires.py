"""
Commande de gestion Django pour mettre à jour les itinéraires des missions existantes
Usage: python manage.py update_mission_itineraires
"""
from django.core.management.base import BaseCommand
from transport.models import Mission


class Command(BaseCommand):
    help = 'Met à jour les itinéraires des missions existantes qui n\'en ont pas'

    def handle(self, *args, **options):
        # Récupérer toutes les missions sans itinéraire ou avec l'itinéraire par défaut
        missions = Mission.objects.filter(itineraire__in=['', 'Itinéraire à compléter'])

        total = missions.count()
        self.stdout.write(f"Nombre de missions à mettre à jour: {total}")

        updated = 0
        for mission in missions:
            try:
                # Créer un itinéraire détaillé basé sur les données de la mission
                itineraire = f"Itinéraire : {mission.origine} → {mission.destination}\n"
                itineraire += f"Contrat: {mission.contrat.numero_bl}\n"
                itineraire += f"Camion: {mission.contrat.camion.immatriculation}\n"
                itineraire += f"Chauffeur: {mission.contrat.chauffeur.nom} {mission.contrat.chauffeur.prenom}\n"
                itineraire += f"Téléphone: {mission.contrat.chauffeur.telephone}\n"
                itineraire += f"Conteneur: {mission.contrat.conteneur.numero_conteneur}\n"
                itineraire += f"Date de départ: {mission.date_depart}\n"

                if mission.date_retour:
                    itineraire += f"Date de retour: {mission.date_retour}\n"
                else:
                    itineraire += f"Date de retour prévue: {mission.contrat.date_limite_retour}\n"

                itineraire += f"Statut: {mission.get_statut_display()}\n"
                itineraire += "\n--- Itinéraire généré automatiquement ---\n"
                itineraire += "Veuillez compléter avec les détails spécifiques du trajet."

                # Mettre à jour sans validation pour éviter les erreurs
                mission.itineraire = itineraire
                mission.save(validate=False)

                updated += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Mission {mission.pk_mission} mise à jour")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Erreur pour la mission {mission.pk_mission}: {str(e)}")
                )

        self.stdout.write(
            self.style.SUCCESS(f"\n✅ {updated}/{total} missions mises à jour avec succès")
        )
