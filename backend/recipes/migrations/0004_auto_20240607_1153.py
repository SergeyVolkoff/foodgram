# Generated by Django 2.2.16 on 2024-06-07 11:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20240607_1153'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={},
        ),
        migrations.AlterField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор рецепта'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='tag',
            field=models.ManyToManyField(to='recipes.Tag', verbose_name='Tags'),
        ),
    ]
