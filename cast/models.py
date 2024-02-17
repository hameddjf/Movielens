from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Actor(models.Model):
    name = models.CharField(_("نام بازیگر"), max_length=500, unique=True)
    poster = models.ImageField(_("عکس بازیگر"), upload_to='actors/', blank=True, null=True)
    class Meta:
        verbose_name = _("بازیگر")
        verbose_name_plural = _("بازیگران")
        
    def __str__(self):
        return self.name

class Director(models.Model):
    full_name = models.CharField(_("نام کارگردان"), max_length=500, unique=True)
    class Meta:
        verbose_name = _("کارگردان")
        verbose_name_plural = _("کارگردان‌ها")
        
    def __str__(self):
        return self.full_name