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
        return;
    }

    const dateDebut = dateDebutField.value;
    if (!dateDebut) {
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
}

/**
 * Calculer le reliquat (Montant total - Avance)
 */
function calculerReliquat() {
    const montantTotalField = document.getElementById('id_montant_total');
    const avanceField = document.getElementById('id_avance_transport');
    const reliquatField = document.getElementById('id_reliquat_transport');

    if (!montantTotalField || !avanceField || !reliquatField) {
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
}

/**
 * Variable pour éviter les boucles infinies lors de la sélection bidirectionnelle
 */
let isUpdatingVehicleDriver = false;

/**
 * Charger automatiquement le client et le transitaire du conteneur sélectionné
 */
function chargerClientTransitaire() {
    const conteneurSelect = document.getElementById('id_conteneur');
    const clientSelect = document.getElementById('id_client');
    const transitaireSelect = document.getElementById('id_transitaire');

    if (!conteneurSelect || !clientSelect || !transitaireSelect) {
        return;
    }

    const conteneurId = conteneurSelect.value;

    if (!conteneurId) {
        return;
    }

    // Appel AJAX pour récupérer le client et le transitaire du conteneur
    fetch(`/api/conteneur/${conteneurId}/info/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Sélectionner automatiquement le client si disponible
                if (data.client_id) {
                    clientSelect.value = data.client_id;
                    clientSelect.style.backgroundColor = '#d1ecf1';
                    clientSelect.style.border = '2px solid #0c5460';
                    clientSelect.title = `Client du conteneur : ${data.client_nom}`;
                } else {
                    clientSelect.value = '';
                    clientSelect.style.backgroundColor = '#fff3cd';
                    clientSelect.style.border = '1px solid #ffc107';
                    clientSelect.title = '⚠️ Aucun client associé à ce conteneur';
                }

                // Sélectionner automatiquement le transitaire si disponible
                if (data.transitaire_id) {
                    transitaireSelect.value = data.transitaire_id;
                    transitaireSelect.style.backgroundColor = '#d1ecf1';
                    transitaireSelect.style.border = '2px solid #0c5460';
                    transitaireSelect.title = `Transitaire du conteneur : ${data.transitaire_nom}`;
                } else {
                    transitaireSelect.value = '';
                    transitaireSelect.style.backgroundColor = '#fff3cd';
                    transitaireSelect.style.border = '1px solid #ffc107';
                    transitaireSelect.title = '⚠️ Aucun transitaire associé à ce conteneur';
                }
            } else {
                clientSelect.style.backgroundColor = '#f8d7da';
                clientSelect.style.border = '1px solid #dc3545';
                transitaireSelect.style.backgroundColor = '#f8d7da';
                transitaireSelect.style.border = '1px solid #dc3545';
            }
        })
        .catch(error => {
            console.error('Erreur chargement conteneur:', error);
            clientSelect.style.backgroundColor = '#f8d7da';
            clientSelect.style.border = '1px solid #dc3545';
            transitaireSelect.style.backgroundColor = '#f8d7da';
            transitaireSelect.style.border = '1px solid #dc3545';
        });
}

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
            } else {
                // Aucun chauffeur affecté
                chauffeurSelect.value = '';
                chauffeurSelect.style.backgroundColor = '#fff3cd';
                chauffeurSelect.style.border = '1px solid #ffc107';
                chauffeurSelect.title = '⚠️ Aucun chauffeur affecté à ce camion';
            }
        })
        .catch(error => {
            console.error('Erreur chargement chauffeur:', error);
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
            } else {
                // Aucun camion affecté
                camionSelect.value = '';
                camionSelect.style.backgroundColor = '#fff3cd';
                camionSelect.style.border = '1px solid #ffc107';
                camionSelect.title = '⚠️ Aucun camion affecté à ce chauffeur';
            }
        })
        .catch(error => {
            console.error('Erreur chargement camion:', error);
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
    // Calculer le reliquat au chargement si des valeurs existent
    calculerReliquat();

    // En mode création (date_limite_retour vide), calculer depuis date_debut
    const dateLimiteField = document.getElementById('id_date_limite_retour');
    if (dateLimiteField && !dateLimiteField.value) {
        calculerDateLimiteRetour();
    }

    // Event listener pour la date de début
    const dateDebutField = document.getElementById('id_date_debut');
    if (dateDebutField) {
        dateDebutField.addEventListener('change', calculerDateLimiteRetour);
    }

    // Event listeners pour les champs financiers
    const montantTotalField = document.getElementById('id_montant_total');
    if (montantTotalField) {
        montantTotalField.addEventListener('input', calculerReliquat);
    }

    const avanceField = document.getElementById('id_avance_transport');
    if (avanceField) {
        avanceField.addEventListener('input', calculerReliquat);
    }

    // Event listeners pour camion/chauffeur (seulement sur changement utilisateur)
    const camionSelect = document.getElementById('id_camion');
    if (camionSelect) {
        camionSelect.addEventListener('change', chargerChauffeurAffecte);
    }

    const chauffeurSelect = document.getElementById('id_chauffeur');
    if (chauffeurSelect) {
        chauffeurSelect.addEventListener('change', chargerCamionAffecte);
    }

    // Auto-remplir le chauffeur depuis l'affectation du camion sélectionné
    // (aussi bien en création qu'en modification)
    if (camionSelect && camionSelect.value) {
        chargerChauffeurAffecte();
    }

    // Event listener pour conteneur (seulement sur changement utilisateur)
    const conteneurSelect = document.getElementById('id_conteneur');
    if (conteneurSelect) {
        conteneurSelect.addEventListener('change', chargerClientTransitaire);

        // Auto-remplir client/transitaire si conteneur sélectionné mais client vide
        const clientSelect = document.getElementById('id_client');
        if (conteneurSelect.value && clientSelect && !clientSelect.value) {
            chargerClientTransitaire();
        }
    }
}

// Export pour utilisation globale
window.calculerDateLimiteRetour = calculerDateLimiteRetour;
window.calculerReliquat = calculerReliquat;
window.chargerClientTransitaire = chargerClientTransitaire;
window.chargerChauffeurAffecte = chargerChauffeurAffecte;
window.chargerCamionAffecte = chargerCamionAffecte;
window.initContratFormCalculs = initContratFormCalculs;
