from django.db import models
from django.urls import reverse

# Create your models here.


class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=150)

    class Meta:
        verbose_name = 'دسته بندی'
        verbose_name_plural = 'دسته بندی ها'

    def get_absolute_url(self):
        return reverse("products_by_category", args=[self.slug])

    def __str__(self):
        return self.title
