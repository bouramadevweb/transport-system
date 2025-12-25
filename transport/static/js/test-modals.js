/**
 * Script de test complet des modals AJAX
 * Exécute une série de tests pour identifier les problèmes
 */

(function() {
    console.log('%c🧪 TEST COMPLET DES MODALS AJAX', 'background: #3b82f6; color: white; padding: 5px 10px; font-size: 14px; font-weight: bold;');

    const results = {
        dependencies: {},
        buttons: {},
        managers: {},
        urls: {},
        errors: []
    };

    // ========== TEST 1: DÉPENDANCES ==========
    console.log('\n%c📦 Test 1: Vérification des dépendances', 'color: #3b82f6; font-weight: bold;');

    results.dependencies = {
        'Bootstrap': typeof bootstrap !== 'undefined',
        'jQuery (optionnel)': typeof $ !== 'undefined',
        'ajaxManager': typeof ajaxManager !== 'undefined',
        'toastManager': typeof toastManager !== 'undefined',
        'loadingManager': typeof loadingManager !== 'undefined',
        'CrudModalManager': typeof CrudModalManager !== 'undefined',
        'MissionCRUDManager': typeof MissionCRUDManager !== 'undefined',
        'TerminerMissionModalManager': typeof TerminerMissionModalManager !== 'undefined'
    };

    console.table(results.dependencies);

    // Identifier les dépendances manquantes
    for (const [key, value] of Object.entries(results.dependencies)) {
        if (!value && !key.includes('optionnel')) {
            results.errors.push(`❌ Dépendance manquante: ${key}`);
        }
    }

    // ========== TEST 2: BOUTONS ==========
    console.log('\n%c🔘 Test 2: Détection des boutons AJAX', 'color: #3b82f6; font-weight: bold;');

    const buttonSelectors = {
        'Clients - Créer': '.btn-create-client',
        'Clients - Modifier': '.btn-edit-client',
        'Chauffeurs - Créer': '.btn-create-chauffeur',
        'Chauffeurs - Modifier': '.btn-edit-chauffeur',
        'Camions - Créer': '[data-action="create-camion"]',
        'Camions - Modifier': '[data-action="edit-camion"]',
        'Missions - Créer': '[data-action="create-mission"]',
        'Missions - Modifier': '[data-action="edit-mission"]',
        'Missions - Terminer': '.btn-terminer-mission',
        'Paiements - Valider': '.btn-validate-payment'
    };

    for (const [label, selector] of Object.entries(buttonSelectors)) {
        const count = document.querySelectorAll(selector).length;
        results.buttons[label] = count;

        if (count > 0) {
            console.log(`✅ ${label}: ${count} bouton(s)`);
        } else {
            console.log(`⚠️  ${label}: aucun bouton trouvé`);
        }
    }

    // ========== TEST 3: MANAGERS ACTIFS ==========
    console.log('\n%c🎯 Test 3: Managers JavaScript actifs', 'color: #3b82f6; font-weight: bold;');

    results.managers = {
        'crudModalManager': typeof window.crudModalManager !== 'undefined',
        'missionCRUDManager': typeof window.missionCRUDManager !== 'undefined',
        'terminerMissionModalManager': typeof window.terminerMissionModalManager !== 'undefined',
        'validationModalManager': typeof window.validationModalManager !== 'undefined',
        'dashboardManager': typeof window.dashboardManager !== 'undefined'
    };

    for (const [manager, active] of Object.entries(results.managers)) {
        if (active) {
            console.log(`✅ ${manager} est actif`);
        } else {
            console.log(`⚠️  ${manager} non trouvé (normal si pas sur la page concernée)`);
        }
    }

    // ========== TEST 4: TOKEN CSRF ==========
    console.log('\n%c🔐 Test 4: Token CSRF', 'color: #3b82f6; font-weight: bold;');

    const csrfCookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
    if (csrfCookie) {
        const token = csrfCookie.split('=')[1];
        console.log(`✅ Token CSRF trouvé: ${token.substring(0, 10)}...`);
    } else {
        console.log('❌ Token CSRF MANQUANT!');
        results.errors.push('❌ Token CSRF manquant - Vérifier settings.py');
    }

    // ========== TEST 5: URLS AJAX (si sur une page spécifique) ==========
    console.log('\n%c🔗 Test 5: Test des URLs AJAX', 'color: #3b82f6; font-weight: bold;');

    // Détecter quelle page on est
    const path = window.location.pathname;
    let urlsToTest = [];

    if (path.includes('/clients')) {
        urlsToTest = [
            { name: 'Créer client', url: '/clients/ajax/create/' },
            { name: 'Rechercher clients', url: '/clients/ajax/search/' }
        ];
    } else if (path.includes('/chauffeurs')) {
        urlsToTest = [
            { name: 'Créer chauffeur', url: '/chauffeurs/ajax/create/' },
            { name: 'Rechercher chauffeurs', url: '/chauffeurs/ajax/search/' }
        ];
    } else if (path.includes('/camions')) {
        urlsToTest = [
            { name: 'Formulaire camion', url: '/camions/ajax/create-form/' }
        ];
    } else if (path.includes('/missions')) {
        urlsToTest = [
            { name: 'Formulaire mission', url: '/missions/ajax/create-form/' }
        ];
    }

    if (urlsToTest.length > 0) {
        console.log(`Tests d'URLs pour la page courante:`);
        // Note: On ne teste pas réellement les URLs pour éviter les requêtes,
        // mais on affiche quelles URLs devraient fonctionner
        urlsToTest.forEach(test => {
            console.log(`  📍 ${test.name}: ${test.url}`);
        });
        console.log('  💡 Pour tester une URL, ouvrez-la dans un nouvel onglet');
    } else {
        console.log('⚠️  Page non reconnue, impossible de tester les URLs AJAX');
    }

    // ========== TEST 6: ÉVÉNEMENTS ==========
    console.log('\n%c⚡ Test 6: Test des événements', 'color: #3b82f6; font-weight: bold;');

    // Test si on peut cliquer sur un bouton
    const testButton = document.querySelector('.btn-create-client, .btn-create-chauffeur, [data-action="create-camion"], [data-action="create-mission"]');

    if (testButton) {
        console.log('✅ Bouton de test trouvé');
        console.log('  💡 Cliquez sur "Ajouter" pour tester le modal');

        // Ajouter un listener temporaire pour détecter le clic
        const tempListener = () => {
            console.log('🎉 CLIC DÉTECTÉ sur le bouton!');
            testButton.removeEventListener('click', tempListener);
        };
        testButton.addEventListener('click', tempListener);
    } else {
        console.log('⚠️  Aucun bouton de test trouvé sur cette page');
    }

    // ========== RÉSUMÉ FINAL ==========
    console.log('\n%c📊 RÉSUMÉ DU DIAGNOSTIC', 'background: #10b981; color: white; padding: 5px 10px; font-size: 14px; font-weight: bold;');

    const totalDeps = Object.keys(results.dependencies).length;
    const loadedDeps = Object.values(results.dependencies).filter(v => v).length;
    const totalButtons = Object.values(results.buttons).reduce((sum, count) => sum + count, 0);

    console.log(`\n✅ Dépendances: ${loadedDeps}/${totalDeps} chargées`);
    console.log(`✅ Boutons AJAX: ${totalButtons} détectés`);
    console.log(`✅ Managers actifs: ${Object.values(results.managers).filter(v => v).length}`);

    if (results.errors.length > 0) {
        console.log('\n%c⚠️  ERREURS DÉTECTÉES:', 'color: #ef4444; font-weight: bold;');
        results.errors.forEach(err => console.log(err));
    } else {
        console.log('\n%c✅ AUCUNE ERREUR CRITIQUE', 'color: #10b981; font-weight: bold;');
    }

    // ========== INSTRUCTIONS ==========
    console.log('\n%c💡 INSTRUCTIONS', 'background: #f59e0b; color: white; padding: 5px 10px; font-size: 14px; font-weight: bold;');
    console.log('\n1. Si des dépendances manquent:');
    console.log('   → Vérifiez que ajax-utils.js est chargé dans admin.html');
    console.log('   → Vérifiez que Bootstrap 5 JS est chargé');

    console.log('\n2. Si aucun bouton n\'est détecté:');
    console.log('   → Vous êtes peut-être sur une page sans modal AJAX');
    console.log('   → Allez sur /clients/ ou /chauffeurs/ ou /camions/ ou /missions/');

    console.log('\n3. Pour tester un modal:');
    console.log('   → Cliquez sur "Ajouter" ou "Modifier"');
    console.log('   → Le modal devrait s\'ouvrir');
    console.log('   → Si rien ne se passe, regardez les erreurs dans la console');

    console.log('\n%c✅ DIAGNOSTIC TERMINÉ', 'background: #3b82f6; color: white; padding: 5px 10px; font-size: 14px; font-weight: bold;');
    console.log('\n');

    // Exposer les résultats globalement pour consultation
    window.modalTestResults = results;
    console.log('💾 Résultats sauvegardés dans: window.modalTestResults');

})();
