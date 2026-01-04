/**
 * Camions CRUD - Version simplifiée et robuste
 */

(function() {
    'use strict';

    console.log('🚀 Camions CRUD Simple - Initializing...');

    // Helper pour récupérer le cookie CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Attendre que le DOM et les dépendances soient prêts
    function init() {
        console.log('📋 Init function called');

        // Vérifier les dépendances
        if (typeof bootstrap === 'undefined') {
            console.error('❌ bootstrap not found!');
            return;
        }
        if (typeof toastManager === 'undefined') {
            console.error('❌ toastManager not found!');
            return;
        }
        if (typeof loadingManager === 'undefined') {
            console.error('❌ loadingManager not found!');
            return;
        }

        console.log('✅ All dependencies found');

        // Trouver le bouton de création
        const createBtn = document.querySelector('[data-action="create-camion"]');
        console.log('🔍 Create button:', createBtn);

        if (!createBtn) {
            console.warn('⚠️ No create button found on this page');
            return;
        }

        console.log('✅ Create button found, attaching event');

        // Attacher l'événement de clic
        createBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('🎯 Create button clicked!');
            openCreateModal();
        });

        console.log('✅ Event attached successfully');
    }

    // Ouvrir le modal de création
    async function openCreateModal() {
        console.log('📂 Opening create modal...');

        try {
            // Charger le formulaire avec fetch direct
            console.log('🌐 Fetching form from server...');

            loadingManager.show();

            const fetchResponse = await fetch('/camions/ajax/create-form/', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            });

            const response = await fetchResponse.json();
            loadingManager.hide();

            console.log('📥 Response received:', response);

            if (!response || !response.success) {
                console.error('❌ Invalid response from server');
                toastManager.error('Erreur lors du chargement du formulaire');
                return;
            }

            console.log('✅ Form HTML received, creating modal...');

            // Créer ou récupérer le modal
            let modalEl = document.getElementById('camionModal');
            if (!modalEl) {
                console.log('🆕 Creating new modal element');
                modalEl = document.createElement('div');
                modalEl.id = 'camionModal';
                modalEl.className = 'modal fade';
                modalEl.innerHTML = `
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header bg-success text-white">
                                <h5 class="modal-title">
                                    <i class="fas fa-truck me-2"></i>
                                    Créer un camion
                                </h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                            </div>
                            <div id="camionModalBody"></div>
                        </div>
                    </div>
                `;
                document.body.appendChild(modalEl);
            }

            // Injecter le formulaire
            console.log('📝 Injecting form HTML...');
            const modalBody = document.getElementById('camionModalBody');
            modalBody.innerHTML = response.html;

            // Créer l'instance Bootstrap Modal
            const modal = new bootstrap.Modal(modalEl);

            // Attacher l'événement submit au formulaire
            setTimeout(() => {
                const form = document.getElementById('camionForm');
                console.log('🔍 Form after injection:', form);

                if (!form) {
                    console.error('❌ Form not found after injection!');
                    return;
                }

                console.log('✅ Form found, attaching submit handler');

                // Retirer les anciens listeners
                const newForm = form.cloneNode(true);
                form.parentNode.replaceChild(newForm, form);

                // Attacher le submit
                newForm.addEventListener('submit', async function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();

                    console.log('🎯 FORM SUBMITTED!');

                    await submitForm(newForm, modal);
                }, {capture: true});

                console.log('✅ Submit handler attached');
            }, 50);

            // Afficher le modal
            console.log('🎭 Showing modal...');
            modal.show();

        } catch (error) {
            console.error('❌ Error opening modal:', error);
            toastManager.error('Erreur lors de l\'ouverture du formulaire');
        }
    }

    // Soumettre le formulaire
    async function submitForm(form, modal) {
        console.log('📤 Submitting form...');

        const formData = new FormData(form);

        // Afficher les données
        console.log('Form data:');
        for (let [key, value] of formData.entries()) {
            console.log(`  ${key}: "${value}"`);
        }

        try {
            // UTILISER FETCH DIRECTEMENT au lieu de ajaxManager
            console.log('🚀 Using direct fetch with FormData...');

            loadingManager.show();

            const fetchResponse = await fetch('/camions/ajax/create/', {
                method: 'POST',
                body: formData,  // FormData directement, pas de JSON
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            });

            const response = await fetchResponse.json();
            loadingManager.hide();

            console.log('📥 Submit response:', response);

            if (response.success) {
                console.log('✅ Camion created successfully!');
                toastManager.success(response.message || 'Camion créé avec succès');
                modal.hide();

                // Recharger la page après 1 seconde
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                console.error('❌ Server returned error:', response.message);
                toastManager.error(response.message || 'Erreur lors de la création');

                // Si le serveur renvoie un nouveau HTML avec les erreurs
                if (response.html) {
                    console.log('📝 Updating form with errors...');
                    document.getElementById('camionModalBody').innerHTML = response.html;

                    // Réattacher le submit
                    setTimeout(() => {
                        const newForm = document.getElementById('camionForm');
                        if (newForm) {
                            newForm.addEventListener('submit', async function(e) {
                                e.preventDefault();
                                e.stopPropagation();
                                await submitForm(newForm, modal);
                            }, {capture: true});
                        }
                    }, 50);
                }
            }
        } catch (error) {
            console.error('❌ Error submitting form:', error);
            toastManager.error('Erreur lors de l\'envoi du formulaire');
        }
    }

    // Initialiser au chargement
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
