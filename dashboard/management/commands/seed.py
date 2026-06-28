import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dashboard.models import Empresa, EtapaProductiva, Merma


class Command(BaseCommand):
    help = 'Poblar la BD con datos de prueba'

    def handle(self, *args, **kwargs):
        self.stdout.write('🧹 Limpiando datos anteriores...')
        Merma.objects.all().delete()
        Empresa.objects.all().delete()
        EtapaProductiva.objects.all().delete()
        User.objects.filter(username__in=['admin', 'empresa1']).delete()

        # Etapas
        self.stdout.write('🏭 Creando etapas productivas...')
        etapas_data = [
            ('Corte', 1),
            ('Confección', 2),
            ('Acabado', 3),
            ('Control de Calidad', 4),
        ]
        etapas = []
        for nombre, orden in etapas_data:
            e = EtapaProductiva.objects.create(nombre=nombre, orden=orden)
            etapas.append(e)

        # Admin
        self.stdout.write('👤 Creando usuario admin...')
        User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True,
            is_superuser=True,
        )

        # Empresa1
        self.stdout.write('🏢 Creando usuario empresa1 y su empresa...')
        user_empresa = User.objects.create_user(
            username='empresa1',
            password='emp123',
        )
        empresa = Empresa.objects.create(
            usuario=user_empresa,
            nombre='Textil Sur S.A.',
            rubro='Confección de ropa deportiva',
            tamano='Mediana empresa',
            region='Región Metropolitana',
            contacto_principal='Juan Pérez',
            ingresos_anuales='$2.1M USD',
            programa_sostenibilidad='ISO 14001 en proceso',
            estado=True,
        )

        # Mermas
        self.stdout.write('📊 Creando mermas de prueba...')
        mermas_data = [
            ('Desperdicio de tela en corte',     'operativa', 'alta',  etapas[0]),
            ('Piezas defectuosas por costura',   'anormal',   'alta',  etapas[1]),
            ('Manchas en proceso de acabado',    'anormal',   'media', etapas[2]),
            ('Rechazo en control de calidad',    'operativa', 'media', etapas[3]),
            ('Sobrante de hilos y materiales',   'operativa', 'baja',  etapas[1]),
        ]
        for problema, tipo, prioridad, etapa in mermas_data:
            Merma.objects.create(
                empresa=empresa,
                etapa=etapa,
                problema_detectado=problema,
                tipo=tipo,
                porcentaje=round(random.uniform(5.0, 40.0), 2),
                impacto_economico=round(random.uniform(50000, 500000), 2),
                prioridad=prioridad,
            )

        self.stdout.write(self.style.SUCCESS('✅ Semilla completada exitosamente.'))
        self.stdout.write('   Usuario admin   → admin / admin123')
        self.stdout.write('   Usuario empresa → empresa1 / emp123')