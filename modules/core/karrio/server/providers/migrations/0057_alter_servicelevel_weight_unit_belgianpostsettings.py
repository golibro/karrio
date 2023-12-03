# Generated by Django 4.2.7 on 2023-11-11 11:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("providers", "0056_asendiaussettings_geodissettings_code_client_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="servicelevel",
            name="weight_unit",
            field=models.CharField(
                blank=True,
                choices=[("KG", "KG"), ("LB", "LB"), ("OZ", "OZ"), ("G", "G")],
                max_length=2,
                null=True,
            ),
        ),
        migrations.CreateModel(
            name="BelgianPostSettings",
            fields=[
                (
                    "carrier_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="providers.carrier",
                    ),
                ),
                ("account_id", models.CharField(max_length=100)),
                ("passphrase", models.CharField(max_length=100)),
                (
                    "services",
                    models.ManyToManyField(blank=True, to="providers.servicelevel"),
                ),
            ],
            options={
                "verbose_name": "Belgian Post Settings",
                "verbose_name_plural": "Belgian Post Settings",
                "db_table": "bpost-settings",
            },
            bases=("providers.carrier",),
        ),
    ]