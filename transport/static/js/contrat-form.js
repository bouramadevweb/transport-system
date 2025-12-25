/**
 * Contrat Form - Calculs automatiques
 *
 * Gère les calculs automatiques pour les formulaires de contrat:
 * - Date limite de retour (Date début + 23 jours)
 * - Reliquat (Montant total - Avance)
 */

/**
 * Calculer la date limite de retour (Date début + 23 jours)
 */
function calculerDateLimiteRetour() {
    const dateDebutField = document.getElementById('id_date_debut');
    const dateLimiteField = document.getElementById('id_date_limite_retour');

    if (!dateDebutField || !dateLimiteField) {
        console.warn('Champs date non trouvés');
        return;
    }

    const dateDebut = dateDebutField.value;
    if (!dateDebut) {
        console.log('Pas de date début saisie');
        return;
    }

    // Calculer la date + 23 jours
    const date = new Date(dateDebut);
    date.setDate(date.getDate() + 23);

    // Formater au format YYYY-MM-DD
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const dateLimite = `${year}-${month}-${day}`;

    // Mettre à jour le champ
    dateLimiteField.value = dateLimite;

    // Indication visuelle
    dateLimiteField.style.backgroundColor = '#d1ecf1';
    dateLimiteField.title = 'Calculé automatiquement : Date début + 23 jours';

    console.log(`✅ Date limite calculée: ${dateDebut} + 23 jours = ${dateLimite}`);
}

/**
 * Calculer le reliquat (Montant total - Avance)
 */
function calculerReliquat() {
    const montantTotalField = document.getElementById('id_montant_total');
    const avanceField = document.getElementById('id_avance_transport');
    const reliquatField = document.getElementById('id_reliquat_transport');

    if (!montantTotalField || !avanceField || !reliquatField) {
        console.warn('Champs financiers non trouvés');
        return;
    }

    const montantTotal = parseFloat(montantTotalField.value) || 0;
    const avance = parseFloat(avanceField.value) || 0;
    const reliquat = montantTotal - avance;

    // Mettre à jour le champ avec 2 décimales
    reliquatField.value = reliquat.toFixed(2);

    // Indication visuelle selon le résultat
    if (reliquat < 0) {
        // Avance > Montant total
        reliquatField.style.backgroundColor = '#f8d7da';
        reliquatField.style.color = '#721c24';
        reliquatField.title = '⚠️ Attention : L\'avance dépasse le montant total';
    } else if (reliquat === 0) {
        // Paiement intégral
        reliquatField.style.backgroundColor = '#d4edda';
        reliquatField.style.color = '#155724';
        reliquatField.title = '✅ Paiement intégral en avance';
    } else {
        // Normal
        reliquatField.style.backgroundColor = '#d1ecf1';
        reliquatField.style.color = '#0c5460';
        reliquatField.title = `Reliquat à payer: ${reliquat.toFixed(2)} FCFA`;
    }

    console.log(`✅ Reliquat calculé: ${montantTotal} - ${avance} = ${reliquat.toFixed(2)}`);
}

/**
 * Variable pour éviter les boucles infinies lors de la sélection bidirectionnelle
 */
let isUpdatingVehicleDriver = false;

/**
 * Charger automatiquement le chauffeur affecté au camion sélectionné
 */
function chargerChauffeurAffecte() {
    if (isUpdatingVehicleDriver) return;

    const camionSelect = document.getElementById('id_camion');
    const chauffeurSelect = document.getElementById('id_chauffeur');

    if (!camionSelect || !chauffeurSelect) {
        return;
    }

    const camionId = camionSelect.value;
    if (!camionId) {
        return;
    }

    isUpdatingVehicleDriver = true;
    console.log('🚛 Chargement du chauffeur pour camion:', camionId);

    // Appel AJAX pour récupérer le chauffeur affecté au camion
    fetch(`/api/camion/${camionId}/chauffeur/`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.chauffeur_id) {
                // Sélectionner automatiquement le chauffeur
                chauffeurSelect.value = data.chauffeur_id;

                // Indication visuelle
                chauffeurSelect.style.backgroundColor = '#d1ecf1';
                chauffeurSelect.style.border = '2px solid #0c5460';
                chauffeurSelect.title = `Chauffeur affecté : ${data.chauffeur_nom}`;

                console.log(`✅ Chauffeur affecté automatiquement : ${data.chauffeur_nom}`);
            } else {
                // Aucun chauffeur affecté
                chauffeurSelect.value = '';
                chauffeurSelect.style.backgroundColor = '#fff3cd';
                chauffeurSelect.style.border = '1px solid #ffc107';
                chauffeurSelect.title = '⚠️ Aucun chauffeur affecté à ce camion';

                console.warn('⚠️ Aucun chauffeur affecté à ce camion');
            }
        })
        .catch(error => {
            console.error('❌ Erreur lors de la récupération du chauffeur:', error);
            chauffeurSelect.style.backgroundColor = '#f8d7da';
            chauffeurSelect.style.border = '1px solid #dc3545';
            chauffeurSelect.title = '❌ Erreur lors de la récupération du chauffeur';
        })
        .finally(() => {
            isUpdatingVehicleDriver = false;
        });
}

/**
 * Charger automatiquement le camion affecté au chauffeur sélectionné
 */
function chargerCamionAffecte() {
    if (isUpdatingVehicleDriver) return;

    const camionSelect = document.getElementById('id_camion');
    const chauffeurSelect = document.getElementById('id_chauffeur');

    if (!camionSelect || !chauffeurSelect) {
        return;
    }

    const chauffeurId = chauffeurSelect.value;
    if (!chauffeurId) {
        return;
    }

    isUpdatingVehicleDriver = true;
    console.log('👨‍✈️ Chargement du camion pour chauffeur:', chauffeurId);

    // Appel AJAX pour récupérer le camion affecté au chauffeur
    fetch(`/api/chauffeur/${chauffeurId}/camion/`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.camion_id) {
                // Sélectionner automatiquement le camion
                camionSelect.value = data.camion_id;

                // Indication visuelle
                camionSelect.style.backgroundColor = '#d1ecf1';
                camionSelect.style.border = '2px solid #0c5460';
                camionSelect.title = `Camion affecté : ${data.camion_immatriculation}`;

                console.log(`✅ Camion affecté automatiquement : ${data.camion_immatriculation}`);
            } else {
                // Aucun camion affecté
                camionSelect.value = '';
                camionSelect.style.backgroundColor = '#fff3cd';
                camionSelect.style.border = '1px solid #ffc107';
                camionSelect.title = '⚠️ Aucun camion affecté à ce chauffeur';

                console.warn('⚠️ Aucun camion affecté à ce chauffeur');
            }
        })
        .catch(error => {
            console.error('❌ Erreur lors de la récupération du camion:', error);
            camionSelect.style.backgroundColor = '#f8d7da';
            camionSelect.style.border = '1px solid #dc3545';
            camionSelect.title = '❌ Erreur lors de la récupération du camion';
        })
        .finally(() => {
            isUpdatingVehicleDriver = false;
        });
}

/**
 * Initialiser les calculs automatiques pour le formulaire de contrat
 */
function initContratFormCalculs() {
    console.log('🔧 Initialisation des calculs automatiques contrat...');

    // Calculer au chargement si des valeurs existent
    calculerDateLimiteRetour();
    calculerReliquat();

    // Event listener pour la date de début
    const dateDebutField = document.getElementById('id_date_debut');
    if (dateDebutField) {
        dateDebutField.addEventListener('change', function() {
            console.log('📅 Date début changée:', this.value);
            calculerDateLimiteRetour();
        });
        console.log('✅ Event listener ajouté sur date_debut');
    } else {
        console.warn('❌ Champ date_debut non trouvé');
    }

    // Event listeners pour les champs financiers
    const montantTotalField = document.getElementById('id_montant_total');
    if (montantTotalField) {
        montantTotalField.addEventListener('input', function() {
            console.log('💰 Montant total changé:', this.value);
            calculerReliquat();
        });
        console.log('✅ Event listener ajouté sur montant_total');
    } else {
        console.warn('❌ Champ montant_total non trouvé');
    }

    const avanceField = document.getElementById('id_avance_transport');
    if (avanceField) {
        avanceField.addEventListener('input', function() {
            console.log('💵 Avance changée:', this.value);
            calculerReliquat();
        });
        console.log('✅ Event listener ajouté sur avance_transport');
    } else {
        console.warn('❌ Champ avance_transport non trouvé');
    }

    // ✅ Event listeners pour camion/chauffeur
    const camionSelect = document.getElementById('id_camion');
    if (camionSelect) {
        camionSelect.addEventListener('change', function() {
            console.log('🚛 Camion changé:', this.value);
            chargerChauffeurAffecte();
        });
        console.log('✅ Event listener ajouté sur camion');
    } else {
        console.warn('❌ Champ camion non trouvé');
    }

    const chauffeurSelect = document.getElementById('id_chauffeur');
    if (chauffeurSelect) {
        chauffeurSelect.addEventListener('change', function() {
            console.log('👨‍✈️ Chauffeur changé:', this.value);
            chargerCamionAffecte();
        });
        console.log('✅ Event listener ajouté sur chauffeur');
    } else {
        console.warn('❌ Champ chauffeur non trouvé');
    }

    // Charger le chauffeur si un camion est déjà sélectionné (mode édition)
    if (camionSelect && camionSelect.value) {
        chargerChauffeurAffecte();
    }

    console.log('✅ Calculs automatiques initialisés');
}

// Export pour utilisation globale
window.calculerDateLimiteRetour = calculerDateLimiteRetour;
window.calculerReliquat = calculerReliquat;
window.chargerChauffeurAffecte = chargerChauffeurAffecte;
window.chargerCamionAffecte = chargerCamionAffecte;
window.initContratFormCalculs = initContratFormCalculs;
