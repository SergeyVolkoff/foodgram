# Generated by Django 4.2.13 on 2024-08-29 14:18

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0003_alter_recipeingredient_options_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='FavoriteRecipes',
            new_name='FavoriteRecipe',
        ),
    ]
