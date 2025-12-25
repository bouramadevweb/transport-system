/**
 * Notifications AJAX Module
 *
 * Gère les notifications en temps réel sans rechargement de page
 */

class NotificationsManager {
    constructor() {
        this.notificationBadge = document.querySelector('.notification-badge');
        this.notificationList = document.querySelector('.notification-list');
        this.refreshInterval = null;

        this.init();
        console.log('✅ NotificationsManager initialized');
    }

    /**
     * Initialiser les événements
     */
    init() {
        // Événement sur chaque notification item pour marquer comme lu au clic
        this.attachNotificationClickHandlers();

        // Bouton "Tout marquer comme lu"
        const markAllBtn = document.querySelector('[onclick="markAllAsRead()"]');
        if (markAllBtn) {
            markAllBtn.removeAttribute('onclick');
            markAllBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.markAllAsRead();
            });
        }

        // Rafraîchissement périodique des notifications (toutes les 30 secondes)
        this.startAutoRefresh(30000);
    }

    /**
     * Attacher les handlers de clic aux notifications
     */
    attachNotificationClickHandlers() {
        document.querySelectorAll('.notification-item.unread').forEach(item => {
            item.addEventListener('click', (e) => {
                // Trouver l'ID de la notification (on doit l'ajouter au HTML)
                const notificationId = item.dataset.notificationId;
                if (notificationId) {
                    this.markAsRead(notificationId, item);
                }
            });
        });
    }

    /**
     * Marquer une notification comme lue
     */
    async markAsRead(notificationId, itemElement) {
        try {
            const response = await ajaxManager.post(
                `/notifications/${notificationId}/ajax/mark-read/`,
                {},
                { showLoading: false, showToast: false }
            );

            if (response.success) {
                // Retirer la classe unread
                itemElement.classList.remove('unread');

                // Mettre à jour le badge
                this.updateBadge(response.unread_count);

                // Petit toast discret
                if (typeof toastManager !== 'undefined') {
                    toastManager.success('Notification marquée comme lue', { duration: 2000 });
                }
            }
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    }

    /**
     * Marquer toutes les notifications comme lues
     */
    async markAllAsRead() {
        try {
            const response = await ajaxManager.post(
                '/notifications/ajax/mark-all-read/',
                {},
                { showLoading: false }
            );

            if (response.success) {
                // Retirer toutes les classes unread
                document.querySelectorAll('.notification-item.unread').forEach(item => {
                    item.classList.remove('unread');
                });

                // Mettre à jour le badge
                this.updateBadge(0);

                // Toast de succès
                if (typeof toastManager !== 'undefined') {
                    toastManager.success(response.message);
                }
            }
        } catch (error) {
            console.error('Error marking all notifications as read:', error);
            if (typeof toastManager !== 'undefined') {
                toastManager.error('Erreur lors du marquage des notifications');
            }
        }
    }

    /**
     * Mettre à jour le badge de compteur
     */
    updateBadge(count) {
        if (count > 0) {
            if (this.notificationBadge) {
                this.notificationBadge.textContent = count;
                this.notificationBadge.style.display = '';
            } else {
                // Créer le badge s'il n'existe pas
                const notificationBtn = document.getElementById('notificationBtn');
                if (notificationBtn) {
                    const badge = document.createElement('span');
                    badge.className = 'notification-badge';
                    badge.textContent = count;
                    notificationBtn.appendChild(badge);
                    this.notificationBadge = badge;
                }
            }
        } else {
            // Cacher le badge s'il n'y a plus de notifications
            if (this.notificationBadge) {
                this.notificationBadge.style.display = 'none';
            }
        }
    }

    /**
     * Rafraîchir les notifications depuis le serveur
     */
    async refreshNotifications() {
        try {
            const response = await ajaxManager.get(
                '/notifications/ajax/get/',
                {},
                { showLoading: false, showToast: false }
            );

            if (response.success) {
                // Mettre à jour le badge
                this.updateBadge(response.unread_count);

                // Mettre à jour la liste (optionnel - peut causer des problèmes d'UX)
                // this.updateNotificationList(response.notifications);
            }
        } catch (error) {
            console.error('Error refreshing notifications:', error);
        }
    }

    /**
     * Mettre à jour la liste des notifications
     */
    updateNotificationList(notifications) {
        if (!this.notificationList) return;

        if (notifications.length === 0) {
            this.notificationList.innerHTML = `
                <div class="notification-item">
                    <div class="notification-content text-center py-3">
                        <i class="fas fa-bell-slash text-muted fa-2x mb-2"></i>
                        <p class="text-muted mb-0">Aucune notification</p>
                    </div>
                </div>
            `;
            return;
        }

        let html = '';
        notifications.forEach(notif => {
            const unreadClass = !notif.is_read ? 'unread' : '';
            html += `
                <div class="notification-item ${unreadClass}" data-notification-id="${notif.id}">
                    <i class="fas fa-${notif.icon} text-${notif.color}"></i>
                    <div class="notification-content">
                        <p><strong>${notif.title}</strong></p>
                        <span class="text-muted">${notif.timesince}</span>
                    </div>
                </div>
            `;
        });

        this.notificationList.innerHTML = html;

        // Réattacher les handlers
        this.attachNotificationClickHandlers();
    }

    /**
     * Démarrer le rafraîchissement automatique
     */
    startAutoRefresh(interval) {
        // Rafraîchir immédiatement
        this.refreshNotifications();

        // Puis rafraîchir périodiquement
        this.refreshInterval = setInterval(() => {
            this.refreshNotifications();
        }, interval);
    }

    /**
     * Arrêter le rafraîchissement automatique
     */
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
}

// Fonction globale pour compatibilité (appelée depuis le template)
function markAllAsRead() {
    if (window.notificationsManager) {
        window.notificationsManager.markAllAsRead();
    }
}

// Initialiser quand le DOM est prêt
document.addEventListener('DOMContentLoaded', () => {
    // Attendre que ajaxManager soit disponible
    if (typeof ajaxManager !== 'undefined') {
        window.notificationsManager = new NotificationsManager();
    } else {
        console.error('ajaxManager not found. Make sure ajax-utils.js is loaded first.');
    }
});
