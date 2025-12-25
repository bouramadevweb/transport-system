/**
 * Dashboard AJAX Module
 *
 * Gère les filtres de date et met à jour les graphiques et statistiques en temps réel
 */

class DashboardManager {
    constructor() {
        this.filterForm = document.getElementById('dashboardFilterForm');
        this.charts = {};

        if (!this.filterForm) {
            console.warn('Dashboard filter form not found');
            return;
        }

        this.init();
        console.log('✅ DashboardManager initialized');
    }

    /**
     * Initialiser les événements
     */
    init() {
        // Intercepter la soumission du formulaire
        this.filterForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.applyFilters();
        });

        // Boutons de filtres rapides
        document.querySelectorAll('.quick-filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const days = btn.dataset.days;
                this.setQuickFilter(days);
            });
        });
    }

    /**
     * Appliquer les filtres via AJAX
     */
    async applyFilters() {
        try {
            // Obtenir les données du formulaire
            const formData = new FormData(this.filterForm);
            const params = {};

            for (const [key, value] of formData.entries()) {
                if (value) {
                    params[key] = value;
                }
            }

            // Afficher un indicateur de chargement
            this.showLoading();

            // Faire la requête AJAX
            const response = await ajaxManager.get(
                '/dashboard/ajax/filter/',
                params,
                { showLoading: false, showToast: false }
            );

            if (response.success) {
                // Mettre à jour toutes les statistiques et graphiques
                this.updateStats(response.stats);
                this.updateMissionsChart(response.mission_par_statut);
                this.updatePaiementsChart(response.paiements_mois_labels, response.paiements_mois_values);
                this.updateReparationsChart(response.reparation_labels, response.reparation_values);
                this.updateEntreprisesChart(response.entreprises_stats);
                this.updateRevenus(response.revenus_mois_actuel);
                this.updateAlertes(response.missions_en_retard);

                // Toast de succès
                if (typeof toastManager !== 'undefined') {
                    toastManager.success('Dashboard mis à jour');
                }
            } else {
                if (typeof toastManager !== 'undefined') {
                    toastManager.error(response.message || 'Erreur lors du filtrage');
                }
            }

        } catch (error) {
            console.error('Filter error:', error);
            if (typeof toastManager !== 'undefined') {
                toastManager.error('Une erreur est survenue');
            }
        }
    }

    /**
     * Afficher un indicateur de chargement
     */
    showLoading() {
        // Ajouter une classe de chargement aux cartes
        document.querySelectorAll('.card').forEach(card => {
            card.style.opacity = '0.6';
        });
    }

    /**
     * Mettre à jour les statistiques générales
     */
    updateStats(stats) {
        // Remettre l'opacité normale
        document.querySelectorAll('.card').forEach(card => {
            card.style.opacity = '1';
        });

        // Mettre à jour chaque statistique
        const statElements = {
            chauffeurs: document.querySelector('[data-stat="chauffeurs"]'),
            camions: document.querySelector('[data-stat="camions"]'),
            missions: document.querySelector('[data-stat="missions"]'),
            missions_en_cours: document.querySelector('[data-stat="missions_en_cours"]'),
            missions_terminees: document.querySelector('[data-stat="missions_terminees"]'),
            reparations: document.querySelector('[data-stat="reparations"]'),
            paiements: document.querySelector('[data-stat="paiements"]'),
            clients: document.querySelector('[data-stat="clients"]'),
            affectations: document.querySelector('[data-stat="affectations"]')
        };

        for (const [key, element] of Object.entries(statElements)) {
            if (element && stats[key] !== undefined) {
                // Animation du compteur
                this.animateCounter(element, stats[key]);
            }
        }
    }

    /**
     * Animer un compteur
     */
    animateCounter(element, targetValue) {
        const currentValue = parseInt(element.textContent.replace(/[^0-9]/g, '')) || 0;
        const duration = 500; // ms
        const steps = 20;
        const increment = (targetValue - currentValue) / steps;
        let current = currentValue;
        let step = 0;

        const timer = setInterval(() => {
            step++;
            current += increment;

            if (step >= steps) {
                element.textContent = this.formatNumber(targetValue);
                clearInterval(timer);
            } else {
                element.textContent = this.formatNumber(Math.round(current));
            }
        }, duration / steps);
    }

    /**
     * Formater un nombre
     */
    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    /**
     * Mettre à jour le graphique des missions
     */
    updateMissionsChart(missionData) {
        if (!window.missionsChartInstance) return;

        const colorMap = {
            'En cours': '#3b82f6',
            'en cours': '#3b82f6',
            'Terminée': '#10b981',
            'terminée': '#10b981',
            'Terminee': '#10b981',
            'Annulée': '#ef4444',
            'annulée': '#ef4444',
            'Annulee': '#ef4444'
        };

        const labels = missionData.map(item => item.statut);
        const data = missionData.map(item => item.total);
        const colors = labels.map(statut => colorMap[statut] || '#6b7280');

        window.missionsChartInstance.data.labels = labels;
        window.missionsChartInstance.data.datasets[0].data = data;
        window.missionsChartInstance.data.datasets[0].backgroundColor = colors;
        window.missionsChartInstance.update();
    }

    /**
     * Mettre à jour le graphique des paiements
     */
    updatePaiementsChart(labels, values) {
        if (!window.paiementsChartInstance) return;

        window.paiementsChartInstance.data.labels = labels;
        window.paiementsChartInstance.data.datasets[0].data = values;
        window.paiementsChartInstance.update();
    }

    /**
     * Mettre à jour le graphique des réparations
     */
    updateReparationsChart(labels, values) {
        if (!window.reparationsChartInstance) return;

        const colors = [
            '#f59e0b', '#3b82f6', '#10b981', '#ef4444', '#8b5cf6',
            '#ec4899', '#14b8a6', '#f97316', '#6366f1', '#84cc16'
        ];

        window.reparationsChartInstance.data.labels = labels;
        window.reparationsChartInstance.data.datasets[0].data = values;
        window.reparationsChartInstance.data.datasets[0].backgroundColor = colors.slice(0, labels.length);
        window.reparationsChartInstance.update();
    }

    /**
     * Mettre à jour le graphique des entreprises
     */
    updateEntreprisesChart(entreprisesStats) {
        if (!window.entreprisesChartInstance) return;

        const labels = entreprisesStats.map(e => e.nom);
        const chauffeurs = entreprisesStats.map(e => e.chauffeurs);
        const camions = entreprisesStats.map(e => e.camions);

        window.entreprisesChartInstance.data.labels = labels;
        window.entreprisesChartInstance.data.datasets[0].data = chauffeurs;
        window.entreprisesChartInstance.data.datasets[1].data = camions;
        window.entreprisesChartInstance.update();
    }

    /**
     * Mettre à jour les revenus
     */
    updateRevenus(revenus) {
        const revenusElement = document.querySelector('[data-stat="revenus"]');
        if (revenusElement) {
            revenusElement.textContent = revenus.toLocaleString('fr-FR') + ' FCFA';
        }
    }

    /**
     * Mettre à jour les alertes
     */
    updateAlertes(missionsEnRetard) {
        const alertElement = document.querySelector('[data-stat="missions_retard"]');
        if (alertElement) {
            alertElement.textContent = missionsEnRetard;
        }
    }

    /**
     * Définir un filtre rapide (30j, 90j, etc.)
     */
    setQuickFilter(days) {
        const today = new Date();
        const startDate = new Date();
        startDate.setDate(today.getDate() - parseInt(days));

        const formatDate = (date) => {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
        };

        document.getElementById('date_debut').value = formatDate(startDate);
        document.getElementById('date_fin').value = formatDate(today);

        // Appliquer automatiquement
        this.applyFilters();
    }
}

// Initialiser quand le DOM est prêt
document.addEventListener('DOMContentLoaded', () => {
    // Attendre que ajaxManager soit disponible
    if (typeof ajaxManager !== 'undefined') {
        window.dashboardManager = new DashboardManager();
    } else {
        console.error('ajaxManager not found. Make sure ajax-utils.js is loaded first.');
    }
});
