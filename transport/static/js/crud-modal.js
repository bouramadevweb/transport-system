/**
 * CRUD Modal Module
 *
 * Module générique pour gérer les modals de création/modification d'entités
 */

class CrudModalManager {
    constructor(config) {
        this.entityName = config.entityName; // Ex: "client", "chauffeur"
        this.entityNameDisplay = config.entityNameDisplay; // Ex: "Client", "Chauffeur"
        this.createUrl = config.createUrl;
        this.updateUrlPattern = config.updateUrlPattern; // Ex: "/clients/{id}/ajax/update/"
        this.listSelector = config.listSelector; // Ex: "#clientTableBody"

        this.modal = null;
        this.modalElement = null;
        this.currentMode = null; // 'create' ou 'update'
        this.currentEntityId = null;

        this.initButtons();
        this.createModal();

        console.log(`✅ CrudModalManager initialized for ${this.entityName}`);
    }

    /**
     * Créer le modal Bootstrap dynamiquement (élément DOM uniquement)
     * L'instance Bootstrap.Modal est créée de façon lazy dans getModal()
     */
    createModal() {
        const modalHtml = `
            <div class="modal fade" id="${this.entityName}CrudModal" tabindex="-1">
                <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
                    <div class="modal-content">
                        <div class="modal-header bg-primary text-white">
                            <h5 class="modal-title" id="${this.entityName}ModalTitle">
                                <i class="fas fa-plus-circle me-2"></i>Nouveau ${this.entityNameDisplay}
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body" id="${this.entityName}ModalBody">
                            <div class="text-center py-5">
                                <div class="spinner-border text-primary" role="status">
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
        this.modalElement = document.getElementById(`${this.entityName}CrudModal`);
        // NE PAS créer new bootstrap.Modal() ici — Bootstrap peut ne pas être
        // encore chargé si le script est différé. On crée l'instance de façon lazy.
    }

    /**
     * Obtenir (ou créer) l'instance Bootstrap.Modal de façon lazy
     */
    getModal() {
        if (!this.modal) {
            if (typeof bootstrap === 'undefined') {
                console.error('❌ bootstrap is not defined! Make sure Bootstrap JS is loaded.');
                return null;
            }
            this.modal = new bootstrap.Modal(this.modalElement);
        }
        return this.modal;
    }

    /**
     * Initialiser les boutons (event delegation)
     */
    initButtons() {
        // Bouton "Créer" (nouveau)
        document.addEventListener('click', (e) => {
            const btn = e.target.closest(`.btn-create-${this.entityName}`);
            if (btn) {
                e.preventDefault();
                this.openCreateModal();
            }
        });

        // Bouton "Modifier" (éditer)
        document.addEventListener('click', (e) => {
            const btn = e.target.closest(`.btn-edit-${this.entityName}`);
            if (btn) {
                e.preventDefault();
                const entityId = btn.dataset[`${this.entityName}Id`];
                if (entityId) {
                    this.openUpdateModal(entityId);
                } else {
                    console.error('Entity ID not found on edit button');
                }
            }
        });
    }

    /**
     * Ouvrir le modal pour créer une nouvelle entité
     */
    async openCreateModal() {
        this.currentMode = 'create';
        this.currentEntityId = null;

        // Mettre à jour le titre
        this.updateModalTitle('create');

        // Afficher le modal avec loading
        const modal = this.getModal();
        if (!modal) return;
        modal.show();
        this.showLoading();

        try {
            const response = await ajaxManager.get(
                this.createUrl,
                {},
                { showLoading: false, showToast: false }
            );

            if (response.success) {
                // Injecter le formulaire dans le modal
                document.getElementById(`${this.entityName}ModalBody`).innerHTML = response.html;

                // Attacher le handler de soumission
                this.attachFormHandler();

                // Initialiser les calculs automatiques pour les contrats
                if (this.entityName === 'contrat' && typeof initContratFormCalculs === 'function') {
                    setTimeout(() => initContratFormCalculs(), 100);
                }
            } else {
                this.showError(response.message || 'Erreur lors du chargement du formulaire');
            }
        } catch (error) {
            console.error('Modal loading error:', error);
            this.showError('Une erreur est survenue lors du chargement');
        }
    }

    /**
     * Ouvrir le modal pour modifier une entité existante
     */
    async openUpdateModal(entityId) {
        this.currentMode = 'update';
        this.currentEntityId = entityId;

        // Mettre à jour le titre
        this.updateModalTitle('update');

        // Afficher le modal avec loading
        const modal = this.getModal();
        if (!modal) return;
        modal.show();
        this.showLoading();

        try {
            const url = this.updateUrlPattern.replace('{id}', entityId);
            const response = await ajaxManager.get(
                url,
                {},
                { showLoading: false, showToast: false }
            );

            if (response.success) {
                // Injecter le formulaire dans le modal
                document.getElementById(`${this.entityName}ModalBody`).innerHTML = response.html;

                // Attacher le handler de soumission
                this.attachFormHandler();

                // Initialiser les calculs automatiques pour les contrats
                if (this.entityName === 'contrat' && typeof initContratFormCalculs === 'function') {
                    setTimeout(() => initContratFormCalculs(), 100);
                }
            } else {
                this.showError(response.message || 'Erreur lors du chargement du formulaire');
            }
        } catch (error) {
            console.error('Modal loading error:', error);
            this.showError('Une erreur est survenue lors du chargement');
        }
    }

    /**
     * Mettre à jour le titre du modal
     */
    updateModalTitle(mode) {
        const titleElement = document.getElementById(`${this.entityName}ModalTitle`);
        if (mode === 'create') {
            titleElement.innerHTML = `<i class="fas fa-plus-circle me-2"></i>Nouveau ${this.entityNameDisplay}`;
        } else {
            titleElement.innerHTML = `<i class="fas fa-edit me-2"></i>Modifier ${this.entityNameDisplay}`;
        }
    }

    /**
     * Attacher le handler au formulaire
     */
    attachFormHandler() {
        const form = document.getElementById(`${this.entityName}Form`);

        if (!form) {
            console.error('Form not found');
            return;
        }

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitForm(form);
        });
    }

    /**
     * Soumettre le formulaire via AJAX
     */
    async submitForm(form) {
        const formData = new FormData(form);

        // Convertir FormData en objet JSON
        const data = {};
        formData.forEach((value, key) => {
            // Gérer les champs multiples (select multiple, checkboxes)
            if (data[key]) {
                if (Array.isArray(data[key])) {
                    data[key].push(value);
                } else {
                    data[key] = [data[key], value];
                }
            } else {
                data[key] = value;
            }
        });

        console.log('📤 Submitting form:', data);

        try {
            let url;
            if (this.currentMode === 'create') {
                url = this.createUrl;
            } else {
                url = this.updateUrlPattern.replace('{id}', this.currentEntityId);
            }

            console.log('🌐 POST to:', url);

            const response = await ajaxManager.post(
                url,
                data,
                { showLoading: false }
            );

            console.log('📥 Response:', response);

            if (response.success) {
                // Succès - afficher le message
                if (typeof toastManager !== 'undefined') {
                    toastManager.success(response.message);
                }

                // Fermer le modal
                const modal = this.getModal();
                if (modal) modal.hide();

                // Rediriger si redirect_url est fourni, sinon rafraîchir
                if (response.redirect_url) {
                    window.location.href = response.redirect_url;
                } else {
                    this.refreshList();
                }
            } else {
                // Erreur mais pas d'exception
                console.warn('❌ Response non-success:', response);
                if (response.html) {
                    // Mettre à jour le formulaire avec les erreurs
                    document.getElementById(`${this.entityName}ModalBody`).innerHTML = response.html;
                    this.attachFormHandler();
                }
                if (typeof toastManager !== 'undefined') {
                    toastManager.error(response.message || 'Veuillez corriger les erreurs');
                }
            }
        } catch (error) {
            console.error('💥 Exception caught:', error);

            // Gérer les erreurs de validation
            if (error.response && error.response.errors) {
                this.showValidationErrors(error.response.errors);
            } else if (error.response && error.response.html) {
                // Si le serveur renvoie du HTML avec les erreurs
                document.getElementById(`${this.entityName}ModalBody`).innerHTML = error.response.html;
                this.attachFormHandler();
                if (typeof toastManager !== 'undefined') {
                    toastManager.error(error.response.message || 'Veuillez corriger les erreurs');
                }
            } else {
                const message = error.response?.message || error.message || 'Une erreur est survenue';
                if (typeof toastManager !== 'undefined') {
                    toastManager.error(message);
                }
            }
        }
    }

    /**
     * Afficher les erreurs de validation dans le formulaire
     */
    showValidationErrors(errors) {
        // Effacer les erreurs précédentes
        document.querySelectorAll('.invalid-feedback').forEach(el => el.remove());
        document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));

        // Afficher les nouvelles erreurs
        for (const [field, messages] of Object.entries(errors)) {
            const input = document.getElementById(`id_${field}`);
            if (input) {
                input.classList.add('is-invalid');

                const errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback';
                errorDiv.textContent = Array.isArray(messages) ? messages.join(', ') : messages;

                input.parentElement.appendChild(errorDiv);
            }
        }

        // Toast général
        if (typeof toastManager !== 'undefined') {
            toastManager.error('Veuillez corriger les erreurs dans le formulaire');
        }
    }

    /**
     * Afficher l'état de chargement
     */
    showLoading() {
        document.getElementById(`${this.entityName}ModalBody`).innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
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
        document.getElementById(`${this.entityName}ModalBody`).innerHTML = `
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
     * Rafraîchir la liste après création/modification
     */
    refreshList() {
        // Option 1: Recharger la page
        window.location.reload();

        // Option 2: Si vous avez un système de recherche AJAX, rafraîchir via AJAX
        // const listManager = window[`${this.entityName}ListManager`];
        // if (listManager && typeof listManager.performSearch === 'function') {
        //     listManager.performSearch('');
        // }
    }
}
