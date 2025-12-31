/**
 * AJAX Utilities Module
 *
 * Provides centralized AJAX functionality for the transport system
 * with CSRF protection, error handling, and integration with existing
 * ToastManager and LoadingManager.
 */

/**
 * Custom error class for AJAX operations
 */
class AjaxError extends Error {
    constructor(message, status = null, response = null) {
        super(message);
        this.name = 'AjaxError';
        this.status = status;
        this.response = response;
    }
}

/**
 * Main AJAX Manager Class
 *
 * Handles all AJAX requests with automatic CSRF protection,
 * loading indicators, and error handling.
 */
class AjaxManager {
    constructor() {
        this.csrfToken = this.getCSRFToken();
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        };
    }

    /**
     * Extract CSRF token from cookie
     * @returns {string|null} CSRF token
     */
    getCSRFToken() {
        const name = 'csrftoken';
        const cookies = document.cookie.split(';');

        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                return decodeURIComponent(cookie.substring(name.length + 1));
            }
        }

        return null;
    }

    /**
     * Build query string from params object
     * @param {Object} params - Query parameters
     * @returns {string} Query string
     */
    buildQueryString(params) {
        if (!params || Object.keys(params).length === 0) {
            return '';
        }

        const queryParts = [];
        for (const [key, value] of Object.entries(params)) {
            if (value !== null && value !== undefined && value !== '') {
                queryParts.push(
                    `${encodeURIComponent(key)}=${encodeURIComponent(value)}`
                );
            }
        }

        return queryParts.length > 0 ? '?' + queryParts.join('&') : '';
    }

    /**
     * Handle HTTP response
     * @param {Response} response - Fetch response object
     * @returns {Promise} Parsed response
     */
    async handleResponse(response) {
        const contentType = response.headers.get('content-type');

        // Parse JSON response
        if (contentType && contentType.includes('application/json')) {
            const data = await response.json();

            if (!response.ok) {
                throw new AjaxError(
                    data.message || data.error || `HTTP Error ${response.status}`,
                    response.status,
                    data
                );
            }

            return data;
        }

        // Parse text response
        const text = await response.text();

        if (!response.ok) {
            throw new AjaxError(
                `HTTP Error ${response.status}`,
                response.status,
                text
            );
        }

        return text;
    }

    /**
     * Handle AJAX errors
     * @param {Error} error - Error object
     * @param {boolean} showToast - Show error toast
     */
    handleError(error, showToast = true) {
        console.error('AJAX Error:', error);

        if (showToast && typeof toastManager !== 'undefined') {
            let message = 'Une erreur est survenue';

            if (error instanceof AjaxError) {
                message = error.message;

                // Handle specific HTTP errors
                if (error.status === 403) {
                    message = 'Accès refusé. Vous n\'avez pas les permissions nécessaires.';
                } else if (error.status === 404) {
                    message = 'Ressource non trouvée.';
                } else if (error.status === 500) {
                    message = 'Erreur serveur. Veuillez réessayer.';
                }
            }

            toastManager.error(message);
        }

        throw error;
    }

    /**
     * Perform GET request
     * @param {string} url - Request URL
     * @param {Object} params - Query parameters
     * @param {Object} options - Additional options
     * @returns {Promise} Response data
     */
    async get(url, params = {}, options = {}) {
        const { showLoading = true, showToast = true } = options;

        try {
            if (showLoading && typeof loadingManager !== 'undefined') {
                loadingManager.show();
            }

            const queryString = this.buildQueryString(params);
            const fullUrl = url + queryString;

            const response = await fetch(fullUrl, {
                method: 'GET',
                headers: this.defaultHeaders,
                credentials: 'same-origin'
            });

            const data = await this.handleResponse(response);

            if (showLoading && typeof loadingManager !== 'undefined') {
                loadingManager.hide();
            }

            return data;

        } catch (error) {
            if (showLoading && typeof loadingManager !== 'undefined') {
                loadingManager.hide();
            }
            this.handleError(error, showToast);
        }
    }

    /**
     * Perform POST request
     * @param {string} url - Request URL
     * @param {Object} data - Request body data
     * @param {Object} options - Additional options
     * @returns {Promise} Response data
     */
    async post(url, data = {}, options = {}) {
        const { showLoading = true, showToast = true } = options;

        try {
            if (showLoading && typeof loadingManager !== 'undefined') {
                loadingManager.show();
            }

            const headers = { ...this.defaultHeaders };

            // Add CSRF token for POST requests
            if (this.csrfToken) {
                headers['X-CSRFToken'] = this.csrfToken;
            }

            const response = await fetch(url, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(data),
                credentials: 'same-origin'
            });

            const responseData = await this.handleResponse(response);

            if (showLoading && typeof loadingManager !== 'undefined') {
                loadingManager.hide();
            }

            return responseData;

        } catch (error) {
            if (showLoading && typeof loadingManager !== 'undefined') {
                loadingManager.hide();
            }
            this.handleError(error, showToast);
        }
    }

    /**
     * Perform PUT request
     * @param {string} url - Request URL
     * @param {Object} data - Request body data
     * @param {Object} options - Additional options
     * @returns {Promise} Response data
     */
    async put(url, data = {}, options = {}) {
        const { showLoading = true, showToast = true } = options;

        try {
            if (showLoading && typeof loadingManager !== 'undefined') {
                loadingManager.show();
            }

            const headers = { ...this.defaultHeaders };

            // Add CSRF token
            if (this.csrfToken) {
                headers['X-CSRFToken'] = this.csrfToken;
            }

            const response = await fetch(url, {
                method: 'PUT',
                headers: headers,
                body: JSON.stringify(data),
                credentials: 'same-origin'
            });

            const responseData = await this.handleResponse(response);

            if (showLoading && typeof loadingManager !== 'undefined') {
                loadingManager.hide();
            }

            return responseData;

        } catch (error) {
            if (showLoading && typeof loadingManager !== 'undefined') {
                loadingManager.hide();
            }
            this.handleError(error, showToast);
        }
    }

    /**
     * Perform DELETE request
     * @param {string} url - Request URL
     * @param {Object} options - Additional options
     * @returns {Promise} Response data
     */
    async delete(url, options = {}) {
        const { showLoading = true, showToast = true } = options;

        try {
            if (showLoading && typeof loadingManager !== 'undefined') {
                loadingManager.show();
            }

            const headers = { ...this.defaultHeaders };

            // Add CSRF token
            if (this.csrfToken) {
                headers['X-CSRFToken'] = this.csrfToken;
            }

            const response = await fetch(url, {
                method: 'DELETE',
                headers: headers,
                credentials: 'same-origin'
            });

            const data = await this.handleResponse(response);

            if (showLoading && typeof loadingManager !== 'undefined') {
                loadingManager.hide();
            }

            return data;

        } catch (error) {
            if (showLoading && typeof loadingManager !== 'undefined') {
                loadingManager.hide();
            }
            this.handleError(error, showToast);
        }
    }

    /**
     * Submit a form via AJAX
     * @param {HTMLFormElement} form - Form element
     * @param {string} url - Submit URL (optional, uses form action if not provided)
     * @param {Object} options - Additional options
     * @returns {Promise} Response data
     */
    async submitForm(form, url = null, options = {}) {
        const submitUrl = url || form.action;
        const method = (form.method || 'POST').toUpperCase();

        // Get form data
        const formData = new FormData(form);
        const data = {};

        for (const [key, value] of formData.entries()) {
            // Handle multiple values (checkboxes, multi-select)
            if (data[key]) {
                if (Array.isArray(data[key])) {
                    data[key].push(value);
                } else {
                    data[key] = [data[key], value];
                }
            } else {
                data[key] = value;
            }
        }

        // Send request based on method
        if (method === 'GET') {
            return await this.get(submitUrl, data, options);
        } else if (method === 'POST') {
            return await this.post(submitUrl, data, options);
        } else if (method === 'PUT') {
            return await this.put(submitUrl, data, options);
        } else if (method === 'DELETE') {
            return await this.delete(submitUrl, options);
        }
    }
}

// Create global instance
const ajaxManager = new AjaxManager();
window.ajaxManager = ajaxManager; // Make it explicitly global

// Log initialization
console.log('✅ AjaxManager initialized');
console.log('CSRF Token:', ajaxManager.csrfToken ? '✅ Found' : '❌ Not found');
