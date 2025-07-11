from django.db import models

# Create your models here.

class ConsultaIALog(models.Model):
    consulta = models.TextField()
    respuesta = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
