/**
 * Terminer Mission Modal Module
 *
 * Gère le modal AJAX pour terminer une mission avec calcul des pénalités en temps réel
 */

class TerminerMissionModalManager {
    constructor() {
        this.modal = null;
        this.modalElement = null;
        this.currentMissionId = null;
        this.requireConfirmation = false;
        this.initButtons();
        this.createModal();
    }

    /**
     * Créer le modal Bootstrap dynamiquement
     */
    createModal() {
        const modalHtml = `
            <div class="modal fade" id="terminerMissionModal" tabindex="-1">
                <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
                    <div class="modal-content">
                        <div class="modal-header bg-success text-white">
                            <h5 class="modal-title">
                                <i class="fas fa-flag-checkered me-2"></i>Terminer la mission
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body" id="terminerMissionModalBody">
                            <div class="text-center py-5">
                                <div class="spinner-border text-success" role="status">
                                    <span class="visually-hidden">Chargement...</span>
                                </div>
                                <p class="mt-3 text-muted">Chargement...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
        this.modalElement = document.getElementById('terminerMissionModal');
        this.modal = new bootstrap.Modal(this.modalElement);

        console.log('✅ TerminerMissionModalManager initialized');
    }

    /**
     * Initialiser les boutons de terminer mission (event delegation)
     */
    initButtons() {
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('.btn-terminer-mission');
            if (btn) {
                e.preventDefault();
                const missionId = btn.dataset.missionId;
                if (missionId) {
                    this.openModal(missionId);
                } else {
                    console.error('Mission ID not found on button');
                }
            }
        });
    }

    /**
     * Ouvrir le modal et charger le contenu via AJAX
     */
    async openModal(missionId) {
        this.currentMissionId = missionId;
        this.requireConfirmation = false;

        // Afficher le modal avec loading
        this.modal.show();
        this.showLoading();

        try {
            const response = await ajaxManager.get(
                `/missions/${missionId}/ajax/terminer/`,
                {},
                { showLoading: false, showToast: false }
            );

            if (response.success) {
                // Injecter le HTML dans le modal
                document.getElementById('terminerMissionModalBody').innerHTML = response.html;

                // Attacher le handler de soumission du formulaire
                this.attachFormHandler();
            } else {
                this.showError(response.message || 'Erreur lors du chargement du modal');
            }
        } catch (error) {
            console.error('Modal loading error:', error);
            this.showError('Une erreur est survenue lors du chargement');
        }
    }

    /**
     * Attacher le handler au formulaire
     */
    attachFormHandler() {
        const form = document.getElementById('terminerMissionForm');
        const confirmRetardBtn = document.getElementById('confirmRetardBtn');

        if (!form) {
            console.error('Form not found');
            return;
        }

        // Soumission normale du formulaire
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitMission(false);
        });

        // Bouton de confirmation pour retard
        if (confirmRetardBtn) {
            confirmRetardBtn.addEventListener('click', () => {
                this.submitMission(true);
            });
        }
    }

    /**
     * Soumettre la terminaison de mission
     */
    async submitMission(force = false) {
        const form = document.getElementById('terminerMissionForm');
        const dateRetour = document.getElementById('dateRetour').value;

        if (!dateRetour) {
            if (typeof toastManager !== 'undefined') {
                toastManager.error('Veuillez sélectionner une date de retour');
            }
            return;
        }

        try {
            const response = await ajaxManager.post(
                `/missions/${this.currentMissionId}/ajax/terminer-execute/`,
                {
                    date_retour: dateRetour,
                    force: force
                },
                { showLoading: false }
            );

            if (response.success) {
                // Succès - afficher le message et fermer le modal
                if (typeof toastManager !== 'undefined') {
                    if (response.en_retard) {
                        toastManager.warning(response.message);
                    } else {
                        toastManager.success(response.message);
                    }
                }

                // Fermer le modal
                this.modal.hide();

                // Rafraîchir la liste des missions
                this.refreshMissionList();
            }
        } catch (error) {
            // Vérifier si c'est une demande de confirmation
            if (error.response && error.response.require_confirmation) {
                this.showConfirmationButtons();
                if (typeof toastManager !== 'undefined') {
                    toastManager.warning(error.response.message || 'Confirmation requise pour ce retard');
                }
            } else {
                // Autre erreur
                const message = error.response?.message || 'Une erreur est survenue';
                if (typeof toastManager !== 'undefined') {
                    toastManager.error(message);
                }
            }
        }
    }

    /**
     * Afficher les boutons de confirmation pour retard
     */
    showConfirmationButtons() {
        const normalSubmit = document.getElementById('normalSubmit');
        const retardSubmit = document.getElementById('retardSubmit');

        if (normalSubmit && retardSubmit) {
            normalSubmit.classList.add('d-none');
            retardSubmit.classList.remove('d-none');
        }
    }

    /**
     * Afficher l'état de chargement
     */
    showLoading() {
        document.getElementById('terminerMissionModalBody').innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-success" role="status">
                    <span class="visually-hidden">Chargement...</span>
                </div>
                <p class="mt-3 text-muted">Chargement...</p>
            </div>
        `;
    }

    /**
     * Afficher une erreur
     */
    showError(message) {
        document.getElementById('terminerMissionModalBody').innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-exclamation-circle text-danger fa-3x mb-3"></i>
                <p class="text-danger mb-0">${message}</p>
            </div>
        `;

        if (typeof toastManager !== 'undefined') {
            toastManager.error(message);
        }
    }

    /**
     * Rafraîchir la liste des missions (recharger la page pour simplifier)
     */
    refreshMissionList() {
        // Option 1: Recharger la page
        window.location.reload();

        // Option 2: Si vous avez un gestionnaire de liste AJAX, l'appeler ici
        // if (typeof window.missionListManager !== 'undefined') {
        //     window.missionListManager.refreshList();
        // }
    }
}

// Initialiser quand le DOM est prêt
document.addEventListener('DOMContentLoaded', () => {
    // Attendre que ajaxManager soit disponible
    if (typeof ajaxManager !== 'undefined') {
        // Exposer l'instance globalement
        window.terminerMissionModalManager = new TerminerMissionModalManager();
    } else {
        console.error('ajaxManager not found. Make sure ajax-utils.js is loaded first.');
    }
});
