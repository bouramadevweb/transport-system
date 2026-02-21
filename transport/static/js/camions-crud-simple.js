/**
 * Camions CRUD - Version simplifiée et robuste
 * Pattern identique à chauffeurs-crud.js (qui fonctionne)
 */

(function() {
    'use strict';

    console.log('🚀 Camions CRUD Simple - Initializing...');

    let currentModal = null;
    let currentMode = 'create';
    let currentCamionId = null;

    // Wrapper sécurisé pour toastManager (optionnel)
    function showToast(type, msg) {
        if (typeof toastManager !== 'undefined') toastManager[type](msg);
    }

    // Récupère le token CSRF depuis cookie, meta tag ou input caché
    // CSRF_COOKIE_HTTPONLY=True empêche la lecture du cookie par JS,
    // on utilise donc le meta tag en fallback.
    function getCsrfToken() {
        // 1. Essayer le cookie (fonctionne si CSRF_COOKIE_HTTPONLY=False)
        const name = 'csrftoken';
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    return decodeURIComponent(cookie.substring(name.length + 1));
                }
            }
        }
        // 2. Meta tag (admin.html: <meta name="csrf-token" content="{{ csrf_token }}">)
        const meta = document.querySelector('meta[name="csrf-token"]');
        if (meta && meta.getAttribute('content')) {
            return meta.getAttribute('content');
        }
        // 3. Input caché dans le formulaire
        const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (input && input.value) {
            return input.value;
        }
        return null;
    }

    function init() {
        console.log('📋 Camions CRUD - Init...');

        if (typeof bootstrap === 'undefined') {
            console.error('❌ bootstrap not found!');
            return;
        }

        console.log('✅ Bootstrap found, attaching event listeners');

        // Event delegation - bouton créer
        document.addEventListener('click', function(e) {
            const createBtn = e.target.closest('[data-action="create-camion"]');
            if (createBtn) {
                e.preventDefault();
                console.log('🎯 Create camion button clicked!');
                openCreateModal();
            }

            const editBtn = e.target.closest('[data-action="edit-camion"]');
            if (editBtn) {
                e.preventDefault();
                const camionId = editBtn.dataset.camionId;
                console.log('🎯 Edit camion button clicked! ID:', camionId);
                if (camionId) {
                    openEditModal(camionId);
                }
            }
        });

        console.log('✅ Event listeners attached');
    }

    function getOrCreateModal() {
        let modalEl = document.getElementById('camionModal');
        if (!modalEl) {
            modalEl = document.createElement('div');
            modalEl.id = 'camionModal';
            modalEl.className = 'modal fade';
            modalEl.setAttribute('tabindex', '-1');
            modalEl.innerHTML = `
                <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
                    <div class="modal-content">
                        <div class="modal-header bg-primary text-white">
                            <h5 class="modal-title" id="camionModalTitle">
                                <i class="fas fa-truck me-2"></i>
                                <span id="camionModalTitleText">Camion</span>
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div id="camionModalBody">
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
        const titleText = document.getElementById('camionModalTitleText');
        const header = document.querySelector('#camionModal .modal-header');
        if (!titleText || !header) return;

        if (mode === 'create') {
            titleText.textContent = 'Nouveau Camion';
            header.className = 'modal-header bg-success text-white';
        } else {
            titleText.textContent = 'Modifier le Camion';
            header.className = 'modal-header bg-warning text-dark';
        }
    }

    function showError(message) {
        const modalBody = document.getElementById('camionModalBody');
        if (modalBody) {
            modalBody.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-exclamation-circle text-danger fa-3x mb-3"></i>
                    <p class="text-danger mb-0">${message}</p>
                </div>
            `;
        }
        showToast('error', message);
    }

    async function openCreateModal() {
        currentMode = 'create';
        currentCamionId = null;

        try {
            const modalEl = getOrCreateModal();
            updateModalTitle('create');

            // Réutiliser l'instance existante si possible
            currentModal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
            currentModal.show();

            const fetchResponse = await fetch('/camions/ajax/create/', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json'
                },
                credentials: 'same-origin'
            });

            const response = await fetchResponse.json();
            console.log('📥 Create form response:', response.success);

            if (!response || !response.success) {
                console.error('❌ Invalid response from server');
                showError('Erreur lors du chargement du formulaire');
                return;
            }

            const modalBody = document.getElementById('camionModalBody');
            modalBody.innerHTML = response.html;
            attachFormHandler();

        } catch (error) {
            console.error('❌ Error opening create modal:', error);
            showError('Erreur lors de l\'ouverture du formulaire');
        }
    }

    async function openEditModal(camionId) {
        currentMode = 'update';
        currentCamionId = camionId;

        try {
            const modalEl = getOrCreateModal();
            updateModalTitle('update');

            currentModal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
            currentModal.show();

            const fetchResponse = await fetch(`/camions/${camionId}/ajax/update/`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json'
                },
                credentials: 'same-origin'
            });

            const response = await fetchResponse.json();
            console.log('📥 Edit form response:', response.success);

            if (!response || !response.success) {
                console.error('❌ Invalid response from server');
                showError('Erreur lors du chargement du formulaire');
                return;
            }

            const modalBody = document.getElementById('camionModalBody');
            modalBody.innerHTML = response.html;
            attachFormHandler();

        } catch (error) {
            console.error('❌ Error opening edit modal:', error);
            showError('Erreur lors de l\'ouverture du formulaire');
        }
    }

    function attachFormHandler() {
        setTimeout(() => {
            const form = document.getElementById('camionForm');
            console.log('🔍 camionForm found:', !!form);

            if (!form) {
                console.error('❌ Form #camionForm not found!');
                return;
            }

            form.addEventListener('submit', async function(e) {
                e.preventDefault();
                console.log('📤 Submitting camion form...');
                await submitForm(form);
            });

            console.log('✅ Form handler attached');
        }, 100);
    }

    async function submitForm(form) {
        try {
            const formData = new FormData(form);
            const csrfToken = getCsrfToken();

            let url;
            if (currentMode === 'create') {
                url = '/camions/ajax/create/';
            } else {
                url = `/camions/${currentCamionId}/ajax/update/`;
            }

            // Convertir FormData en JSON (comme chauffeurs-crud.js)
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

            const response = await fetchResponse.json();
            console.log('📥 Submit response:', response.success, response.message);

            if (response.success) {
                showToast('success', response.message || 'Opération réussie');
                if (currentModal) {
                    currentModal.hide();
                }
                setTimeout(() => window.location.reload(), 500);
            } else {
                if (response.html) {
                    const modalBody = document.getElementById('camionModalBody');
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
