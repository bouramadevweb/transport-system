/**
 * Validation Modal Module
 *
 * Handles payment validation modal with AJAX
 */

class ValidationModalManager {
    constructor() {
        this.modal = null;
        this.modalElement = null;
        this.currentPaiementId = null;

        this.initButtons();
        this.createModal();
    }

    /**
     * Create Bootstrap modal element
     */
    createModal() {
        // Check if modal already exists
        let existingModal = document.getElementById('validationModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Create modal HTML
        const modalHtml = `
            <div class="modal fade" id="validationModal" tabindex="-1" aria-labelledby="validationModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
                    <div class="modal-content">
                        <div class="modal-header bg-primary text-white">
                            <h5 class="modal-title" id="validationModalLabel">
                                <i class="fas fa-check-circle me-2"></i>Validation du paiement
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body" id="validationModalBody">
                            <div class="text-center py-5">
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">Chargement...</span>
                                </div>
                                <p class="mt-3 text-muted">Chargement des informations...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // Get modal element
        this.modalElement = document.getElementById('validationModal');

        // Initialize Bootstrap modal
        this.modal = new bootstrap.Modal(this.modalElement);

        console.log('✅ Validation modal created');
    }

    /**
     * Initialize validation buttons
     */
    initButtons() {
        // Use event delegation for dynamically added buttons
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('.btn-validate-payment');
            if (btn) {
                e.preventDefault();
                const paiementId = btn.dataset.paiementId;
                if (paiementId) {
                    this.openModal(paiementId);
                }
            }
        });

        console.log('✅ Validation buttons initialized');
    }

    /**
     * Open modal and load content
     */
    async openModal(paiementId) {
        this.currentPaiementId = paiementId;

        // Show modal with loading state
        this.modal.show();

        // Reset modal body with loading spinner
        const modalBody = document.getElementById('validationModalBody');
        modalBody.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Chargement...</span>
                </div>
                <p class="mt-3 text-muted">Chargement des informations...</p>
            </div>
        `;

        try {
            // Load modal content via AJAX
            const response = await ajaxManager.get(
                `/paiement-missions/${paiementId}/ajax/validation/`,
                {},
                { showLoading: false } // Don't show global loading
            );

            if (response.success) {
                // Inject HTML content
                modalBody.innerHTML = response.html;

                // Attach form submit handler if validation is possible
                if (response.can_validate) {
                    this.attachFormHandler();
                }
            } else {
                modalBody.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-circle me-2"></i>
                        ${response.message || 'Erreur lors du chargement'}
                    </div>
                `;
            }

        } catch (error) {
            modalBody.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Une erreur est survenue lors du chargement.
                </div>
            `;
            console.error('Modal loading error:', error);
        }
    }

    /**
     * Attach form submit handler
     */
    attachFormHandler() {
        const form = document.getElementById('validationForm');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.submitValidation();
        });
    }

    /**
     * Submit validation via AJAX
     */
    async submitValidation() {
        if (!this.currentPaiementId) {
            console.error('No paiement ID set');
            return;
        }

        try {
            // Disable submit button
            const submitBtn = document.querySelector('#validationForm button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Validation...';
            }

            // Make AJAX POST request
            const response = await ajaxManager.post(
                `/paiement-missions/${this.currentPaiementId}/ajax/validate/`,
                {},
                { showLoading: false }
            );

            if (response.success) {
                // Success!
                if (typeof toastManager !== 'undefined') {
                    toastManager.success(response.message || 'Paiement validé avec succès!');
                }

                // Close modal
                this.modal.hide();

                // Refresh payment list
                this.refreshPaymentList();
            } else {
                // Show error
                if (typeof toastManager !== 'undefined') {
                    toastManager.error(response.message || 'Erreur lors de la validation');
                }

                // Re-enable button
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="fas fa-check-circle me-2"></i>Valider le paiement';
                }
            }

        } catch (error) {
            console.error('Validation error:', error);

            // Re-enable button
            const submitBtn = document.querySelector('#validationForm button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-check-circle me-2"></i>Valider le paiement';
            }
        }
    }

    /**
     * Refresh payment list after validation
     */
    refreshPaymentList() {
        // If PaiementListManager exists (from paiement-ajax.js), trigger filter
        if (typeof window.paiementListManager !== 'undefined') {
            window.paiementListManager.applyFilters();
        } else {
            // Otherwise, reload page
            window.location.reload();
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Wait for required dependencies
    if (typeof ajaxManager !== 'undefined' && typeof bootstrap !== 'undefined') {
        window.validationModalManager = new ValidationModalManager();
    } else {
        console.error('ValidationModalManager requires ajaxManager and Bootstrap');
    }
});
