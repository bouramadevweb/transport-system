#!/usr/bin/env python
"""
Script de test des endpoints AJAX
Vérifie que toutes les URLs AJAX sont bien configurées
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport_system.settings')
django.setup()

from django.urls import reverse, NoReverseMatch

class AjaxEndpointTester:
    def __init__(self):
        self.endpoints = {
            'Clients': [
                ('ajax_client_create', None, 'GET/POST'),
                ('ajax_client_update', {'pk': 'test-client-id'}, 'GET/POST'),
                ('ajax_search_clients', None, 'GET'),
            ],
            'Chauffeurs': [
                ('ajax_chauffeur_create', None, 'GET/POST'),
                ('ajax_chauffeur_update', {'pk': 'test-chauffeur-id'}, 'GET/POST'),
                ('ajax_search_chauffeurs', None, 'GET'),
            ],
            'Camions': [
                ('ajax_camion_create_form', None, 'GET'),
                ('ajax_camion_create', None, 'POST'),
                ('ajax_camion_update_form', {'pk': 'test-camion-id'}, 'GET'),
                ('ajax_camion_update', {'pk': 'test-camion-id'}, 'POST'),
            ],
            'Missions': [
                ('ajax_mission_create_form', None, 'GET'),
                ('ajax_mission_create', None, 'POST'),
                ('ajax_mission_update_form', {'pk': 'test-mission-id'}, 'GET'),
                ('ajax_mission_update', {'pk': 'test-mission-id'}, 'POST'),
                ('ajax_terminer_mission_modal', {'pk': 'test-mission-id'}, 'GET'),
                ('ajax_terminer_mission', {'pk': 'test-mission-id'}, 'POST'),
            ],
            'Paiements': [
                ('ajax_filter_paiements', None, 'GET'),
                ('ajax_validation_modal', {'pk': 'test-paiement-id'}, 'GET'),
                ('ajax_validate_paiement', {'pk': 'test-paiement-id'}, 'POST'),
            ],
            'Dashboard': [
                ('ajax_dashboard_filter', None, 'GET'),
            ],
            'Notifications': [
                ('ajax_mark_notification_read', {'pk': 'test-notif-id'}, 'POST'),
                ('ajax_mark_all_notifications_read', None, 'POST'),
                ('ajax_get_notifications', None, 'GET'),
            ],
            'Affectations': [
                ('ajax_affectation_create', None, 'GET/POST'),
                ('ajax_affectation_update', {'pk': 'test-affectation-id'}, 'GET/POST'),
            ],
            'Entreprises': [
                ('ajax_entreprise_create', None, 'GET/POST'),
                ('ajax_entreprise_update', {'pk': 'test-entreprise-id'}, 'GET/POST'),
            ],
            'Conteneurs': [
                ('ajax_conteneur_create', None, 'GET/POST'),
                ('ajax_conteneur_update', {'pk': 'test-conteneur-id'}, 'GET/POST'),
            ],
            'Contrats': [
                ('ajax_contrat_create', None, 'GET/POST'),
                ('ajax_contrat_update', {'pk': 'test-contrat-id'}, 'GET/POST'),
            ],
            'Prestations': [
                ('ajax_prestation_create', None, 'GET/POST'),
                ('ajax_prestation_update', {'pk': 'test-prestation-id'}, 'GET/POST'),
            ],
        }

        self.results = {
            'success': 0,
            'error': 0,
            'warnings': 0
        }

    def test_url_resolution(self, url_name, kwargs):
        """Teste si une URL peut être résolue"""
        try:
            url = reverse(url_name, kwargs=kwargs) if kwargs else reverse(url_name)
            return True, url
        except NoReverseMatch as e:
            return False, str(e)

    def check_endpoint(self, category, url_name, kwargs, methods):
        """Vérifie un endpoint AJAX"""
        success, result = self.test_url_resolution(url_name, kwargs)

        if success:
            print(f"  ✓ {url_name:<40} {result:<50} [{methods}]")
            self.results['success'] += 1
        else:
            print(f"  ✗ {url_name:<40} ERROR: {result}")
            self.results['error'] += 1

    def run_tests(self):
        """Exécute tous les tests"""
        print(f"\n{'='*100}")
        print(f"{'VÉRIFICATION DES ENDPOINTS AJAX':^100}")
        print(f"{'='*100}\n")

        for category, endpoints in self.endpoints.items():
            print(f"\n▶ {category}")
            print(f"{'-'*100}")

            for url_name, kwargs, methods in endpoints:
                self.check_endpoint(category, url_name, kwargs, methods)

        # Résumé
        print(f"\n{'='*100}")
        print(f"\nRÉSUMÉ:")
        print(f"  ✓ Succès: {self.results['success']}")
        print(f"  ✗ Erreurs: {self.results['error']}")
        print(f"  ⚠ Avertissements: {self.results['warnings']}")

        total = self.results['success'] + self.results['error']
        success_rate = (self.results['success'] / total * 100) if total > 0 else 0

        print(f"\n  Taux de réussite: {success_rate:.1f}%")

        if self.results['error'] == 0:
            print(f"\n{'✓ TOUS LES ENDPOINTS AJAX SONT CONFIGURÉS CORRECTEMENT!':^100}")
        else:
            print(f"\n{'✗ CERTAINS ENDPOINTS NÉCESSITENT UNE ATTENTION!':^100}")

        print(f"\n{'='*100}\n")

        return self.results['error'] == 0


def main():
    """Point d'entrée principal"""
    print(f"\nDémarrage des tests d'endpoints AJAX...")

    tester = AjaxEndpointTester()
    success = tester.run_tests()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
