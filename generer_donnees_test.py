"""
Script pour générer des données de test Excel pour le système de transport
"""

import pandas as pd
from datetime import datetime, timedelta
import random

# Définir la date de départ
date_base = datetime(2025, 1, 1)

# ============================================================================
# 1. ENTREPRISES
# ============================================================================
entreprises_data = [
    {
        'nom': 'Transport Express Mali',
        'adresse': 'Avenue Modibo Keita, Bamako',
        'telephone': '+223 20 22 33 44',
        'email': 'contact@transportexpress.ml',
        'ninea': 'ML123456789',
        'date_creation': date_base,
    },
    {
        'nom': 'Logistique Sahel',
        'adresse': 'Route de Koulikoro, Bamako',
        'telephone': '+223 20 55 66 77',
        'email': 'info@logistiquesahel.ml',
        'ninea': 'ML987654321',
        'date_creation': date_base + timedelta(days=30),
    },
]

# ============================================================================
# 2. UTILISATEURS
# ============================================================================
utilisateurs_data = [
    {
        'email': 'admin.test@transport.com',
        'prenom': 'Amadou',
        'nom': 'Diarra',
        'telephone': '+223 70 11 22 33',
        'role': 'admin',
        'entreprise': 'Transport Express Mali',
        'is_active': True,
    },
    {
        'email': 'manager.test@transport.com',
        'prenom': 'Fatou',
        'nom': 'Traoré',
        'telephone': '+223 70 44 55 66',
        'role': 'manager',
        'entreprise': 'Transport Express Mali',
        'is_active': True,
    },
    {
        'email': 'comptable.test@transport.com',
        'prenom': 'Ibrahim',
        'nom': 'Koné',
        'telephone': '+223 70 77 88 99',
        'role': 'comptable',
        'entreprise': 'Transport Express Mali',
        'is_active': True,
    },
]

# ============================================================================
# 3. CHAUFFEURS
# ============================================================================
chauffeurs_data = [
    {
        'nom': 'Coulibaly',
        'prenom': 'Mamadou',
        'telephone': '+223 70 12 34 56',
        'email': 'mamadou.coulibaly@transport.ml',
        'entreprise': 'Transport Express Mali',
        'numero_permis': 'ML-2020-00123',
        'date_embauche': date_base + timedelta(days=10),
    },
    {
        'nom': 'Sangaré',
        'prenom': 'Ousmane',
        'telephone': '+223 70 23 45 67',
        'email': 'ousmane.sangare@transport.ml',
        'entreprise': 'Transport Express Mali',
        'numero_permis': 'ML-2020-00456',
        'date_embauche': date_base + timedelta(days=15),
    },
    {
        'nom': 'Keita',
        'prenom': 'Seydou',
        'telephone': '+223 70 34 56 78',
        'email': 'seydou.keita@transport.ml',
        'entreprise': 'Transport Express Mali',
        'numero_permis': 'ML-2021-00789',
        'date_embauche': date_base + timedelta(days=20),
    },
    {
        'nom': 'Diallo',
        'prenom': 'Abdoulaye',
        'telephone': '+223 70 45 67 89',
        'email': 'abdoulaye.diallo@transport.ml',
        'entreprise': 'Logistique Sahel',
        'numero_permis': 'ML-2021-01012',
        'date_embauche': date_base + timedelta(days=45),
    },
]

# ============================================================================
# 4. CAMIONS
# ============================================================================
camions_data = [
    {
        'immatriculation': 'BKO-1234-ML',
        'modele': 'Mercedes Actros 1844',
        'capacite_tonnes': 18,
        'entreprise': 'Transport Express Mali',
        'statut': 'disponible',
    },
    {
        'immatriculation': 'BKO-5678-ML',
        'modele': 'Volvo FH 460',
        'capacite_tonnes': 20,
        'entreprise': 'Transport Express Mali',
        'statut': 'disponible',
    },
    {
        'immatriculation': 'BKO-9012-ML',
        'modele': 'Scania R450',
        'capacite_tonnes': 22,
        'entreprise': 'Transport Express Mali',
        'statut': 'disponible',
    },
    {
        'immatriculation': 'KLK-3456-ML',
        'modele': 'MAN TGX 480',
        'capacite_tonnes': 24,
        'entreprise': 'Logistique Sahel',
        'statut': 'disponible',
    },
]

# ============================================================================
# 5. CLIENTS
# ============================================================================
clients_data = [
    {
        'nom': 'SOMAPIL SA',
        'telephone': '+223 20 22 11 00',
        'email': 'contact@somapil.ml',
        'adresse': 'Zone Industrielle, Bamako',
        'ninea': 'ML111222333',
    },
    {
        'nom': 'COMATEX',
        'telephone': '+223 20 23 22 11',
        'email': 'info@comatex.ml',
        'adresse': 'Avenue Kassé Keita, Bamako',
        'ninea': 'ML444555666',
    },
    {
        'nom': 'HUICOMA',
        'telephone': '+223 20 24 33 22',
        'email': 'contact@huicoma.ml',
        'adresse': 'Route de Koulikoro, Bamako',
        'ninea': 'ML777888999',
    },
]

# ============================================================================
# 6. TRANSITAIRES
# ============================================================================
transitaires_data = [
    {
        'nom': 'SDV Mali',
        'telephone': '+223 20 70 11 22',
        'email': 'bamako@sdv.com',
        'adresse': 'ACI 2000, Bamako',
    },
    {
        'nom': 'GETMA Mali',
        'telephone': '+223 20 70 33 44',
        'email': 'contact@getma.ml',
        'adresse': 'Hamdallaye ACI 2000, Bamako',
    },
    {
        'nom': 'MAERSK Mali',
        'telephone': '+223 20 70 55 66',
        'email': 'info@maersk.ml',
        'adresse': 'Badalabougou, Bamako',
    },
]

# ============================================================================
# 7. COMPAGNIES DE CONTENEURS
# ============================================================================
compagnies_data = [
    {
        'nom': 'MAERSK LINE',
        'telephone': '+223 20 71 11 11',
        'email': 'mali@maersk.com',
        'adresse': 'Port de Dakar',
    },
    {
        'nom': 'MSC',
        'telephone': '+223 20 71 22 22',
        'email': 'mali@msc.com',
        'adresse': 'Port de Dakar',
    },
    {
        'nom': 'CMA CGM',
        'telephone': '+223 20 71 33 33',
        'email': 'mali@cmacgm.com',
        'adresse': 'Port de Dakar',
    },
]

# ============================================================================
# 8. CONTENEURS
# ============================================================================
conteneurs_data = [
    {
        'numero_conteneur': 'MAEU1234567',
        'compagnie': 'MAERSK LINE',
        'type_conteneur': '40 HC',
        'poids': 28500,
        'client': 'SOMAPIL SA',
        'transitaire': 'SDV Mali',
    },
    {
        'numero_conteneur': 'MSCU7654321',
        'compagnie': 'MSC',
        'type_conteneur': '20 DRY',
        'poids': 18000,
        'client': 'COMATEX',
        'transitaire': 'GETMA Mali',
    },
    {
        'numero_conteneur': 'CMAU9876543',
        'compagnie': 'CMA CGM',
        'type_conteneur': '40 HC',
        'poids': 30000,
        'client': 'HUICOMA',
        'transitaire': 'MAERSK Mali',
    },
    {
        'numero_conteneur': 'MAEU5555555',
        'compagnie': 'MAERSK LINE',
        'type_conteneur': '40 HC',
        'poids': 27000,
        'client': 'SOMAPIL SA',
        'transitaire': 'SDV Mali',
    },
]

# ============================================================================
# 9. CONTRATS DE TRANSPORT
# ============================================================================
contrats_data = [
    {
        'numero_bl': 'BL-2025-001',
        'conteneur': 'MAEU1234567',
        'client': 'SOMAPIL SA',
        'transitaire': 'SDV Mali',
        'entreprise': 'Transport Express Mali',
        'camion': 'BKO-1234-ML',
        'chauffeur': 'Mamadou Coulibaly',
        'lieu_chargement': 'Port de Dakar',
        'destinataire': 'SOMAPIL Bamako',
        'montant_total': 850000,
        'avance_transport': 350000,
        'caution': 100000,
        'statut_caution': 'bloquee',
        'date_debut': date_base + timedelta(days=30),
        'date_limite_retour': date_base + timedelta(days=53),  # +23 jours
    },
    {
        'numero_bl': 'BL-2025-002',
        'conteneur': 'MSCU7654321',
        'client': 'COMATEX',
        'transitaire': 'GETMA Mali',
        'entreprise': 'Transport Express Mali',
        'camion': 'BKO-5678-ML',
        'chauffeur': 'Ousmane Sangaré',
        'lieu_chargement': 'Port de Dakar',
        'destinataire': 'COMATEX Bamako',
        'montant_total': 750000,
        'avance_transport': 300000,
        'caution': 80000,
        'statut_caution': 'bloquee',
        'date_debut': date_base + timedelta(days=35),
        'date_limite_retour': date_base + timedelta(days=58),
    },
    {
        'numero_bl': 'BL-2025-003',
        'conteneur': 'CMAU9876543',
        'client': 'HUICOMA',
        'transitaire': 'MAERSK Mali',
        'entreprise': 'Transport Express Mali',
        'camion': 'BKO-9012-ML',
        'chauffeur': 'Seydou Keita',
        'lieu_chargement': 'Port de Dakar',
        'destinataire': 'HUICOMA Bamako',
        'montant_total': 900000,
        'avance_transport': 400000,
        'caution': 120000,
        'statut_caution': 'remboursee',
        'date_debut': date_base + timedelta(days=40),
        'date_limite_retour': date_base + timedelta(days=63),
    },
]

# ============================================================================
# 10. MISSIONS
# ============================================================================
missions_data = [
    {
        'numero_bl': 'BL-2025-001',
        'destination': 'Bamako',
        'date_depart': date_base + timedelta(days=30),
        'date_retour': date_base + timedelta(days=50),
        'statut': 'terminée',
        'commentaire': 'Livraison effectuée sans incident',
    },
    {
        'numero_bl': 'BL-2025-002',
        'destination': 'Bamako',
        'date_depart': date_base + timedelta(days=35),
        'date_retour': None,
        'statut': 'en cours',
        'commentaire': 'Mission en cours de route',
    },
    {
        'numero_bl': 'BL-2025-003',
        'destination': 'Bamako',
        'date_depart': date_base + timedelta(days=40),
        'date_retour': date_base + timedelta(days=58),
        'statut': 'terminée',
        'commentaire': 'Livraison effectuée avec succès',
    },
]

# ============================================================================
# 11. CAUTIONS
# ============================================================================
cautions_data = [
    {
        'numero_bl': 'BL-2025-001',
        'montant': 100000,
        'montant_rembourser': 100000,
        'statut': 'remboursee',
        'date_versement': date_base + timedelta(days=30),
        'date_remboursement': date_base + timedelta(days=51),
    },
    {
        'numero_bl': 'BL-2025-002',
        'montant': 80000,
        'montant_rembourser': 0,
        'statut': 'bloquee',
        'date_versement': date_base + timedelta(days=35),
        'date_remboursement': None,
    },
    {
        'numero_bl': 'BL-2025-003',
        'montant': 120000,
        'montant_rembourser': 120000,
        'statut': 'remboursee',
        'date_versement': date_base + timedelta(days=40),
        'date_remboursement': date_base + timedelta(days=59),
    },
]

# ============================================================================
# 12. PAIEMENTS MISSION
# ============================================================================
paiements_data = [
    {
        'numero_bl': 'BL-2025-001',
        'montant_total': 850000,
        'avance': 350000,
        'reliquat': 500000,
        'mode_paiement': 'virement',
        'date_paiement': date_base + timedelta(days=51),
        'est_valide': True,
        'valide_par': 'admin.test@transport.com',
        'commentaire': 'Paiement complet effectué',
    },
    {
        'numero_bl': 'BL-2025-002',
        'montant_total': 750000,
        'avance': 300000,
        'reliquat': 450000,
        'mode_paiement': 'especes',
        'date_paiement': None,
        'est_valide': False,
        'valide_par': None,
        'commentaire': 'En attente de validation',
    },
    {
        'numero_bl': 'BL-2025-003',
        'montant_total': 900000,
        'avance': 400000,
        'reliquat': 500000,
        'mode_paiement': 'virement',
        'date_paiement': date_base + timedelta(days=59),
        'est_valide': True,
        'valide_par': 'manager.test@transport.com',
        'commentaire': 'Paiement validé',
    },
]

# ============================================================================
# 13. MÉCANICIENS
# ============================================================================
mecaniciens_data = [
    {
        'nom': 'Touré',
        'prenom': 'Bakary',
        'telephone': '+223 70 98 76 54',
        'email': 'bakary.toure@mecanique.ml',
        'specialite': 'Moteur Diesel',
    },
    {
        'nom': 'Sidibé',
        'prenom': 'Moussa',
        'telephone': '+223 70 87 65 43',
        'email': 'moussa.sidibe@mecanique.ml',
        'specialite': 'Électricité',
    },
]

# ============================================================================
# 14. FOURNISSEURS
# ============================================================================
fournisseurs_data = [
    {
        'nom': 'Auto Pièces Mali',
        'telephone': '+223 20 22 99 88',
        'email': 'contact@autopieces.ml',
        'adresse': 'Marché de Médine, Bamako',
    },
    {
        'nom': 'Garage Central',
        'telephone': '+223 20 23 88 77',
        'email': 'info@garagecentral.ml',
        'adresse': 'Route de Koulikoro, Bamako',
    },
]

# ============================================================================
# 15. RÉPARATIONS
# ============================================================================
reparations_data = [
    {
        'camion': 'BKO-1234-ML',
        'chauffeur': 'Mamadou Coulibaly',
        'date_reparation': date_base + timedelta(days=25),
        'cout': 450000,
        'description': 'Vidange moteur + changement filtres',
        'mecaniciens': 'Bakary Touré',
    },
    {
        'camion': 'BKO-5678-ML',
        'chauffeur': 'Ousmane Sangaré',
        'date_reparation': date_base + timedelta(days=60),
        'cout': 850000,
        'description': 'Réparation système de freinage',
        'mecaniciens': 'Bakary Touré, Moussa Sidibé',
    },
]

# ============================================================================
# 16. PIÈCES RÉPARÉES
# ============================================================================
pieces_data = [
    {
        'reparation_id': 1,
        'nom_piece': 'Filtre à huile',
        'categorie': 'filtres',
        'reference': 'FO-2024-001',
        'quantite': 1,
        'cout_unitaire': 25000,
        'fournisseur': 'Auto Pièces Mali',
    },
    {
        'reparation_id': 1,
        'nom_piece': 'Huile moteur 15W40',
        'categorie': 'lubrifiants',
        'reference': 'HM-2024-002',
        'quantite': 20,
        'cout_unitaire': 15000,
        'fournisseur': 'Auto Pièces Mali',
    },
    {
        'reparation_id': 2,
        'nom_piece': 'Plaquettes de frein avant',
        'categorie': 'freinage',
        'reference': 'PF-2024-003',
        'quantite': 4,
        'cout_unitaire': 45000,
        'fournisseur': 'Garage Central',
    },
    {
        'reparation_id': 2,
        'nom_piece': 'Disques de frein avant',
        'categorie': 'freinage',
        'reference': 'DF-2024-004',
        'quantite': 2,
        'cout_unitaire': 85000,
        'fournisseur': 'Garage Central',
    },
]

# ============================================================================
# 17. SALAIRES
# ============================================================================
salaires_data = [
    {
        'chauffeur': 'Mamadou Coulibaly',
        'mois': 1,
        'annee': 2025,
        'salaire_base': 250000,
        'prime_mission': 50000,
        'prime_performance': 25000,
        'deduction_avance': 0,
        'deduction_autre': 0,
        'salaire_net': 325000,
        'statut': 'paye',
        'mode_paiement': 'virement',
        'date_paiement': date_base + timedelta(days=35),
    },
    {
        'chauffeur': 'Ousmane Sangaré',
        'mois': 1,
        'annee': 2025,
        'salaire_base': 250000,
        'prime_mission': 40000,
        'prime_performance': 20000,
        'deduction_avance': 50000,
        'deduction_autre': 0,
        'salaire_net': 260000,
        'statut': 'valide',
        'mode_paiement': 'especes',
        'date_paiement': None,
    },
    {
        'chauffeur': 'Seydou Keita',
        'mois': 1,
        'annee': 2025,
        'salaire_base': 250000,
        'prime_mission': 60000,
        'prime_performance': 30000,
        'deduction_avance': 0,
        'deduction_autre': 10000,
        'salaire_net': 330000,
        'statut': 'paye',
        'mode_paiement': 'virement',
        'date_paiement': date_base + timedelta(days=35),
    },
]

# ============================================================================
# GÉNÉRATION DU FICHIER EXCEL
# ============================================================================

def generer_excel():
    """Génère un fichier Excel avec toutes les données de test"""

    # Créer un writer Excel
    output_file = 'donnees_test_transport.xlsx'

    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:

        # Convertir chaque dictionnaire en DataFrame et écrire dans une feuille
        pd.DataFrame(entreprises_data).to_excel(writer, sheet_name='Entreprises', index=False)
        pd.DataFrame(utilisateurs_data).to_excel(writer, sheet_name='Utilisateurs', index=False)
        pd.DataFrame(chauffeurs_data).to_excel(writer, sheet_name='Chauffeurs', index=False)
        pd.DataFrame(camions_data).to_excel(writer, sheet_name='Camions', index=False)
        pd.DataFrame(clients_data).to_excel(writer, sheet_name='Clients', index=False)
        pd.DataFrame(transitaires_data).to_excel(writer, sheet_name='Transitaires', index=False)
        pd.DataFrame(compagnies_data).to_excel(writer, sheet_name='Compagnies', index=False)
        pd.DataFrame(conteneurs_data).to_excel(writer, sheet_name='Conteneurs', index=False)
        pd.DataFrame(contrats_data).to_excel(writer, sheet_name='Contrats', index=False)
        pd.DataFrame(missions_data).to_excel(writer, sheet_name='Missions', index=False)
        pd.DataFrame(cautions_data).to_excel(writer, sheet_name='Cautions', index=False)
        pd.DataFrame(paiements_data).to_excel(writer, sheet_name='Paiements', index=False)
        pd.DataFrame(mecaniciens_data).to_excel(writer, sheet_name='Mécaniciens', index=False)
        pd.DataFrame(fournisseurs_data).to_excel(writer, sheet_name='Fournisseurs', index=False)
        pd.DataFrame(reparations_data).to_excel(writer, sheet_name='Réparations', index=False)
        pd.DataFrame(pieces_data).to_excel(writer, sheet_name='Pièces', index=False)
        pd.DataFrame(salaires_data).to_excel(writer, sheet_name='Salaires', index=False)

    print(f"✅ Fichier Excel généré avec succès: {output_file}")
    print(f"📊 Nombre de feuilles: 17")
    print(f"\nContenu:")
    print(f"  - Entreprises: {len(entreprises_data)} enregistrements")
    print(f"  - Utilisateurs: {len(utilisateurs_data)} enregistrements")
    print(f"  - Chauffeurs: {len(chauffeurs_data)} enregistrements")
    print(f"  - Camions: {len(camions_data)} enregistrements")
    print(f"  - Clients: {len(clients_data)} enregistrements")
    print(f"  - Transitaires: {len(transitaires_data)} enregistrements")
    print(f"  - Compagnies: {len(compagnies_data)} enregistrements")
    print(f"  - Conteneurs: {len(conteneurs_data)} enregistrements")
    print(f"  - Contrats: {len(contrats_data)} enregistrements")
    print(f"  - Missions: {len(missions_data)} enregistrements")
    print(f"  - Cautions: {len(cautions_data)} enregistrements")
    print(f"  - Paiements: {len(paiements_data)} enregistrements")
    print(f"  - Mécaniciens: {len(mecaniciens_data)} enregistrements")
    print(f"  - Fournisseurs: {len(fournisseurs_data)} enregistrements")
    print(f"  - Réparations: {len(reparations_data)} enregistrements")
    print(f"  - Pièces: {len(pieces_data)} enregistrements")
    print(f"  - Salaires: {len(salaires_data)} enregistrements")

    return output_file

if __name__ == '__main__':
    generer_excel()
