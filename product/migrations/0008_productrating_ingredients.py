# Generated by Django 4.2.5 on 2024-09-10 08:32

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0007_delete_ingredient_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='productrating',
            name='ingredients',
            field=models.TextField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
