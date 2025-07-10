from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from .models import Product, ShoppingList, ShoppingListItem
from firebase_config import firebase
import json
from datetime import datetime


class FirebaseService:
    """Servicio para sincronizar datos entre Django y Firebase"""
    
    @staticmethod
    def sync_product_to_firebase(product):
        """Sincroniza un producto de Django a Firebase"""
        try:
            product_data = {
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': float(product.price),
                'brand': product.brand,
                'quality_category': product.quality_category,
                'image_url': product.image_url,
                'stock': product.stock,
                'created_at': product.created_at.isoformat(),
                'updated_at': product.updated_at.isoformat(),
                'django_model': 'Product'
            }
            
            # Guardar en Firebase
            firebase.add_document('products', product_data, str(product.id))
            return True
        except Exception as e:
            print(f"Error sincronizando producto a Firebase: {e}")
            return False
    
    @staticmethod
    def sync_shopping_list_to_firebase(shopping_list):
        """
        Sincroniza una lista de compras de Django a Firebase.
        Incluye los ítems anidados.
        """
        try:
            # Obtener items de la lista
            items = []
            for item in shopping_list.shoppinglistitem_set.all():
                item_data = {
                    'id': item.id,
                    'item_name_raw': item.item_name_raw,
                    'quantity_requested': item.quantity_requested,
                    'suggested_product_id': item.suggested_product.id if item.suggested_product else None,
                    'ai_suggestions_json': item.ai_suggestions_json,
                    'created_at': item.created_at.isoformat(),
                    'updated_at': item.updated_at.isoformat()
                }
                items.append(item_data)
            
            shopping_list_data = {
                'id': shopping_list.id,
                'user_id': shopping_list.user.id if shopping_list.user else None,
                'name': shopping_list.name,
                'created_at': shopping_list.created_at.isoformat(),
                'updated_at': shopping_list.updated_at.isoformat(),
                'total_items': shopping_list.get_total_items(),
                'total_estimated_cost': float(shopping_list.get_total_estimated_cost()),
                'items': items,
                'django_model': 'ShoppingList'
            }
            
            # Guardar en Firebase
            firebase.add_document('shopping_lists', shopping_list_data, str(shopping_list.id))
            return True
        except Exception as e:
            print(f"Error sincronizando lista de compras a Firebase: {e}")
            return False
    
    @staticmethod
    def get_products_from_firebase():
        """Obtiene productos desde Firebase"""
        try:
            products_ref = firebase.get_collection('products')
            products = products_ref.stream()
            return [doc.to_dict() for doc in products]
        except Exception as e:
            print(f"Error obteniendo productos de Firebase: {e}")
            return []
    
    @staticmethod
    def get_shopping_lists_from_firebase():
        """Obtiene listas de compras desde Firebase"""
        try:
            lists_ref = firebase.get_collection('shopping_lists')
            lists = lists_ref.stream()
            return [doc.to_dict() for doc in lists]
        except Exception as e:
            print(f"Error obteniendo listas de Firebase: {e}")
            return []
    
    @staticmethod
    def sync_all_products():
        """Sincroniza todos los productos de Django a Firebase"""
        products = Product.objects.all()
        success_count = 0
        for product in products:
            if FirebaseService.sync_product_to_firebase(product):
                success_count += 1
        return success_count, len(products)
    
    @staticmethod
    def sync_all_shopping_lists():
        """Sincroniza todas las listas de compras de Django a Firebase"""
        shopping_lists = ShoppingList.objects.all()
        success_count = 0
        for shopping_list in shopping_lists:
            if FirebaseService.sync_shopping_list_to_firebase(shopping_list):
                success_count += 1
        return success_count, len(shopping_lists)


class FirebaseAnalytics:
    """Servicio para analytics y métricas usando Firebase"""
    
    @staticmethod
    def log_user_action(user_id, action, data=None):
        """Registra una acción del usuario en Firebase"""
        try:
            log_data = {
                'user_id': user_id,
                'action': action,
                'data': data or {},
                'timestamp': datetime.now().isoformat(),
                'source': 'django_backend'
            }
            firebase.add_document('user_analytics', log_data)
            return True
        except Exception as e:
            print(f"Error registrando analytics: {e}")
            return False
    
    @staticmethod
    def log_product_view(product_id, user_id=None):
        """Registra una vista de producto"""
        return FirebaseAnalytics.log_user_action(
            user_id, 
            'product_view', 
            {'product_id': product_id}
        )
    
    @staticmethod
    def log_shopping_list_creation(user_id, list_id):
        """Registra la creación de una lista de compras"""
        return FirebaseAnalytics.log_user_action(
            user_id, 
            'shopping_list_created', 
            {'list_id': list_id}
        )
    
    @staticmethod
    def log_ai_suggestion_used(user_id, item_id, product_id):
        """Registra cuando un usuario usa una sugerencia de IA"""
        return FirebaseAnalytics.log_user_action(
            user_id, 
            'ai_suggestion_used', 
            {'item_id': item_id, 'product_id': product_id}
        ) 