/**
 * Camions CRUD AJAX Module
 *
 * Gère la création et modification de camions en modal AJAX
 */

class CamionCRUDManager {
    constructor() {
        this.modal = null;
        this.modalElement = null;
        this.init();
        console.log('✅ CamionCRUDManager initialized');
    }

    /**
     * Initialiser les événements
     */
    init() {
        // Bouton de création
        const createBtn = document.querySelector('[data-action="create-camion"]');
        if (createBtn) {
            createBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.openCreateModal();
            });
        }

        // Boutons de modification
        document.querySelectorAll('[data-action="edit-camion"]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const camionId = btn.dataset.camionId;
                this.openEditModal(camionId);
            });
        });
    }

    /**
     * Ouvrir le modal de création
     */
    async openCreateModal() {
        try {
            const response = await ajaxManager.get(
                '/camions/ajax/create-form/',
                {},
                { showLoading: true, showToast: false }
            );

            if (response.success) {
                this.showModal('Créer un camion', response.html, 'create');
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
    async openEditModal(camionId) {
        try {
            const response = await ajaxManager.get(
                `/camions/${camionId}/ajax/update-form/`,
                {},
                { showLoading: true, showToast: false }
            );

            if (response.success) {
                this.showModal('Modifier le camion', response.html, 'update', camionId);
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
    showModal(title, htmlContent, mode, camionId = null) {
        // Créer le modal s'il n'existe pas
        if (!this.modalElement) {
            this.modalElement = document.createElement('div');
            this.modalElement.className = 'modal fade';
            this.modalElement.id = 'camionCRUDModal';
            this.modalElement.innerHTML = `
                <div class="modal-dialog modal-lg modal-dialog-scrollable">
                    <div class="modal-content">
                        <div class="modal-header bg-success text-white">
                            <h5 class="modal-title">
                                <i class="fas fa-truck me-2"></i>
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
        const form = document.getElementById('camionForm');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                if (mode === 'create') {
                    this.submitCreate();
                } else {
                    this.submitUpdate(camionId);
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
            const form = document.getElementById('camionForm');
            const formData = new FormData(form);

            const response = await ajaxManager.post(
                '/camions/ajax/create/',
                formData,
                { showLoading: true, showToast: false }
            );

            if (response.success) {
                toastManager.success(response.message);
                this.modal.hide();

                // Rafraîchir la page pour afficher le nouveau camion
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                // Si le serveur renvoie le HTML avec les erreurs, on le réaffiche
                if (response.html) {
                    document.getElementById('modalContentContainer').innerHTML = response.html;

                    // Réattacher l'événement de soumission
                    const newForm = document.getElementById('camionForm');
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
            console.error('Error creating camion:', error);
            toastManager.error('Erreur lors de la création du camion');
        }
    }

    /**
     * Soumettre le formulaire de modification
     */
    async submitUpdate(camionId) {
        try {
            const form = document.getElementById('camionForm');
            const formData = new FormData(form);

            const response = await ajaxManager.post(
                `/camions/${camionId}/ajax/update/`,
                formData,
                { showLoading: true, showToast: false }
            );

            if (response.success) {
                toastManager.success(response.message);
                this.modal.hide();

                // Rafraîchir la page pour afficher les modifications
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                // Si le serveur renvoie le HTML avec les erreurs, on le réaffiche
                if (response.html) {
                    document.getElementById('modalContentContainer').innerHTML = response.html;

                    // Réattacher l'événement de soumission
                    const newForm = document.getElementById('camionForm');
                    if (newForm) {
                        newForm.addEventListener('submit', (e) => {
                            e.preventDefault();
                            this.submitUpdate(camionId);
                        });
                    }
                }

                toastManager.error(response.message || 'Erreur lors de la modification');
            }

        } catch (error) {
            console.error('Error updating camion:', error);
            toastManager.error('Erreur lors de la modification du camion');
        }
    }
}

// Initialiser quand le DOM est prêt
document.addEventListener('DOMContentLoaded', () => {
    // Attendre que ajaxManager soit disponible
    if (typeof ajaxManager !== 'undefined') {
        window.camionCRUDManager = new CamionCRUDManager();
    } else {
        console.error('ajaxManager not found. Make sure ajax-utils.js is loaded first.');
    }
});
