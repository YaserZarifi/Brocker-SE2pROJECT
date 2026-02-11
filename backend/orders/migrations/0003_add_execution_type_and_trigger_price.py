# Generated manually - Binance-style order types

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="execution_type",
            field=models.CharField(
                choices=[
                    ("limit", "Limit"),
                    ("market", "Market"),
                    ("stop_loss", "Stop-Loss"),
                    ("take_profit", "Take-Profit"),
                ],
                default="limit",
                max_length=12,
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="trigger_price",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=12, null=True
            ),
        ),
    ]
