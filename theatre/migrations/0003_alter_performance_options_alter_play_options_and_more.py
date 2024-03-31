# Generated by Django 5.0.3 on 2024-03-31 16:19

import theatre.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("theatre", "0002_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="performance",
            options={"ordering": ("-show_time",)},
        ),
        migrations.AlterModelOptions(
            name="play",
            options={"ordering": ("title",)},
        ),
        migrations.AlterModelOptions(
            name="reservation",
            options={"ordering": ("-created_at",)},
        ),
        migrations.AlterModelOptions(
            name="ticket",
            options={"ordering": ("performance", "row", "seat")},
        ),
        migrations.AddField(
            model_name="play",
            name="image",
            field=models.ImageField(
                null=True, upload_to=theatre.models.play_image_path
            ),
        ),
    ]