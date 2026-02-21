"""
Commande Django pour sauvegarder la base de données et les fichiers média.

Usage:
    python manage.py backup_db                    # Backup base de données uniquement
    python manage.py backup_db --include-media    # Backup DB + fichiers média
    python manage.py backup_db --cleanup 7        # Supprimer les backups > 7 jours
"""

import os
import shutil
import gzip
from datetime import datetime, timedelta
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = 'Sauvegarde la base de données SQLite et optionnellement les fichiers média'

    def add_arguments(self, parser):
        parser.add_argument(
            '--include-media',
            action='store_true',
            help='Inclure les fichiers média dans la sauvegarde',
        )
        parser.add_argument(
            '--cleanup',
            type=int,
            metavar='DAYS',
            help='Supprimer les sauvegardes plus anciennes que X jours',
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default=None,
            help='Répertoire de destination (défaut: backups/)',
        )

    def handle(self, *args, **options):
        # Créer le répertoire de backup
        if options['output_dir']:
            backup_dir = Path(options['output_dir'])
        else:
            backup_dir = Path(settings.BASE_DIR) / 'backups'

        backup_dir.mkdir(parents=True, exist_ok=True)

        # Timestamp pour le nom du fichier
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # 1. Backup de la base de données
        self.backup_database(backup_dir, timestamp)

        # 2. Backup des médias si demandé
        if options['include_media']:
            self.backup_media(backup_dir, timestamp)

        # 3. Nettoyage des anciens backups si demandé
        if options['cleanup']:
            self.cleanup_old_backups(backup_dir, options['cleanup'])

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Sauvegarde terminée avec succès!'
        ))
        self.stdout.write(f'   Répertoire: {backup_dir}')

    def backup_database(self, backup_dir, timestamp):
        """Sauvegarde la base de données SQLite avec compression"""
        db_path = settings.DATABASES['default']['NAME']

        if not os.path.exists(db_path):
            raise CommandError(f'Base de données non trouvée: {db_path}')

        # Nom du fichier de backup
        backup_filename = f'db_backup_{timestamp}.sqlite3.gz'
        backup_path = backup_dir / backup_filename

        self.stdout.write(f'📦 Sauvegarde de la base de données...')

        # Copier et compresser
        with open(db_path, 'rb') as f_in:
            with gzip.open(backup_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        # Taille du fichier
        size_mb = backup_path.stat().st_size / (1024 * 1024)

        self.stdout.write(self.style.SUCCESS(
            f'   ✓ Base de données sauvegardée: {backup_filename} ({size_mb:.2f} MB)'
        ))

        return backup_path

    def backup_media(self, backup_dir, timestamp):
        """Sauvegarde les fichiers média"""
        media_root = getattr(settings, 'MEDIA_ROOT', None)

        if not media_root or not os.path.exists(media_root):
            self.stdout.write(self.style.WARNING(
                '   ⚠ Répertoire média non trouvé, ignoré.'
            ))
            return None

        # Nom de l'archive
        backup_filename = f'media_backup_{timestamp}.tar.gz'
        backup_path = backup_dir / backup_filename

        self.stdout.write(f'📦 Sauvegarde des fichiers média...')

        # Créer l'archive
        shutil.make_archive(
            str(backup_path).replace('.tar.gz', ''),
            'gztar',
            media_root
        )

        # Taille du fichier
        size_mb = backup_path.stat().st_size / (1024 * 1024)

        self.stdout.write(self.style.SUCCESS(
            f'   ✓ Fichiers média sauvegardés: {backup_filename} ({size_mb:.2f} MB)'
        ))

        return backup_path

    def cleanup_old_backups(self, backup_dir, days):
        """Supprime les sauvegardes plus anciennes que X jours"""
        self.stdout.write(f'🧹 Nettoyage des sauvegardes > {days} jours...')

        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0

        for file_path in backup_dir.glob('*_backup_*.gz'):
            if file_path.stat().st_mtime < cutoff_date.timestamp():
                file_path.unlink()
                deleted_count += 1
                self.stdout.write(f'   ✓ Supprimé: {file_path.name}')

        if deleted_count == 0:
            self.stdout.write('   Aucun ancien backup à supprimer.')
        else:
            self.stdout.write(self.style.SUCCESS(
                f'   ✓ {deleted_count} ancien(s) backup(s) supprimé(s)'
            ))
