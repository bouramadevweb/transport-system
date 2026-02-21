"""
Management command pour générer les icônes PWA

Génère les icônes PNG dans différentes tailles pour la PWA
"""

from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Génère les icônes PWA en différentes tailles'

    ICON_SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default=None,
            help='Répertoire de sortie pour les icônes'
        )

    def handle(self, *args, **options):
        # Répertoire de sortie
        output_dir = options.get('output_dir')
        if not output_dir:
            output_dir = os.path.join(
                settings.BASE_DIR, 'transport', 'static', 'icons'
            )

        # Créer le répertoire si nécessaire
        os.makedirs(output_dir, exist_ok=True)

        self.stdout.write(f"Génération des icônes dans: {output_dir}")

        for size in self.ICON_SIZES:
            self.generate_icon(size, output_dir)
            self.stdout.write(
                self.style.SUCCESS(f"  ✓ icon-{size}x{size}.png créé")
            )

        self.stdout.write(
            self.style.SUCCESS(f"\n✓ {len(self.ICON_SIZES)} icônes générées avec succès!")
        )

    def generate_icon(self, size, output_dir):
        """Génère une icône de la taille spécifiée"""
        # Créer l'image avec fond bleu dégradé
        img = Image.new('RGB', (size, size), '#2563eb')
        draw = ImageDraw.Draw(img)

        # Dessiner un cercle de fond (dégradé simulé)
        padding = int(size * 0.05)
        draw.ellipse(
            [padding, padding, size - padding, size - padding],
            fill='#1e40af'
        )

        # Dessiner un camion simplifié
        self.draw_truck(draw, size)

        # Sauvegarder
        filename = f"icon-{size}x{size}.png"
        filepath = os.path.join(output_dir, filename)
        img.save(filepath, 'PNG')

    def draw_truck(self, draw, size):
        """Dessine un camion simplifié"""
        # Proportions basées sur la taille
        scale = size / 512

        # Offset pour centrer
        offset_x = int(96 * scale)
        offset_y = int(160 * scale)

        # Couleur blanche pour le camion
        white = '#ffffff'
        dark = '#1e293b'
        blue = '#2563eb'

        # Corps du camion (rectangle avec coins arrondis simulés)
        body_x1 = int(offset_x + 0)
        body_y1 = int(offset_y + 60 * scale)
        body_x2 = int(offset_x + 200 * scale)
        body_y2 = int(offset_y + 160 * scale)
        draw.rectangle([body_x1, body_y1, body_x2, body_y2], fill=white)

        # Cabine
        cab_points = [
            (int(offset_x + 200 * scale), int(offset_y + 60 * scale)),
            (int(offset_x + 200 * scale), int(offset_y + 160 * scale)),
            (int(offset_x + 280 * scale), int(offset_y + 160 * scale)),
            (int(offset_x + 280 * scale), int(offset_y + 100 * scale)),
            (int(offset_x + 240 * scale), int(offset_y + 60 * scale)),
        ]
        draw.polygon(cab_points, fill=white)

        # Fenêtre
        window_x1 = int(offset_x + 210 * scale)
        window_y1 = int(offset_y + 75 * scale)
        window_x2 = int(offset_x + 260 * scale)
        window_y2 = int(offset_y + 110 * scale)
        draw.rectangle([window_x1, window_y1, window_x2, window_y2], fill=blue)

        # Roues
        wheel_radius = int(30 * scale)
        wheel_center_radius = int(15 * scale)

        # Roue arrière
        wheel1_x = int(offset_x + 70 * scale)
        wheel1_y = int(offset_y + 170 * scale)
        draw.ellipse(
            [wheel1_x - wheel_radius, wheel1_y - wheel_radius,
             wheel1_x + wheel_radius, wheel1_y + wheel_radius],
            fill=dark
        )
        draw.ellipse(
            [wheel1_x - wheel_center_radius, wheel1_y - wheel_center_radius,
             wheel1_x + wheel_center_radius, wheel1_y + wheel_center_radius],
            fill=white
        )

        # Roue avant
        wheel2_x = int(offset_x + 240 * scale)
        wheel2_y = int(offset_y + 170 * scale)
        draw.ellipse(
            [wheel2_x - wheel_radius, wheel2_y - wheel_radius,
             wheel2_x + wheel_radius, wheel2_y + wheel_radius],
            fill=dark
        )
        draw.ellipse(
            [wheel2_x - wheel_center_radius, wheel2_y - wheel_center_radius,
             wheel2_x + wheel_center_radius, wheel2_y + wheel_center_radius],
            fill=white
        )

        # Lignes du conteneur
        line_width = max(1, int(4 * scale))
        for i, x_offset in enumerate([50, 100, 150]):
            x = int(offset_x + x_offset * scale)
            y1 = int(offset_y + 80 * scale)
            y2 = int(offset_y + 140 * scale)
            draw.line([(x, y1), (x, y2)], fill=blue, width=line_width)
