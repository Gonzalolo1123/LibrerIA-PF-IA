from django.core.management.base import BaseCommand
from ia_agente.embeddings_manager import embeddings_manager

class Command(BaseCommand):
    help = 'Genera embeddings para todos los productos del catálogo'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Iniciando generación de embeddings...')
        )
        
        try:
            # Crear el índice vectorial
            embeddings_manager.create_vector_store()
            
            self.stdout.write(
                self.style.SUCCESS('¡Embeddings generados exitosamente!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error generando embeddings: {e}')
            ) 