# Generated by Django 4.2.16 on 2024-12-16 23:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipe_catalog', '0003_recipe_cooking_time_recipe_created_at_recipe_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='title',
            field=models.CharField(db_index=True, max_length=300),
        ),
        migrations.AddIndex(
            model_name='recipeingredient',
            index=models.Index(fields=['recipe', 'ingredient'], name='recipe_cata_recipe__f3700d_idx'),
        ),
    ]
