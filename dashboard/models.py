from django.db import models
from django.contrib.auth.models import User

class Empresa(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_empresa', null=True, blank=True)
    nombre = models.CharField(max_length=150)
    rubro = models.CharField(max_length=150, blank=True, null=True)
    tamano = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    contacto_principal = models.CharField(max_length=150, blank=True, null=True)
    ingresos_anuales = models.CharField(max_length=100, blank=True, null=True) # Ej: $51.4B USD
    programa_sostenibilidad = models.CharField(max_length=200, blank=True, null=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class EtapaProductiva(models.Model):
    nombre = models.CharField(max_length=100) # Ej: Corte, Confección, Tintorería
    orden = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre

class Merma(models.Model):
    TIPO_CHOICES = [
        ('operativa', 'Operativa'),
        ('anormal', 'Anormal'),
    ]
    PRIORIDAD_CHOICES = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    ]
    
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='mermas')
    etapa = models.ForeignKey(EtapaProductiva, on_delete=models.CASCADE)
    problema_detectado = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2) # Ej: 38.50
    impacto_economico = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.empresa.nombre} - {self.etapa.nombre} ({self.porcentaje}%)"