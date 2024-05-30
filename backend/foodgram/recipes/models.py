from django.db import models


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=100,
        unique=True
    )
    slug = models.SlugField()
    color = models.CharField(
        verbose_name = 'Название',
        max_length=100,
    )

    