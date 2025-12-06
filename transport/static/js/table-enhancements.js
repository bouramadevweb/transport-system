/**
 * Améliorations pour les tables: recherche, tri, et export CSV
 * À inclure dans les templates de liste
 */

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    initializeTableEnhancements();
});

function initializeTableEnhancements() {
    initializeSearch();
    initializeSort();
}

/**
 * Recherche en temps réel dans la table
 */
function initializeSearch() {
    const searchInput = document.getElementById('searchInput');
    const table = document.querySelector('table[id$="Table"]');

    if (!searchInput || !table) return;

    searchInput.addEventListener('keyup', function() {
        const filter = this.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(filter) ? '' : 'none';
        });
    });
}

/**
 * Tri des colonnes cliquables
 */
function initializeSort() {
    const headers = document.querySelectorAll('.sortable');

    headers.forEach(header => {
        header.addEventListener('click', function() {
            const columnIndex = parseInt(this.dataset.column);
            const tableId = this.closest('table').id;
            sortTable(tableId, columnIndex);
        });
    });
}

function sortTable(tableId, columnIndex) {
    const table = document.getElementById(tableId);
    if (!table) return;

    const rows = Array.from(table.querySelectorAll('tbody tr'));
    const isAscending = table.dataset.sortOrder !== 'asc';

    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex]?.textContent.trim() || '';
        const bValue = b.cells[columnIndex]?.textContent.trim() || '';

        // Essayer de parser comme nombre
        const aNum = parseFloat(aValue.replace(/[^\d.-]/g, ''));
        const bNum = parseFloat(bValue.replace(/[^\d.-]/g, ''));

        if (!isNaN(aNum) && !isNaN(bNum)) {
            return isAscending ? aNum - bNum : bNum - aNum;
        }

        // Essayer de parser comme date (format dd/mm/yyyy)
        const datePattern = /(\d{2})\/(\d{2})\/(\d{4})/;
        const aMatch = aValue.match(datePattern);
        const bMatch = bValue.match(datePattern);

        if (aMatch && bMatch) {
            const aDate = new Date(aMatch[3], aMatch[2] - 1, aMatch[1]);
            const bDate = new Date(bMatch[3], bMatch[2] - 1, bMatch[1]);
            return isAscending ? aDate - bDate : bDate - aDate;
        }

        // Sinon, tri alphabétique
        return isAscending
            ? aValue.localeCompare(bValue, 'fr')
            : bValue.localeCompare(aValue, 'fr');
    });

    // Réinsérer les lignes triées
    const tbody = table.querySelector('tbody');
    rows.forEach(row => tbody.appendChild(row));

    table.dataset.sortOrder = isAscending ? 'asc' : 'desc';

    // Mettre à jour les icônes de tri
    updateSortIcons(table, columnIndex, isAscending);
}

function updateSortIcons(table, columnIndex, isAscending) {
    // Réinitialiser toutes les icônes
    table.querySelectorAll('.sort-icon').forEach(icon => {
        icon.className = 'fas fa-sort sort-icon';
    });

    // Mettre à jour l'icône de la colonne triée
    const sortedHeader = table.querySelector(`.sortable[data-column="${columnIndex}"] .sort-icon`);
    if (sortedHeader) {
        sortedHeader.className = isAscending ? 'fas fa-sort-up sort-icon' : 'fas fa-sort-down sort-icon';
    }
}

/**
 * Export de la table en CSV
 */
function exportToCSV(filename) {
    const table = document.querySelector('table[id$="Table"]');
    if (!table) {
        console.error('Table non trouvée');
        return;
    }

    const rows = table.querySelectorAll('tr:not([style*="display: none"])');
    let csv = [];

    rows.forEach(row => {
        // Exclure la dernière colonne (Actions)
        const cells = Array.from(row.cells).slice(0, -1);
        const rowData = cells.map(cell => {
            // Nettoyer le texte et échapper les guillemets
            let text = cell.textContent.trim();
            text = text.replace(/\s+/g, ' '); // Remplacer les espaces multiples
            text = text.replace(/"/g, '""'); // Échapper les guillemets
            return '"' + text + '"';
        });
        csv.push(rowData.join(','));
    });

    // Créer et télécharger le fichier
    const csvContent = '\uFEFF' + csv.join('\n'); // BOM pour UTF-8
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = (filename || 'export') + '_' + new Date().toISOString().slice(0,10) + '.csv';
    link.click();
}

/**
 * Calcul automatique de statistiques pour les colonnes numériques
 */
function calculateColumnStatistics(tableId, columnIndexes, elementIds) {
    const table = document.getElementById(tableId);
    if (!table) return;

    const rows = table.querySelectorAll('tbody tr:not([style*="display: none"])');
    const totals = {};

    columnIndexes.forEach(index => {
        totals[index] = 0;
    });

    rows.forEach(row => {
        columnIndexes.forEach(index => {
            const cell = row.cells[index];
            if (cell) {
                const value = parseFloat(cell.textContent.replace(/[^\d.-]/g, '')) || 0;
                totals[index] += value;
            }
        });
    });

    // Mettre à jour les éléments d'affichage
    columnIndexes.forEach((index, i) => {
        const elementId = elementIds[i];
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = totals[index].toFixed(2) + '€';
        }
    });
}

/**
 * Confirmation avant suppression
 */
function confirmDelete(message) {
    return confirm(message || 'Êtes-vous sûr de vouloir supprimer cet élément ?');
}

/**
 * Afficher/masquer les filtres avancés
 */
function toggleFilters() {
    const filtersPanel = document.getElementById('advancedFilters');
    if (filtersPanel) {
        filtersPanel.style.display = filtersPanel.style.display === 'none' ? 'block' : 'none';
    }
}
