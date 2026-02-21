/**
 * MODERN UX JAVASCRIPT - Transport System
 * Provides toast notifications, search, loading states, and more
 */

// ============================================
// TOAST NOTIFICATIONS
// ============================================

class ToastManager {
  constructor() {
    this.container = this.createContainer();
  }

  createContainer() {
    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }
    return container;
  }

  show(message, type = 'info', duration = 4000) {
    const toast = this.createToast(message, type);
    this.container.appendChild(toast);

    // Show toast
    setTimeout(() => toast.classList.add('show'), 10);

    // Auto hide
    setTimeout(() => {
      this.hide(toast);
    }, duration);

    return toast;
  }

  createToast(message, type) {
    const icons = {
      success: 'fa-check-circle',
      error: 'fa-exclamation-circle',
      warning: 'fa-exclamation-triangle',
      info: 'fa-info-circle'
    };

    const titles = {
      success: 'Succès',
      error: 'Erreur',
      warning: 'Attention',
      info: 'Information'
    };

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <div class="toast-header">
        <i class="fas ${icons[type]} me-2"></i>
        <strong class="me-auto">${titles[type]}</strong>
        <button type="button" class="btn-close" onclick="toastManager.hide(this.closest('.toast'))"></button>
      </div>
      <div class="toast-body">
        ${message}
      </div>
    `;

    return toast;
  }

  hide(toast) {
    toast.classList.remove('show');
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 300);
  }

  success(message, duration) {
    return this.show(message, 'success', duration);
  }

  error(message, duration) {
    return this.show(message, 'error', duration);
  }

  warning(message, duration) {
    return this.show(message, 'warning', duration);
  }

  info(message, duration) {
    return this.show(message, 'info', duration);
  }
}

// Initialize global toast manager
const toastManager = new ToastManager();

// ============================================
// CONVERT DJANGO MESSAGES TO TOASTS
// ============================================

function convertDjangoMessagesToToasts() {
  const messagesContainer = document.querySelector('.messages-container');
  if (!messagesContainer) return;

  const alerts = messagesContainer.querySelectorAll('.alert');
  alerts.forEach(alert => {
    const message = alert.textContent.trim();
    let type = 'info';

    if (alert.classList.contains('alert-success')) type = 'success';
    else if (alert.classList.contains('alert-danger') || alert.classList.contains('alert-error')) type = 'error';
    else if (alert.classList.contains('alert-warning')) type = 'warning';

    toastManager.show(message, type);
    alert.style.display = 'none';
  });

  // Hide container after converting
  if (alerts.length > 0) {
    messagesContainer.style.display = 'none';
  }
}

// ============================================
// TABLE SEARCH FUNCTIONALITY
// ============================================

function initTableSearch() {
  const searchInputs = document.querySelectorAll('.table-search');

  searchInputs.forEach(input => {
    const tableId = input.dataset.table;
    const table = document.getElementById(tableId);

    if (!table) return;

    input.addEventListener('input', function(e) {
      const searchTerm = e.target.value.toLowerCase().trim();
      const rows = table.querySelectorAll('tbody tr:not(.no-results-row)');

      let visibleCount = 0;
      rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const shouldShow = text.includes(searchTerm);

        if (shouldShow) {
          row.style.display = '';
          row.style.animation = 'fadeIn 0.3s ease-out';
          visibleCount++;
        } else {
          row.style.display = 'none';
        }
      });

      // Update row count
      const rowCountEl = document.getElementById('rowCount');
      if (rowCountEl) {
        rowCountEl.textContent = visibleCount;
      }

      // Show "no results" message if all rows are hidden
      updateNoResultsMessage(table, visibleCount === 0, searchTerm);
    });
  });
}

function updateNoResultsMessage(table, show, searchTerm) {
  let noResultsRow = table.querySelector('.no-results-row');

  if (show) {
    if (!noResultsRow) {
      const colCount = table.querySelector('thead tr').cells.length;
      noResultsRow = document.createElement('tr');
      noResultsRow.className = 'no-results-row';

      const td = document.createElement('td');
      td.colSpan = colCount;
      td.className = 'text-center py-5';
      // Utiliser innerHTML uniquement pour le contenu statique (pas de données utilisateur)
      td.innerHTML = `
        <i class="fas fa-search fa-3x text-muted mb-3 opacity-50"></i>
        <h5 class="text-muted">Aucun résultat trouvé</h5>
      `;
      // Utiliser textContent pour searchTerm (données utilisateur) — évite le XSS
      const p = document.createElement('p');
      p.className = 'text-muted';
      p.textContent = `Aucun élément ne correspond à "${searchTerm}"`;
      td.appendChild(p);

      noResultsRow.appendChild(td);
      table.querySelector('tbody').appendChild(noResultsRow);
    }
  } else {
    if (noResultsRow) {
      noResultsRow.remove();
    }
  }
}

// ============================================
// LOADING OVERLAY
// ============================================

class LoadingManager {
  constructor() {
    this.overlay = this.createOverlay();
  }

  createOverlay() {
    let overlay = document.querySelector('.spinner-overlay');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.className = 'spinner-overlay';
      overlay.innerHTML = '<div class="spinner"></div>';
      document.body.appendChild(overlay);
    }
    return overlay;
  }

  show() {
    this.overlay.classList.add('active');
  }

  hide() {
    this.overlay.classList.remove('active');
  }
}

const loadingManager = new LoadingManager();

// Show loading on form submit
function initFormLoading() {
  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    form.addEventListener('submit', function(e) {
      // Don't show loading for search forms
      if (form.classList.contains('no-loading')) return;

      loadingManager.show();

      // Hide after 10 seconds as a failsafe
      setTimeout(() => {
        loadingManager.hide();
      }, 10000);
    });
  });
}

// ============================================
// DELETE CONFIRMATION MODAL
// ============================================

function initDeleteConfirmations() {
  const deleteLinks = document.querySelectorAll('a[href*="delete"], a[href*="supprimer"]');

  deleteLinks.forEach(link => {
    // Skip if it's already going to a confirmation page
    if (link.dataset.skipConfirm) return;

    link.addEventListener('click', function(e) {
      const confirmDelete = confirm('Êtes-vous sûr de vouloir supprimer cet élément ? Cette action est irréversible.');
      if (!confirmDelete) {
        e.preventDefault();
      }
    });
  });
}

// ============================================
// SMOOTH SCROLL
// ============================================

function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });
}

// ============================================
// ANIMATE ON SCROLL
// ============================================

function initAnimateOnScroll() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('fade-in');
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.1
  });

  // Observe all cards
  document.querySelectorAll('.card, .stat-card').forEach(el => {
    observer.observe(el);
  });
}

// ============================================
// STAT COUNTER ANIMATION
// ============================================

function animateCounter(element, target, duration = 1000) {
  const start = 0;
  const increment = target / (duration / 16);
  let current = start;

  const timer = setInterval(() => {
    current += increment;
    if (current >= target) {
      element.textContent = target;
      clearInterval(timer);
    } else {
      element.textContent = Math.floor(current);
    }
  }, 16);
}

function initStatCounters() {
  const statCards = document.querySelectorAll('.stat-card h4');

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const target = parseInt(entry.target.textContent);
        if (!isNaN(target)) {
          entry.target.textContent = '0';
          animateCounter(entry.target, target);
        }
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.5
  });

  statCards.forEach(stat => observer.observe(stat));
}

// ============================================
// FORM VALIDATION ENHANCEMENT
// ============================================

function initFormValidation() {
  const forms = document.querySelectorAll('.needs-validation');

  forms.forEach(form => {
    form.addEventListener('submit', function(event) {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
        toastManager.error('Veuillez remplir tous les champs obligatoires');
      }

      form.classList.add('was-validated');
    }, false);
  });

  // Real-time validation feedback
  const inputs = document.querySelectorAll('.needs-validation input, .needs-validation select, .needs-validation textarea');
  inputs.forEach(input => {
    input.addEventListener('blur', function() {
      if (this.checkValidity()) {
        this.classList.remove('is-invalid');
        this.classList.add('is-valid');
      } else {
        this.classList.remove('is-valid');
        this.classList.add('is-invalid');
      }
    });
  });
}

// ============================================
// AUTO-HIDE ALERTS
// ============================================

function autoHideAlerts() {
  const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
  alerts.forEach(alert => {
    setTimeout(() => {
      const closeBtn = alert.querySelector('.btn-close');
      if (closeBtn) {
        closeBtn.click();
      } else {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 300);
      }
    }, 5000);
  });
}

// ============================================
// COPY TO CLIPBOARD
// ============================================

function copyToClipboard(text, successMessage = 'Copié dans le presse-papier !') {
  navigator.clipboard.writeText(text).then(() => {
    toastManager.success(successMessage);
  }).catch(() => {
    toastManager.error('Impossible de copier');
  });
}

// Make it available globally
window.copyToClipboard = copyToClipboard;

// ============================================
// KEYBOARD SHORTCUTS
// ============================================

function initKeyboardShortcuts() {
  document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K: Focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      const searchInput = document.querySelector('.table-search, .search-box input');
      if (searchInput) {
        searchInput.focus();
        searchInput.select();
      }
    }

    // Escape: Close modals/toasts
    if (e.key === 'Escape') {
      const toasts = document.querySelectorAll('.toast');
      toasts.forEach(toast => toastManager.hide(toast));
    }
  });
}

// ============================================
// INITIALIZE ALL
// ============================================

document.addEventListener('DOMContentLoaded', function() {
  // Convert Django messages to modern toasts
  convertDjangoMessagesToToasts();

  // Initialize features
  initTableSearch();
  initFormLoading();
  initSmoothScroll();
  initAnimateOnScroll();
  initStatCounters();
  initFormValidation();
  autoHideAlerts();
  initKeyboardShortcuts();

  // Add animation to page title
  const pageTitle = document.querySelector('.page-title');
  if (pageTitle) {
    pageTitle.classList.add('fade-in');
  }

  console.log('✨ Modern UX initialized successfully!');
});

// ============================================
// TABLE SORTING
// ============================================

function sortTable(columnIndex, tableId) {
  const table = document.getElementById(tableId);
  if (!table) return;

  const tbody = table.querySelector('tbody');
  const rows = Array.from(tbody.querySelectorAll('tr:not(.no-results-row)'));

  // Determine sort direction
  const header = table.querySelectorAll('thead th')[columnIndex];
  const isAscending = header.classList.contains('sort-asc');

  // Remove all sort classes
  table.querySelectorAll('thead th').forEach(th => {
    th.classList.remove('sort-asc', 'sort-desc');
    const sortIcon = th.querySelector('.fa-sort, .fa-sort-up, .fa-sort-down');
    if (sortIcon) {
      sortIcon.className = 'fas fa-sort ms-1 text-muted';
    }
  });

  // Add new sort class
  header.classList.add(isAscending ? 'sort-desc' : 'sort-asc');
  const sortIcon = header.querySelector('.fa-sort, .fa-sort-up, .fa-sort-down');
  if (sortIcon) {
    sortIcon.className = `fas fa-sort-${isAscending ? 'down' : 'up'} ms-1 text-primary`;
  }

  // Sort rows
  rows.sort((a, b) => {
    const aValue = a.cells[columnIndex].textContent.trim();
    const bValue = b.cells[columnIndex].textContent.trim();

    // Try to parse as number
    const aNum = parseFloat(aValue);
    const bNum = parseFloat(bValue);

    if (!isNaN(aNum) && !isNaN(bNum)) {
      return isAscending ? bNum - aNum : aNum - bNum;
    }

    // String comparison
    return isAscending
      ? bValue.localeCompare(aValue, 'fr')
      : aValue.localeCompare(bValue, 'fr');
  });

  // Reorder rows
  rows.forEach(row => tbody.appendChild(row));

  // Add animation
  rows.forEach((row, index) => {
    row.style.animation = 'none';
    setTimeout(() => {
      row.style.animation = 'fadeIn 0.3s ease-out';
    }, index * 20);
  });
}

// ============================================
// EXPORT TO EXCEL
// ============================================

function exportTableToExcel(tableId, filename = 'export') {
  const table = document.getElementById(tableId);
  if (!table) {
    toastManager.error('Table non trouvée');
    return;
  }

  // Get visible rows only
  const rows = Array.from(table.querySelectorAll('tr')).filter(row => {
    return row.style.display !== 'none' && !row.classList.contains('no-results-row');
  });

  if (rows.length <= 1) {
    toastManager.warning('Aucune donnée à exporter');
    return;
  }

  let csv = [];

  rows.forEach(row => {
    const cols = Array.from(row.querySelectorAll('td, th'));
    // Exclude last column (Actions)
    const rowData = cols.slice(0, -1).map(col => {
      // Get text content, handling badges and other elements
      let text = col.textContent.trim();
      // Escape quotes and wrap in quotes if contains comma
      text = text.replace(/"/g, '""');
      return `"${text}"`;
    });
    csv.push(rowData.join(','));
  });

  // Create CSV file
  const csvContent = '\uFEFF' + csv.join('\n'); // Add BOM for Excel UTF-8 support
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');

  if (navigator.msSaveBlob) {
    // IE 10+
    navigator.msSaveBlob(blob, filename + '.csv');
  } else {
    link.href = URL.createObjectURL(blob);
    link.download = filename + '_' + new Date().toISOString().split('T')[0] + '.csv';
    link.click();
  }

  toastManager.success('Export réussi ! Fichier téléchargé.');
}

// ============================================
// EXPORT FOR GLOBAL USE
// ============================================

window.toastManager = toastManager;
window.loadingManager = loadingManager;
window.sortTable = sortTable;
window.exportTableToExcel = exportTableToExcel;
