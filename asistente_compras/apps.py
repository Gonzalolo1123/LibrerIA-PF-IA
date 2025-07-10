from django.apps import AppConfig


class AsistenteComprasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'asistente_compras'
    
    def ready(self):
        """Registra las señales cuando la aplicación está lista"""
        import asistente_compras.signals