/**
 * Skeleton Loaders Manager - Transport System
 *
 * Gestionnaire de skeleton loaders pour les chargements AJAX
 */

const SkeletonLoader = {
    /**
     * Génère un skeleton pour une table
     * @param {number} rows - Nombre de lignes
     * @param {number} cols - Nombre de colonnes
     * @returns {string} HTML du skeleton
     */
    table(rows = 5, cols = 4) {
        let html = '<div class="skeleton-table">';

        for (let i = 0; i < rows; i++) {
            html += '<div class="skeleton-table-row">';
            for (let j = 0; j < cols; j++) {
                const size = j === 0 ? 'small' : (j === cols - 1 ? 'small' : '');
                html += `<div class="skeleton skeleton-text skeleton-table-cell ${size}"></div>`;
            }
            html += '</div>';
        }

        html += '</div>';
        return html;
    },

    /**
     * Génère un skeleton pour les cartes de statistiques
     * @param {number} count - Nombre de cartes
     * @returns {string} HTML du skeleton
     */
    statCards(count = 4) {
        let html = '<div class="skeleton-dashboard-stats">';

        for (let i = 0; i < count; i++) {
            html += `
                <div class="skeleton-stat-card">
                    <div class="skeleton skeleton-icon"></div>
                    <div class="skeleton skeleton-number"></div>
                    <div class="skeleton skeleton-label"></div>
                </div>
            `;
        }

        html += '</div>';
        return html;
    },

    /**
     * Génère un skeleton pour un graphique
     * @returns {string} HTML du skeleton
     */
    chart() {
        return `
            <div class="skeleton-dashboard-chart">
                <div class="skeleton skeleton-title" style="width: 30%;"></div>
                <div class="skeleton skeleton-chart"></div>
            </div>
        `;
    },

    /**
     * Génère un skeleton pour une liste
     * @param {number} items - Nombre d'éléments
     * @returns {string} HTML du skeleton
     */
    list(items = 5) {
        let html = '<div class="skeleton-list">';

        for (let i = 0; i < items; i++) {
            html += `
                <div class="skeleton-list-item">
                    <div class="skeleton skeleton-avatar"></div>
                    <div class="skeleton-list-content">
                        <div class="skeleton skeleton-text medium"></div>
                        <div class="skeleton skeleton-text short"></div>
                    </div>
                </div>
            `;
        }

        html += '</div>';
        return html;
    },

    /**
     * Génère un skeleton pour un formulaire
     * @param {number} fields - Nombre de champs
     * @returns {string} HTML du skeleton
     */
    form(fields = 4) {
        let html = '<div class="skeleton-form">';

        for (let i = 0; i < fields; i++) {
            html += `
                <div class="skeleton-form-group">
                    <div class="skeleton skeleton-label"></div>
                    <div class="skeleton skeleton-input"></div>
                </div>
            `;
        }

        html += `
            <div class="skeleton-modal-footer">
                <div class="skeleton skeleton-button"></div>
                <div class="skeleton skeleton-button"></div>
            </div>
        `;

        html += '</div>';
        return html;
    },

    /**
     * Génère un skeleton pour les notifications
     * @param {number} count - Nombre de notifications
     * @returns {string} HTML du skeleton
     */
    notifications(count = 3) {
        let html = '<div class="skeleton-notifications">';

        for (let i = 0; i < count; i++) {
            html += `
                <div class="skeleton-notification">
                    <div class="skeleton skeleton-notification-icon"></div>
                    <div class="skeleton-notification-content">
                        <div class="skeleton skeleton-text medium"></div>
                        <div class="skeleton skeleton-text short"></div>
                    </div>
                </div>
            `;
        }

        html += '</div>';
        return html;
    },

    /**
     * Génère un skeleton pour le contenu d'un modal
     * @returns {string} HTML du skeleton
     */
    modal() {
        return `
            <div class="skeleton-modal-content">
                <div class="skeleton-modal-header">
                    <div class="skeleton skeleton-title"></div>
                    <div class="skeleton skeleton-button" style="width: 30px;"></div>
                </div>
                <div class="skeleton-modal-body">
                    ${this.form(4)}
                </div>
            </div>
        `;
    },

    /**
     * Génère un skeleton pour le dashboard complet
     * @returns {string} HTML du skeleton
     */
    dashboard() {
        return `
            <div class="skeleton-dashboard">
                ${this.statCards(4)}
                <div class="row g-4 mt-2">
                    <div class="col-lg-8">
                        ${this.chart()}
                    </div>
                    <div class="col-lg-4">
                        <div class="skeleton-card">
                            <div class="skeleton skeleton-title" style="width: 50%;"></div>
                            ${this.list(4)}
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Génère un skeleton pour une card
     * @returns {string} HTML du skeleton
     */
    card() {
        return `
            <div class="skeleton-card">
                <div class="skeleton skeleton-title"></div>
                <div class="skeleton skeleton-text long"></div>
                <div class="skeleton skeleton-text medium"></div>
                <div class="skeleton skeleton-text short"></div>
            </div>
        `;
    },

    /**
     * Affiche un skeleton dans un élément
     * @param {string|Element} target - Sélecteur ou élément cible
     * @param {string} type - Type de skeleton (table, list, form, etc.)
     * @param {object} options - Options supplémentaires
     */
    show(target, type = 'table', options = {}) {
        const element = typeof target === 'string'
            ? document.querySelector(target)
            : target;

        if (!element) return;

        // Sauvegarder le contenu original
        element._originalContent = element.innerHTML;
        element._originalMinHeight = element.style.minHeight;

        // Définir une hauteur minimale pour éviter le saut
        element.style.minHeight = element.offsetHeight + 'px';

        // Générer le skeleton approprié
        let skeleton;
        switch (type) {
            case 'table':
                skeleton = this.table(options.rows || 5, options.cols || 4);
                break;
            case 'statCards':
                skeleton = this.statCards(options.count || 4);
                break;
            case 'chart':
                skeleton = this.chart();
                break;
            case 'list':
                skeleton = this.list(options.items || 5);
                break;
            case 'form':
                skeleton = this.form(options.fields || 4);
                break;
            case 'notifications':
                skeleton = this.notifications(options.count || 3);
                break;
            case 'modal':
                skeleton = this.modal();
                break;
            case 'dashboard':
                skeleton = this.dashboard();
                break;
            case 'card':
                skeleton = this.card();
                break;
            default:
                skeleton = this.table();
        }

        element.innerHTML = skeleton;
    },

    /**
     * Masque le skeleton et restaure le contenu
     * @param {string|Element} target - Sélecteur ou élément cible
     * @param {string} newContent - Nouveau contenu (optionnel)
     */
    hide(target, newContent = null) {
        const element = typeof target === 'string'
            ? document.querySelector(target)
            : target;

        if (!element) return;

        // Restaurer la hauteur originale
        if (element._originalMinHeight !== undefined) {
            element.style.minHeight = element._originalMinHeight;
        }

        // Mettre le nouveau contenu ou restaurer l'original
        if (newContent !== null) {
            element.innerHTML = newContent;
        } else if (element._originalContent !== undefined) {
            element.innerHTML = element._originalContent;
        }

        // Nettoyer
        delete element._originalContent;
        delete element._originalMinHeight;
    },

    /**
     * Wrapper pour les requêtes AJAX avec skeleton
     * @param {string|Element} target - Élément cible
     * @param {string} type - Type de skeleton
     * @param {Function} asyncFn - Fonction async à exécuter
     * @param {object} options - Options du skeleton
     */
    async wrap(target, type, asyncFn, options = {}) {
        this.show(target, type, options);

        try {
            const result = await asyncFn();
            return result;
        } finally {
            // Le hide sera appelé manuellement avec le nouveau contenu
        }
    }
};

// Intégration automatique avec les requêtes fetch
const originalFetch = window.fetch;
window.fetchWithSkeleton = async function(url, options = {}, skeletonConfig = null) {
    if (skeletonConfig && skeletonConfig.target) {
        SkeletonLoader.show(skeletonConfig.target, skeletonConfig.type || 'table', skeletonConfig.options || {});
    }

    try {
        const response = await originalFetch(url, options);
        return response;
    } finally {
        if (skeletonConfig && skeletonConfig.target && skeletonConfig.autoHide !== false) {
            // Petit délai pour éviter le flash
            setTimeout(() => {
                SkeletonLoader.hide(skeletonConfig.target);
            }, 100);
        }
    }
};

// Export pour utilisation globale
window.SkeletonLoader = SkeletonLoader;
