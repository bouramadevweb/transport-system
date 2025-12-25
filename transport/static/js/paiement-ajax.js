/**
 * Paiement AJAX Module
 *
 * Handles AJAX filtering and interaction for payment list page
 */

class PaiementListManager {
    constructor() {
        this.filterForm = document.getElementById('dateFilterForm');
        this.tableBody = document.querySelector('#all tbody');
        this.statsCards = {
            total: document.querySelector('.col-12.col-sm-6.col-lg-4:nth-child(3) h3'),
            validated: document.querySelector('.col-12.col-sm-6.col-lg-4:nth-child(1) h3'),
            pending: document.querySelector('.col-12.col-sm-6.col-lg-4:nth-child(2) h3')
        };
        this.tabBadges = {
            all: document.querySelector('#all-tab'),
            attente: document.querySelector('#attente-tab'),
            valides: document.querySelector('#valides-tab')
        };

        this.init();
    }

    init() {
        if (!this.filterForm) {
            console.warn('Filter form not found');
            return;
        }

        // Intercept form submission
        this.filterForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.applyFilters();
        });

        // Optional: Real-time search (debounced)
        const searchInput = document.getElementById('search');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.applyFilters();
                }, 500); // 500ms debounce
            });
        }

        console.log('✅ PaiementListManager initialized');
    }

    /**
     * Apply filters via AJAX
     */
    async applyFilters() {
        try {
            // Get form data
            const formData = new FormData(this.filterForm);
            const params = {};

            for (const [key, value] of formData.entries()) {
                if (value) {
                    params[key] = value;
                }
            }

            // Make AJAX request
            const response = await ajaxManager.get('/paiement-missions/ajax/filter/', params);

            if (response.success) {
                // Update table rows
                this.tableBody.innerHTML = response.html;

                // Update statistics cards
                this.updateStats({
                    total: response.total_count,
                    validated: response.validated_count,
                    pending: response.pending_count
                });

                // Update tab badges
                this.updateTabBadges({
                    total: response.total_count,
                    validated: response.validated_count,
                    pending: response.pending_count
                });

                // Success feedback
                if (typeof toastManager !== 'undefined') {
                    toastManager.success(`Filtres appliqués: ${response.total_count} paiement(s) trouvé(s)`);
                }
            } else {
                if (typeof toastManager !== 'undefined') {
                    toastManager.error(response.message || 'Erreur lors du filtrage');
                }
            }

        } catch (error) {
            console.error('Filter error:', error);
            // Error is already handled by ajaxManager
        }
    }

    /**
     * Update statistics cards
     */
    updateStats(stats) {
        if (this.statsCards.total) {
            this.statsCards.total.textContent = stats.total;
        }
        if (this.statsCards.validated) {
            this.statsCards.validated.textContent = stats.validated;
        }
        if (this.statsCards.pending) {
            this.statsCards.pending.textContent = stats.pending;
        }
    }

    /**
     * Update tab badges with counts
     */
    updateTabBadges(stats) {
        if (this.tabBadges.all) {
            this.tabBadges.all.innerHTML = `
                <i class="fas fa-list me-1"></i>Tous (${stats.total})
            `;
        }
        if (this.tabBadges.attente) {
            this.tabBadges.attente.innerHTML = `
                <i class="fas fa-clock me-1"></i>En attente (${stats.pending})
            `;
        }
        if (this.tabBadges.valides) {
            this.tabBadges.valides.innerHTML = `
                <i class="fas fa-check-circle me-1"></i>Validés (${stats.validated})
            `;
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Wait for ajaxManager to be available
    if (typeof ajaxManager !== 'undefined') {
        // Expose instance globally so validation modal can refresh the list
        window.paiementListManager = new PaiementListManager();
    } else {
        console.error('ajaxManager not found. Make sure ajax-utils.js is loaded first.');
    }
});
