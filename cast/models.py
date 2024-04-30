from django.db import models
from django.utils.translation import gettext_lazy as _

from main.models import Movie
# Create your models here.


class Actor(models.Model):
    name = models.CharField(_("نام بازیگر"), max_length=500, unique=True)
    poster = models.URLField(_("تصویر بازیگر"), null=True, blank=True)
    # poster = models.ImageField(upload_to='actors/', blank=True, null=True)
    tmdb_id = models.IntegerField(_("ایدی بازیگر"),
                                  unique=True, null=True, blank=True)

    movies = models.ManyToManyField(Movie, related_name='actors', blank=True,
                                    verbose_name=_('فیلم‌های کارگردان'))

    class Meta:
        verbose_name = _("بازیگر")
        verbose_name_plural = _("بازیگران")

    def __str__(self):
        return self.name


class Director(models.Model):
    tmdb_id = models.IntegerField(
        _("شناسه TMDB کارگردان"), unique=True)
    full_name = models.CharField(
        _("نام کارگردان"), max_length=500, unique=True)
    poster = models.URLField(_('تصویر کارگردان'), blank=True, null=True)
    movies = models.ManyToManyField(Movie, related_name='directors',
                                    blank=True,
                                    verbose_name=_('فیلم‌های کارگردان'))

    class Meta:
        verbose_name = _("کارگردان")
        verbose_name_plural = _("کارگردان‌ها")

    def __str__(self):
        return self.full_name
