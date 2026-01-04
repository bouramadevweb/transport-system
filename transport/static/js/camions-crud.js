/**
 * Camions CRUD AJAX Module
 *
 * Gère la création et modification de camions en modal AJAX
 */

class CamionCRUDManager {
    constructor() {
        this.modal = null;
        this.modalElement = null;
        this.currentForm = null;  // Stocker une référence au formulaire actuel
        this.isSubmitting = false;  // Flag pour empêcher les soumissions multiples
        this.init();
        console.log('✅ CamionCRUDManager initialized');
    }

    /**
     * Initialiser les événements
     */
    init() {
        console.log('🔧 Initializing CamionCRUDManager...');

        // Bouton de création
        const createBtn = document.querySelector('[data-action="create-camion"]');
        console.log('🔍 Create button found:', createBtn);

        if (createBtn) {
            console.log('✅ Attaching click event to create button');
            createBtn.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('🚀 Create button clicked!');
                this.openCreateModal();
            });
        } else {
            console.error('❌ Create button NOT found!');
        }

        // Boutons de modification
        const editBtns = document.querySelectorAll('[data-action="edit-camion"]');
        console.log(`🔍 Edit buttons found: ${editBtns.length}`);

        editBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const camionId = btn.dataset.camionId;
                console.log('✏️ Edit button clicked for camion:', camionId);
                this.openEditModal(camionId);
            });
        });
    }

    /**
     * Ouvrir le modal de création
     */
    async openCreateModal() {
        console.log('📂 Opening create modal...');

        try {
            console.log('🌐 Fetching form from /camions/ajax/create-form/');

            const response = await ajaxManager.get(
                '/camions/ajax/create-form/',
                {},
                { showLoading: true, showToast: false }
            );

            console.log('📥 Response received:', response);

            if (response.success) {
                console.log('✅ Form loaded successfully');
                this.showModal('Créer un camion', response.html, 'create');
            } else {
                console.error('❌ Server returned error:', response.message);
                toastManager.error(response.message || 'Erreur lors du chargement du formulaire');
            }

        } catch (error) {
            console.error('❌ Error loading create form:', error);
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
        console.log('🎨 showModal called, mode:', mode);

        // Créer le modal s'il n'existe pas
        if (!this.modalElement) {
            console.log('🆕 Creating new modal element');
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
            console.log('✅ Modal element created');
        } else {
            // Mettre à jour le titre
            document.getElementById('modalTitle').textContent = title;
            console.log('♻️ Reusing existing modal');
        }

        // Injecter le contenu
        console.log('📝 Injecting HTML content...');
        document.getElementById('modalContentContainer').innerHTML = htmlContent;

        // Attendre un peu pour que le DOM soit mis à jour
        setTimeout(() => {
            // Attacher l'événement de soumission
            const form = document.getElementById('camionForm');
            console.log('🔍 Looking for form after injection:', form);

            if (form) {
                console.log('✅ Form found, attaching submit event');
                console.log('   Form action:', form.action);
                console.log('   Form method:', form.method);

                // Stocker le formulaire actuel
                this.currentForm = form;

                // Attacher le listener avec capture=true pour être sûr de l'intercepter
                form.addEventListener('submit', (e) => {
                    console.log('🎯 SUBMIT EVENT CAPTURED!');
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                    console.log('🔵 Form submit prevented, mode:', mode);

                    // Empêcher les soumissions multiples
                    if (this.isSubmitting) {
                        console.warn('⚠️ Submission already in progress');
                        return;
                    }

                    if (mode === 'create') {
                        this.submitCreate();
                    } else {
                        this.submitUpdate(camionId);
                    }
                }, true);  // true = capture phase

                console.log('✅ Submit event attached successfully');
            } else {
                console.error('❌ Form not found after injection!');
                console.log('Container HTML:', document.getElementById('modalContentContainer').innerHTML.substring(0, 200));
            }
        }, 100);  // Attendre 100ms pour que le DOM soit prêt

        // Afficher le modal
        console.log('🎭 Showing modal...');
        this.modal.show();
    }

    /**
     * Soumettre le formulaire de création
     */
    async submitCreate() {
        try {
            this.isSubmitting = true;

            // Utiliser le formulaire stocké au lieu de le rechercher
            const form = this.currentForm || document.getElementById('camionForm');

            if (!form) {
                console.error('❌ Form not found!');
                toastManager.error('Erreur: formulaire introuvable');
                this.isSubmitting = false;
                return;
            }

            // Vérifier que le formulaire a des champs
            const inputs = form.querySelectorAll('input, select, textarea');
            console.log(`📝 Form has ${inputs.length} input fields`);

            const formData = new FormData(form);

            console.log('📤 Submitting create form...');
            console.log('Form data entries:');
            let hasData = false;
            for (let [key, value] of formData.entries()) {
                console.log(`  ${key}: "${value}"`);
                if (value && value !== '') hasData = true;
            }

            if (!hasData) {
                console.error('❌ FormData is empty!');
                console.log('Form HTML:', form.outerHTML.substring(0, 500));
                toastManager.error('Erreur: les données du formulaire sont vides');
                this.isSubmitting = false;
                return;
            }

            const response = await ajaxManager.post(
                '/camions/ajax/create/',
                formData,
                { showLoading: true, showToast: false }
            );

            console.log('📥 Server response:', response);
            this.isSubmitting = false;

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
                        this.currentForm = newForm;  // Mettre à jour la référence
                        newForm.addEventListener('submit', (e) => {
                            e.preventDefault();
                            e.stopPropagation();

                            if (this.isSubmitting) {
                                console.warn('⚠️ Submission already in progress');
                                return;
                            }

                            this.submitCreate();
                        });
                    }
                }

                toastManager.error(response.message || 'Erreur lors de la création');
            }

        } catch (error) {
            console.error('Error creating camion:', error);
            toastManager.error('Erreur lors de la création du camion');
            this.isSubmitting = false;  // Important: débloquer en cas d'erreur
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
    console.log('🎬 DOMContentLoaded fired for camions-crud.js');
    console.log('🔍 Checking for ajaxManager:', typeof ajaxManager);
    console.log('🔍 Checking for bootstrap:', typeof bootstrap);

    // Attendre que ajaxManager soit disponible
    if (typeof ajaxManager !== 'undefined') {
        console.log('✅ ajaxManager found, creating CamionCRUDManager');
        window.camionCRUDManager = new CamionCRUDManager();

        // Vérifier que le bouton existe vraiment
        setTimeout(() => {
            const btn = document.querySelector('[data-action="create-camion"]');
            console.log('🔍 Final check - button exists:', btn);
            if (btn) {
                console.log('   Button HTML:', btn.outerHTML.substring(0, 100));
            }
        }, 500);
    } else {
        console.error('❌ ajaxManager not found. Make sure ajax-utils.js is loaded first.');
    }
});
