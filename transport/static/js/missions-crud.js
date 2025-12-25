/**
 * Missions CRUD AJAX Module
 *
 * Gère la création et modification de missions en modal AJAX
 */

class MissionCRUDManager {
    constructor() {
        this.modal = null;
        this.modalElement = null;
        this.init();
        console.log('✅ MissionCRUDManager initialized');
    }

    /**
     * Initialiser les événements
     */
    init() {
        // Bouton de création
        const createBtn = document.querySelector('[data-action="create-mission"]');
        if (createBtn) {
            createBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.openCreateModal();
            });
        }

        // Boutons de modification
        document.querySelectorAll('[data-action="edit-mission"]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const missionId = btn.dataset.missionId;
                this.openEditModal(missionId);
            });
        });
    }

    /**
     * Ouvrir le modal de création
     */
    async openCreateModal() {
        try {
            const response = await ajaxManager.get(
                '/missions/ajax/create-form/',
                {},
                { showLoading: true, showToast: false }
            );

            if (response.success) {
                this.showModal('Créer une mission', response.html, 'create');
            } else {
                toastManager.error(response.message || 'Erreur lors du chargement du formulaire');
            }

        } catch (error) {
            console.error('Error loading create form:', error);
            toastManager.error('Erreur lors du chargement du formulaire');
        }
    }

    /**
     * Ouvrir le modal de modification
     */
    async openEditModal(missionId) {
        try {
            const response = await ajaxManager.get(
                `/missions/${missionId}/ajax/update-form/`,
                {},
                { showLoading: true, showToast: false }
            );

            if (response.success) {
                this.showModal('Modifier la mission', response.html, 'update', missionId);
            } else {
                toastManager.error(response.message || 'Erreur lors du chargement du formulaire');
            }

        } catch (error) {
            console.error('Error loading edit form:', error);
            toastManager.error('Erreur lors du chargement du formulaire');
        }
    }

    /**
     * Afficher le modal avec le formulaire
     */
    showModal(title, htmlContent, mode, missionId = null) {
        // Créer le modal s'il n'existe pas
        if (!this.modalElement) {
            this.modalElement = document.createElement('div');
            this.modalElement.className = 'modal fade';
            this.modalElement.id = 'missionCRUDModal';
            this.modalElement.innerHTML = `
                <div class="modal-dialog modal-lg modal-dialog-scrollable">
                    <div class="modal-content">
                        <div class="modal-header bg-primary text-white">
                            <h5 class="modal-title">
                                <i class="fas fa-route me-2"></i>
                                <span id="modalTitle">${title}</span>
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div id="modalContentContainer"></div>
                    </div>
                </div>
            `;
            document.body.appendChild(this.modalElement);
            this.modal = new bootstrap.Modal(this.modalElement);
        } else {
            // Mettre à jour le titre
            document.getElementById('modalTitle').textContent = title;
        }

        // Injecter le contenu
        document.getElementById('modalContentContainer').innerHTML = htmlContent;

        // Attacher l'événement de soumission
        const form = document.getElementById('missionForm');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                if (mode === 'create') {
                    this.submitCreate();
                } else {
                    this.submitUpdate(missionId);
                }
            });
        }

        // Afficher le modal
        this.modal.show();
    }

    /**
     * Soumettre le formulaire de création
     */
    async submitCreate() {
        try {
            const form = document.getElementById('missionForm');
            const formData = new FormData(form);

            const response = await ajaxManager.post(
                '/missions/ajax/create/',
                formData,
                { showLoading: true, showToast: false }
            );

            if (response.success) {
                toastManager.success(response.message);
                this.modal.hide();

                // Rediriger si une URL est fournie, sinon rafraîchir la page
                setTimeout(() => {
                    if (response.redirect_url) {
                        window.location.href = response.redirect_url;
                    } else {
                        window.location.reload();
                    }
                }, 1000);
            } else {
                // Si le serveur renvoie le HTML avec les erreurs, on le réaffiche
                if (response.html) {
                    document.getElementById('modalContentContainer').innerHTML = response.html;

                    // Réattacher l'événement de soumission
                    const newForm = document.getElementById('missionForm');
                    if (newForm) {
                        newForm.addEventListener('submit', (e) => {
                            e.preventDefault();
                            this.submitCreate();
                        });
                    }
                }

                toastManager.error(response.message || 'Erreur lors de la création');
            }

        } catch (error) {
            console.error('Error creating mission:', error);
            toastManager.error('Erreur lors de la création de la mission');
        }
    }

    /**
     * Soumettre le formulaire de modification
     */
    async submitUpdate(missionId) {
        try {
            const form = document.getElementById('missionForm');
            const formData = new FormData(form);

            const response = await ajaxManager.post(
                `/missions/${missionId}/ajax/update/`,
                formData,
                { showLoading: true, showToast: false }
            );

            if (response.success) {
                toastManager.success(response.message);
                this.modal.hide();

                // Rediriger si une URL est fournie, sinon rafraîchir la page
                setTimeout(() => {
                    if (response.redirect_url) {
                        window.location.href = response.redirect_url;
                    } else {
                        window.location.reload();
                    }
                }, 1000);
            } else {
                // Si le serveur renvoie le HTML avec les erreurs, on le réaffiche
                if (response.html) {
                    document.getElementById('modalContentContainer').innerHTML = response.html;

                    // Réattacher l'événement de soumission
                    const newForm = document.getElementById('missionForm');
                    if (newForm) {
                        newForm.addEventListener('submit', (e) => {
                            e.preventDefault();
                            this.submitUpdate(missionId);
                        });
                    }
                }

                toastManager.error(response.message || 'Erreur lors de la modification');
            }

        } catch (error) {
            console.error('Error updating mission:', error);
            toastManager.error('Erreur lors de la modification de la mission');
        }
    }
}

// Initialiser quand le DOM est prêt
document.addEventListener('DOMContentLoaded', () => {
    // Attendre que ajaxManager soit disponible
    if (typeof ajaxManager !== 'undefined') {
        window.missionCRUDManager = new MissionCRUDManager();
    } else {
        console.error('ajaxManager not found. Make sure ajax-utils.js is loaded first.');
    }
});
