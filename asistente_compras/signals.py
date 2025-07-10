from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product, ShoppingList, ShoppingListItem
from .firebase_service import FirebaseService

@receiver(post_save, sender=Product)
def sync_product_to_firebase(sender, instance, created, **kwargs):
    """Sincroniza automáticamente productos con Firebase"""
    try:
        FirebaseService.sync_product_to_firebase(instance)
        if created:
            print(f"✅ Producto '{instance.name}' sincronizado con Firebase")
        else:
            print(f"✅ Producto '{instance.name}' actualizado en Firebase")
    except Exception as e:
        print(f"❌ Error sincronizando producto: {e}")

@receiver(post_save, sender=ShoppingList)
def sync_shopping_list_to_firebase(sender, instance, created, **kwargs):
    """Sincroniza automáticamente listas de compras con Firebase"""
    try:
        FirebaseService.sync_shopping_list_to_firebase(instance)
        if created:
            print(f"✅ Lista '{instance.name}' sincronizada con Firebase")
        else:
            print(f"✅ Lista '{instance.name}' actualizada en Firebase")
    except Exception as e:
        print(f"❌ Error sincronizando lista: {e}")

@receiver(post_save, sender=ShoppingListItem)
def sync_shopping_list_item_to_firebase(sender, instance, created, **kwargs):
    """Sincroniza automáticamente items de lista con Firebase"""
    try:
        # Sincronizar la lista completa cuando se modifica un item
        FirebaseService.sync_shopping_list_to_firebase(instance.shopping_list)
        if created:
            print(f"✅ Item '{instance.item_name_raw}' sincronizado con Firebase")
        else:
            print(f"✅ Item '{instance.item_name_raw}' actualizado en Firebase")
    except Exception as e:
        print(f"❌ Error sincronizando item: {e}")

@receiver(post_delete, sender=Product)
def delete_product_from_firebase(sender, instance, **kwargs):
    """Elimina productos de Firebase cuando se borran en Django"""
    try:
        from firebase_config import firebase
        firebase.delete_document('products', str(instance.id))
        print(f"✅ Producto '{instance.name}' eliminado de Firebase")
    except Exception as e:
        print(f"❌ Error eliminando producto de Firebase: {e}")

@receiver(post_delete, sender=ShoppingList)
def delete_shopping_list_from_firebase(sender, instance, **kwargs):
    """Elimina listas de compras de Firebase cuando se borran en Django"""
    try:
        from firebase_config import firebase
        firebase.delete_document('shopping_lists', str(instance.id))
        print(f"✅ Lista '{instance.name}' eliminada de Firebase")
    except Exception as e:
        print(f"❌ Error eliminando lista de Firebase: {e}") 