from django.core.management.base import BaseCommand
from asistente_compras.firebase_service import FirebaseService, FirebaseAnalytics


class Command(BaseCommand):
    help = 'Sincroniza datos entre Django y Firebase'

    def add_arguments(self, parser):
        parser.add_argument(
            '--products',
            action='store_true',
            help='Sincronizar productos',
        )
        parser.add_argument(
            '--shopping-lists',
            action='store_true',
            help='Sincronizar listas de compras',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Sincronizar todos los datos',
        )
        parser.add_argument(
            '--from-firebase',
            action='store_true',
            help='Obtener datos desde Firebase (solo lectura)',
        )

    def handle(self, *args, **options):
        if options['from_firebase']:
            self.stdout.write('Obteniendo datos desde Firebase...')
            
            if options['products'] or options['all']:
                products = FirebaseService.get_products_from_firebase()
                self.stdout.write(f'Productos obtenidos de Firebase: {len(products)}')
                for product in products[:5]:  # Mostrar solo los primeros 5
                    self.stdout.write(f'  - {product.get("name", "Sin nombre")}')
            
            if options['shopping_lists'] or options['all']:
                lists = FirebaseService.get_shopping_lists_from_firebase()
                self.stdout.write(f'Listas de compras obtenidas de Firebase: {len(lists)}')
                for list_data in lists[:5]:  # Mostrar solo las primeras 5
                    self.stdout.write(f'  - {list_data.get("name", "Sin nombre")}')
            
            return

        # Sincronización hacia Firebase
        if options['products'] or options['all']:
            self.stdout.write('Sincronizando productos...')
            success, total = FirebaseService.sync_all_products()
            self.stdout.write(
                self.style.SUCCESS(f'Productos sincronizados: {success}/{total}')
            )

        if options['shopping_lists'] or options['all']:
            self.stdout.write('Sincronizando listas de compras...')
            success, total = FirebaseService.sync_all_shopping_lists()
            self.stdout.write(
                self.style.SUCCESS(f'Listas sincronizadas: {success}/{total}')
            )

        if not any([options['products'], options['shopping_lists'], options['all']]):
            self.stdout.write(
                self.style.WARNING(
                    'Debes especificar qué sincronizar. Usa --help para ver las opciones.'
                )
            ) 