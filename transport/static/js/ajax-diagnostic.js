/**
 * Script de diagnostic AJAX
 * Vérifie que toutes les dépendances sont bien chargées
 */

(function() {
    console.log('🔍 Diagnostic AJAX - Démarrage...');

    const checks = {
        bootstrap: typeof bootstrap !== 'undefined',
        ajaxManager: typeof ajaxManager !== 'undefined',
        toastManager: typeof toastManager !== 'undefined',
        loadingManager: typeof loadingManager !== 'undefined',
        jquery: typeof $ !== 'undefined'
    };

    console.log('📊 Résultats du diagnostic:');
    console.table(checks);

    // Vérifier les boutons AJAX
    const buttons = {
        'Boutons création client': document.querySelectorAll('.btn-create-client').length,
        'Boutons édition client': document.querySelectorAll('.btn-edit-client').length,
        'Boutons création chauffeur': document.querySelectorAll('.btn-create-chauffeur').length,
        'Boutons édition chauffeur': document.querySelectorAll('.btn-edit-chauffeur').length,
        'Boutons terminer mission': document.querySelectorAll('.btn-terminer-mission').length,
        'Boutons validation paiement': document.querySelectorAll('.btn-validate-payment').length
    };

    console.log('🔘 Boutons AJAX détectés:');
    console.table(buttons);

    // Vérifier les événements
    console.log('📡 Event listeners:');
    if (typeof window.crudModalManager !== 'undefined') {
        console.log('✅ CrudModalManager actif');
    } else {
        console.log('❌ CrudModalManager non trouvé');
    }

    if (typeof window.terminerMissionModalManager !== 'undefined') {
        console.log('✅ TerminerMissionModalManager actif');
    } else {
        console.log('⚠️  TerminerMissionModalManager non trouvé (normal si pas sur page missions)');
    }

    if (typeof window.validationModalManager !== 'undefined') {
        console.log('✅ ValidationModalManager actif');
    } else {
        console.log('⚠️  ValidationModalManager non trouvé (normal si pas sur page paiements)');
    }

    // Test du token CSRF
    const csrfToken = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
    if (csrfToken) {
        console.log('✅ Token CSRF détecté:', csrfToken.split('=')[1].substring(0, 10) + '...');
    } else {
        console.log('❌ Token CSRF non trouvé!');
    }

    console.log('🔍 Diagnostic terminé!');
    console.log('💡 Testez en cliquant sur un bouton "Ajouter" ou "Modifier"');
})();
