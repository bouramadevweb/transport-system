"""
Commande de gestion Django pour recalculer les dates limites de retour des contrats existants
Usage: python manage.py update_contrat_dates
"""
from django.core.management.base import BaseCommand
from transport.models import ContratTransport
from datetime import timedelta


class Command(BaseCommand):
    help = 'Recalcule les dates limites de retour des contrats (date_debut + 23 jours)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche les modifications sans les appliquer',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)

        contrats = ContratTransport.objects.all()
        total = contrats.count()

        if dry_run:
            self.stdout.write(self.style.WARNING(f"MODE DRY-RUN: Aucune modification ne sera effectuée"))

        self.stdout.write(f"Nombre de contrats à traiter: {total}")

        updated = 0
        errors = 0

        for contrat in contrats:
            try:
                # Calculer la nouvelle date limite de retour
                nouvelle_date_limite = contrat.date_debut + timedelta(days=23)
                ancienne_date_limite = contrat.date_limite_retour

                # Vérifier si la date a changé
                if ancienne_date_limite != nouvelle_date_limite:
                    if dry_run:
                        self.stdout.write(
                            f"  📋 Contrat {contrat.numero_bl}: "
                            f"{ancienne_date_limite} → {nouvelle_date_limite} "
                            f"(différence: {(nouvelle_date_limite - ancienne_date_limite).days} jours)"
                        )
                    else:
                        contrat.date_limite_retour = nouvelle_date_limite
                        contrat.save()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✅ Contrat {contrat.numero_bl}: "
                                f"{ancienne_date_limite} → {nouvelle_date_limite}"
                            )
                        )
                    updated += 1
                else:
                    if not dry_run:
                        self.stdout.write(
                            f"  ⏭️  Contrat {contrat.numero_bl}: Déjà correct ({ancienne_date_limite})"
                        )

            except Exception as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ Erreur pour le contrat {contrat.numero_bl}: {str(e)}"
                    )
                )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\n📊 RÉSUMÉ (DRY-RUN):\n"
                    f"  • {updated} contrat(s) seraient modifié(s)\n"
                    f"  • {total - updated - errors} contrat(s) déjà correct(s)\n"
                    f"  • {errors} erreur(s)"
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    "\n⚠️  Pour appliquer réellement les modifications, exécutez sans --dry-run"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✅ RÉSUMÉ:\n"
                    f"  • {updated} contrat(s) mis à jour\n"
                    f"  • {total - updated - errors} contrat(s) déjà correct(s)\n"
                    f"  • {errors} erreur(s)"
                )
            )
