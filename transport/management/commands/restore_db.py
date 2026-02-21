"""
Commande Django pour restaurer la base de données depuis une sauvegarde.

Usage:
    python manage.py restore_db                           # Liste les backups disponibles
    python manage.py restore_db backups/db_backup_xxx.gz  # Restaure un backup spécifique
    python manage.py restore_db --latest                  # Restaure le dernier backup
"""

import os
import shutil
import gzip
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = 'Restaure la base de données depuis une sauvegarde'

    def add_arguments(self, parser):
        parser.add_argument(
            'backup_file',
            nargs='?',
            type=str,
            default=None,
            help='Chemin vers le fichier de sauvegarde (.gz)',
        )
        parser.add_argument(
            '--latest',
            action='store_true',
            help='Restaurer le dernier backup disponible',
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='Lister les backups disponibles',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forcer la restauration sans confirmation',
        )

    def handle(self, *args, **options):
        backup_dir = Path(settings.BASE_DIR) / 'backups'

        # Lister les backups
        if options['list'] or (not options['backup_file'] and not options['latest']):
            self.list_backups(backup_dir)
            return

        # Trouver le fichier à restaurer
        if options['latest']:
            backup_file = self.get_latest_backup(backup_dir)
        else:
            backup_file = Path(options['backup_file'])

        if not backup_file.exists():
            raise CommandError(f'Fichier de sauvegarde non trouvé: {backup_file}')

        # Confirmation
        if not options['force']:
            self.stdout.write(self.style.WARNING(
                f'\n⚠️  ATTENTION: Cette action va remplacer la base de données actuelle!'
            ))
            self.stdout.write(f'   Fichier source: {backup_file}')
            self.stdout.write(f'   Taille: {backup_file.stat().st_size / (1024*1024):.2f} MB')

            confirm = input('\nVoulez-vous continuer? (oui/non): ')
            if confirm.lower() not in ['oui', 'o', 'yes', 'y']:
                self.stdout.write(self.style.WARNING('Restauration annulée.'))
                return

        # Restaurer
        self.restore_database(backup_file)

    def list_backups(self, backup_dir):
        """Liste les backups disponibles"""
        if not backup_dir.exists():
            self.stdout.write(self.style.WARNING(
                f'Aucun répertoire de backup trouvé: {backup_dir}'
            ))
            return

        backups = sorted(backup_dir.glob('db_backup_*.gz'), reverse=True)

        if not backups:
            self.stdout.write(self.style.WARNING('Aucun backup disponible.'))
            return

        self.stdout.write('\n📁 Backups disponibles:\n')
        self.stdout.write('-' * 70)

        for backup in backups:
            stat = backup.stat()
            size_mb = stat.st_size / (1024 * 1024)
            date = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')

            self.stdout.write(
                f'  {backup.name:<40} {size_mb:>8.2f} MB    {date}'
            )

        self.stdout.write('-' * 70)
        self.stdout.write(f'\nTotal: {len(backups)} backup(s)')
        self.stdout.write('\nPour restaurer: python manage.py restore_db <fichier>')
        self.stdout.write('Ou: python manage.py restore_db --latest')

    def get_latest_backup(self, backup_dir):
        """Retourne le backup le plus récent"""
        backups = sorted(backup_dir.glob('db_backup_*.gz'), reverse=True)

        if not backups:
            raise CommandError('Aucun backup disponible.')

        return backups[0]

    def restore_database(self, backup_file):
        """Restaure la base de données depuis le fichier de backup"""
        db_path = Path(settings.DATABASES['default']['NAME'])

        self.stdout.write(f'\n🔄 Restauration en cours...')

        # Créer un backup de sécurité de la DB actuelle
        if db_path.exists():
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safety_backup = db_path.parent / f'db_before_restore_{timestamp}.sqlite3'
            shutil.copy2(db_path, safety_backup)
            self.stdout.write(f'   ✓ Backup de sécurité créé: {safety_backup.name}')

        # Décompresser et restaurer
        try:
            with gzip.open(backup_file, 'rb') as f_in:
                with open(db_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            self.stdout.write(self.style.SUCCESS(
                f'\n✅ Base de données restaurée avec succès!'
            ))
            self.stdout.write(f'   Source: {backup_file.name}')
            self.stdout.write(f'   Destination: {db_path}')

        except Exception as e:
            # En cas d'erreur, restaurer le backup de sécurité
            if 'safety_backup' in locals() and safety_backup.exists():
                shutil.copy2(safety_backup, db_path)
                self.stdout.write(self.style.ERROR(
                    f'❌ Erreur lors de la restauration: {e}'
                ))
                self.stdout.write('   La base de données originale a été préservée.')
            raise CommandError(f'Erreur de restauration: {e}')
