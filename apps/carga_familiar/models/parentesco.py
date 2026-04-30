from django.db import models


class Parentesco(models.Model):
    descripcion = models.CharField(max_length=50, unique=True)
    estatus = models.BooleanField(default=True)

    class Meta:
        managed             = True
        db_table            = 'carga_familiar\".\"parentesco'
        verbose_name        = 'Parentesco'
        verbose_name_plural = 'Parentescos'

    def __str__(self):
        return self.descripcion