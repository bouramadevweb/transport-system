/**
 * Chauffeurs CRUD - Gestion des chauffeurs via modal AJAX
 * Pattern identique à camions-crud-simple.js (qui fonctionne)
 */

(function() {
    'use strict';

    console.log('🚀 Chauffeurs CRUD - Initializing...');

    let currentModal = null;
    let currentMode = 'create';
    let currentChauffeurId = null;

    // Wrapper sécurisé pour toastManager (optionnel)
    function showToast(type, msg) {
        if (typeof toastManager !== 'undefined') toastManager[type](msg);
    }

    // Helper CSRF token
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

    function init() {
        console.log('📋 Chauffeurs CRUD - Init...');

        if (typeof bootstrap === 'undefined') {
            console.error('❌ bootstrap not found!');
            return;
        }

        console.log('✅ Bootstrap found, attaching event listeners');

        // Event delegation - bouton créer
        document.addEventListener('click', function(e) {
            const createBtn = e.target.closest('.btn-create-chauffeur');
            if (createBtn) {
                e.preventDefault();
                console.log('🎯 Create chauffeur button clicked!');
                openCreateModal();
            }

            const editBtn = e.target.closest('.btn-edit-chauffeur');
            if (editBtn) {
                e.preventDefault();
                const chauffeurId = editBtn.dataset.chauffeurId;
                console.log('🎯 Edit chauffeur button clicked! ID:', chauffeurId);
                if (chauffeurId) {
                    openEditModal(chauffeurId);
                }
            }
        });

        console.log('✅ Event listeners attached');
    }

    function getOrCreateModal() {
        let modalEl = document.getElementById('chauffeurModal');
        if (!modalEl) {
            modalEl = document.createElement('div');
            modalEl.id = 'chauffeurModal';
            modalEl.className = 'modal fade';
            modalEl.setAttribute('tabindex', '-1');
            modalEl.innerHTML = `
                <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
                    <div class="modal-content">
                        <div class="modal-header bg-primary text-white">
                            <h5 class="modal-title" id="chauffeurModalTitle">
                                <i class="fas fa-id-card me-2"></i>
                                <span id="chauffeurModalTitleText">Chauffeur</span>
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div id="chauffeurModalBody">
                            <div class="text-center py-5">
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">Chargement...</span>
                                </div>
                                <p class="mt-3 text-muted">Chargement...</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modalEl);
        }
        return modalEl;
    }

    function updateModalTitle(mode) {
        const titleText = document.getElementById('chauffeurModalTitleText');
        const header = document.querySelector('#chauffeurModal .modal-header');
        if (!titleText || !header) return;

        if (mode === 'create') {
            titleText.textContent = 'Nouveau Chauffeur';
            header.className = 'modal-header bg-primary text-white';
        } else {
            titleText.textContent = 'Modifier le Chauffeur';
            header.className = 'modal-header bg-warning text-dark';
        }
    }

    async function openCreateModal() {
        currentMode = 'create';
        currentChauffeurId = null;

        try {
            const modalEl = getOrCreateModal();
            updateModalTitle('create');

            currentModal = new bootstrap.Modal(modalEl);
            currentModal.show();

            const fetchResponse = await fetch('/chauffeurs/ajax/create/', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json'
                },
                credentials: 'same-origin'
            });

            if (!fetchResponse.ok) {
                throw new Error(`HTTP ${fetchResponse.status}: ${fetchResponse.statusText}`);
            }
            const response = await fetchResponse.json();
            console.log('📥 Create form response:', response.success);

            if (!response || !response.success) {
                console.error('❌ Invalid response from server');
                showError('Erreur lors du chargement du formulaire');
                return;
            }

            const modalBody = document.getElementById('chauffeurModalBody');
            modalBody.innerHTML = response.html;
            attachFormHandler();

        } catch (error) {
            console.error('❌ Error opening create modal:', error);
            showError('Erreur lors de l\'ouverture du formulaire');
        }
    }

    async function openEditModal(chauffeurId) {
        currentMode = 'update';
        currentChauffeurId = chauffeurId;

        try {
            const modalEl = getOrCreateModal();
            updateModalTitle('update');

            currentModal = new bootstrap.Modal(modalEl);
            currentModal.show();

            const fetchResponse = await fetch(`/chauffeurs/${chauffeurId}/ajax/update/`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json'
                },
                credentials: 'same-origin'
            });

            if (!fetchResponse.ok) {
                throw new Error(`HTTP ${fetchResponse.status}: ${fetchResponse.statusText}`);
            }
            const response = await fetchResponse.json();
            console.log('📥 Edit form response:', response.success);

            if (!response || !response.success) {
                console.error('❌ Invalid response from server');
                showError('Erreur lors du chargement du formulaire');
                return;
            }

            const modalBody = document.getElementById('chauffeurModalBody');
            modalBody.innerHTML = response.html;
            attachFormHandler();

        } catch (error) {
            console.error('❌ Error opening edit modal:', error);
            showError('Erreur lors de l\'ouverture du formulaire');
        }
    }

    function showError(message) {
        const modalBody = document.getElementById('chauffeurModalBody');
        if (modalBody) {
            modalBody.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-exclamation-circle text-danger fa-3x mb-3"></i>
                    <p class="text-danger mb-0">${message}</p>
                </div>
            `;
        }
        if (typeof toastManager !== 'undefined') {
            toastManager.error(message);
        }
    }

    function attachFormHandler() {
        setTimeout(() => {
            const form = document.getElementById('chauffeurForm');
            console.log('🔍 chauffeurForm found:', !!form);

            if (!form) {
                console.error('❌ Form #chauffeurForm not found!');
                return;
            }

            form.addEventListener('submit', async function(e) {
                e.preventDefault();
                console.log('📤 Submitting chauffeur form...');
                await submitForm(form);
            });

            console.log('✅ Form handler attached');
        }, 100);
    }

    async function submitForm(form) {
        try {
            const formData = new FormData(form);
            const csrfToken = getCookie('csrftoken') ||
                              document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') ||
                              document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;

            let url;
            if (currentMode === 'create') {
                url = '/chauffeurs/ajax/create/';
            } else {
                url = `/chauffeurs/${currentChauffeurId}/ajax/update/`;
            }

            // Convertir FormData en objet JSON
            const data = {};
            formData.forEach((value, key) => {
                if (key !== 'csrfmiddlewaretoken') {
                    data[key] = value;
                }
            });

            console.log('🌐 POST to:', url, '| data keys:', Object.keys(data));

            const fetchResponse = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(data),
                credentials: 'same-origin'
            });

            if (!fetchResponse.ok && fetchResponse.status !== 400) {
                throw new Error(`HTTP ${fetchResponse.status}: ${fetchResponse.statusText}`);
            }
            const response = await fetchResponse.json();
            console.log('📥 Submit response:', response.success, response.message);

            if (response.success) {
                        showToast('success', response.message || 'Opération réussie');
                if (currentModal) {
                    currentModal.hide();
                }
                // Recharger la page pour afficher les changements
                setTimeout(() => window.location.reload(), 500);
            } else {
                // Mettre à jour le formulaire avec les erreurs
                if (response.html) {
                    const modalBody = document.getElementById('chauffeurModalBody');
                    if (modalBody) {
                        modalBody.innerHTML = response.html;
                        attachFormHandler();
                    }
                }
                showToast('error', response.message || 'Veuillez corriger les erreurs');
            }

        } catch (error) {
            console.error('❌ Error submitting form:', error);
            showToast('error', 'Erreur lors de l\'envoi du formulaire');
        }
    }

    // Initialiser quand le DOM est prêt
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
