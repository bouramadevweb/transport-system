from django.db import migrations, models
import django.core.validators
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0026_camion_date_entree_date_sortie'),
    ]

    operations = [
        migrations.AddField(
            model_name='transitaire',
            name='commission_percentage',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text='Pourcentage de commission du transitaire (0-100)',
                max_digits=5,
                validators=[
                    django.core.validators.MinValueValidator(Decimal('0')),
                    django.core.validators.MaxValueValidator(Decimal('100')),
                ],
            ),
        ),
    ]
