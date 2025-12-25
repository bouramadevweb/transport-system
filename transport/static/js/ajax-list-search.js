/**
 * AJAX List Search Module
 *
 * Generic reusable module for server-side AJAX search on list pages
 */

class AjaxListSearch {
    /**
     * Constructor
     * @param {Object} config - Configuration object
     * @param {string} config.searchInputSelector - CSS selector for search input
     * @param {string} config.tableBodySelector - CSS selector for table tbody
     * @param {string} config.counterSelector - CSS selector for result counter (optional)
     * @param {string} config.ajaxUrl - AJAX endpoint URL
     * @param {number} config.debounceDelay - Debounce delay in ms (default: 300)
     */
    constructor(config) {
        this.searchInput = document.querySelector(config.searchInputSelector);
        this.tableBody = document.querySelector(config.tableBodySelector);
        this.counter = config.counterSelector ? document.querySelector(config.counterSelector) : null;
        this.ajaxUrl = config.ajaxUrl;
        this.debounceDelay = config.debounceDelay || 300;
        this.debounceTimer = null;
        this.lastQuery = '';

        if (!this.searchInput) {
            console.error(`Search input not found: ${config.searchInputSelector}`);
            return;
        }

        if (!this.tableBody) {
            console.error(`Table body not found: ${config.tableBodySelector}`);
            return;
        }

        this.init();
    }

    /**
     * Initialize search functionality
     */
    init() {
        // Attach input event listener
        this.searchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();

            // Clear previous timer
            clearTimeout(this.debounceTimer);

            // Only trigger search if query changed
            if (query === this.lastQuery) {
                return;
            }

            // Debounce search
            this.debounceTimer = setTimeout(() => {
                this.performSearch(query);
            }, this.debounceDelay);
        });

        // Optional: Search on Enter key
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                clearTimeout(this.debounceTimer);
                this.performSearch(this.searchInput.value.trim());
            }
        });

        console.log('✅ AjaxListSearch initialized');
    }

    /**
     * Perform AJAX search
     * @param {string} query - Search query
     */
    async performSearch(query) {
        this.lastQuery = query;

        try {
            // Show loading state
            this.showLoading();

            // Make AJAX request
            const response = await ajaxManager.get(
                this.ajaxUrl,
                { q: query },
                { showLoading: false, showToast: false }
            );

            if (response.success) {
                // Update table body
                this.tableBody.innerHTML = response.html;

                // Update counter if available
                if (this.counter && response.count !== undefined) {
                    this.updateCounter(response.count);
                }

                // Show success feedback for non-empty searches
                if (query && typeof toastManager !== 'undefined') {
                    toastManager.success(`${response.count} résultat(s) trouvé(s)`);
                }
            } else {
                // Show error
                this.showError(response.message || 'Erreur lors de la recherche');
            }

        } catch (error) {
            console.error('Search error:', error);
            this.showError('Une erreur est survenue lors de la recherche');
        }
    }

    /**
     * Show loading state
     */
    showLoading() {
        this.tableBody.innerHTML = `
            <tr>
                <td colspan="100" class="text-center py-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Recherche en cours...</span>
                    </div>
                    <p class="mt-3 text-muted">Recherche en cours...</p>
                </td>
            </tr>
        `;
    }

    /**
     * Show error state
     * @param {string} message - Error message
     */
    showError(message) {
        this.tableBody.innerHTML = `
            <tr>
                <td colspan="100" class="text-center py-4">
                    <i class="fas fa-exclamation-circle text-danger fa-2x mb-3"></i>
                    <p class="text-danger mb-0">${message}</p>
                </td>
            </tr>
        `;

        if (typeof toastManager !== 'undefined') {
            toastManager.error(message);
        }
    }

    /**
     * Update result counter
     * @param {number} count - Number of results
     */
    updateCounter(count) {
        if (!this.counter) return;

        // Assuming counter contains text like "X clients affichés"
        const text = this.counter.textContent;
        const updated = text.replace(/\d+/, count);
        this.counter.textContent = updated;
    }

    /**
     * Reset search (clear input and reload all results)
     */
    reset() {
        this.searchInput.value = '';
        this.lastQuery = '';
        this.performSearch('');
    }
}

// Export for use in other scripts
if (typeof window !== 'undefined') {
    window.AjaxListSearch = AjaxListSearch;
}
