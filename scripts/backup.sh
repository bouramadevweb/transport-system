#!/bin/bash
#
# Script de sauvegarde automatique pour Transport System
#
# Usage:
#   ./scripts/backup.sh                  # Backup normal
#   ./scripts/backup.sh --with-media     # Backup avec fichiers média
#
# Configuration cron (exemple):
#   # Backup quotidien à 2h du matin, garde 30 jours
#   0 2 * * * /chemin/vers/transport-system/scripts/backup.sh >> /var/log/transport-backup.log 2>&1
#
#   # Backup hebdomadaire avec média le dimanche à 3h
#   0 3 * * 0 /chemin/vers/transport-system/scripts/backup.sh --with-media >> /var/log/transport-backup.log 2>&1
#

# Configuration
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_DIR="${PROJECT_DIR}/backups"
RETENTION_DAYS=30
LOG_FILE="${BACKUP_DIR}/backup.log"

# Activer l'environnement virtuel si présent
if [ -f "${PROJECT_DIR}/venv/bin/activate" ]; then
    source "${PROJECT_DIR}/venv/bin/activate"
elif [ -f "${PROJECT_DIR}/.venv/bin/activate" ]; then
    source "${PROJECT_DIR}/.venv/bin/activate"
fi

# Aller dans le répertoire du projet
cd "${PROJECT_DIR}"

# Créer le répertoire de backup si nécessaire
mkdir -p "${BACKUP_DIR}"

# Log de début
echo "========================================" >> "${LOG_FILE}"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Début de la sauvegarde" >> "${LOG_FILE}"

# Options de backup
BACKUP_OPTS="--cleanup ${RETENTION_DAYS}"

if [ "$1" == "--with-media" ]; then
    BACKUP_OPTS="${BACKUP_OPTS} --include-media"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Mode: Backup complet (DB + média)" >> "${LOG_FILE}"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Mode: Backup base de données uniquement" >> "${LOG_FILE}"
fi

# Exécuter le backup
python manage.py backup_db ${BACKUP_OPTS} >> "${LOG_FILE}" 2>&1

# Vérifier le résultat
if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Sauvegarde terminée avec succès" >> "${LOG_FILE}"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ ERREUR lors de la sauvegarde" >> "${LOG_FILE}"
    # Envoyer une alerte (optionnel - décommenter si configuré)
    # mail -s "ERREUR Backup Transport System" admin@example.com < "${LOG_FILE}"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Fin de la sauvegarde" >> "${LOG_FILE}"
echo "" >> "${LOG_FILE}"
