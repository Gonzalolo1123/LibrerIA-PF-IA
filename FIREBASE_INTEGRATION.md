# 🔥 Integración de Firebase con Django - LibreriaIA

## 📋 Resumen

Esta guía te ayudará a integrar Firebase en tu proyecto Django existente. La integración permite mantener tu base de datos Django actual mientras sincronizas datos con Firebase para funcionalidades adicionales como analytics, tiempo real y escalabilidad.

## 🎯 ¿Por qué Firebase + Django?

### Ventajas de esta combinación:
- **Mantienes tu lógica de negocio existente** en Django
- **Escalabilidad** con Firebase Firestore
- **Analytics en tiempo real** con Firebase Analytics
- **Autenticación robusta** con Firebase Auth
- **Almacenamiento de archivos** con Firebase Storage
- **Notificaciones push** con Firebase Cloud Messaging

### Casos de uso específicos para LibreriaIA:
- Sincronización de productos en tiempo real
- Analytics de comportamiento de usuarios
- Almacenamiento de imágenes de productos
- Notificaciones de stock bajo
- Backup y redundancia de datos

## 🚀 Configuración Inicial

### 1. Crear proyecto en Firebase

1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Crea un nuevo proyecto o usa uno existente
3. Habilita los servicios que necesites:
   - **Firestore Database** (para datos)
   - **Authentication** (para usuarios)
   - **Storage** (para archivos)
   - **Analytics** (para métricas)

### 2. Obtener credenciales

1. En Firebase Console, ve a **Project Settings** > **Service Accounts**
2. Haz clic en **Generate New Private Key**
3. Descarga el archivo JSON con las credenciales

### 3. Configurar variables de entorno

Copia el archivo `firebase_env_example.txt` a `.env` y configura las variables:

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp firebase_env_example.txt .env
# Edita .env con tus credenciales reales
```

## 🔧 Uso de la Integración

### Sincronización de datos

```bash
# Sincronizar todos los productos
python manage.py sync_firebase --products

# Sincronizar todas las listas de compras
python manage.py sync_firebase --shopping-lists

# Sincronizar todo
python manage.py sync_firebase --all

# Ver datos desde Firebase (solo lectura)
python manage.py sync_firebase --from-firebase --all
```

### Uso en código Django

```python
from asistente_compras.firebase_service import FirebaseService, FirebaseAnalytics

# Sincronizar un producto específico
product = Product.objects.get(id=1)
FirebaseService.sync_product_to_firebase(product)

# Registrar analytics
FirebaseAnalytics.log_product_view(product_id=1, user_id=user.id)
FirebaseAnalytics.log_shopping_list_creation(user_id=user.id, list_id=list.id)
```

## 📊 Estructura de Datos en Firebase

### Colección: `products`
```json
{
  "id": 1,
  "name": "Cuaderno Espiral",
  "description": "Cuaderno de 100 hojas...",
  "price": 15.99,
  "brand": "Norma",
  "quality_category": "intermedio",
  "image_url": "https://...",
  "stock": 50,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "django_model": "Product"
}
```

### Colección: `shopping_lists`
```json
{
  "id": 1,
  "user_id": 1,
  "name": "Lista Escolar 2024",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "total_items": 5,
  "total_estimated_cost": 125.50,
  "items": [
    {
      "id": 1,
      "item_name_raw": "Cuaderno",
      "quantity_requested": 2,
      "suggested_product_id": 1,
      "ai_suggestions_json": {...}
    }
  ],
  "django_model": "ShoppingList"
}
```

### Colección: `user_analytics`
```json
{
  "user_id": 1,
  "action": "product_view",
  "data": {"product_id": 1},
  "timestamp": "2024-01-01T00:00:00Z",
  "source": "django_backend"
}
```

## 🔄 Estrategias de Sincronización

### 1. Sincronización Manual
- Usa el comando `sync_firebase` cuando necesites
- Ideal para migraciones iniciales

### 2. Sincronización Automática (Recomendado)
Agrega esto a tus modelos Django:

```python
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .firebase_service import FirebaseService

@receiver(post_save, sender=Product)
def sync_product_to_firebase(sender, instance, created, **kwargs):
    FirebaseService.sync_product_to_firebase(instance)

@receiver(post_save, sender=ShoppingList)
def sync_shopping_list_to_firebase(sender, instance, created, **kwargs):
    FirebaseService.sync_shopping_list_to_firebase(instance)
```

### 3. Sincronización Programada
Usa Celery para sincronización periódica:

```python
from celery import shared_task

@shared_task
def sync_all_data_to_firebase():
    FirebaseService.sync_all_products()
    FirebaseService.sync_all_shopping_lists()
```

## 🛡️ Seguridad

### Reglas de Firestore
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Solo lectura para productos
    match /products/{productId} {
      allow read: if true;
      allow write: if request.auth != null && request.auth.token.admin == true;
    }
    
    // Usuarios solo pueden ver sus propias listas
    match /shopping_lists/{listId} {
      allow read, write: if request.auth != null && 
        resource.data.user_id == request.auth.uid;
    }
    
    // Analytics solo escritura desde backend
    match /user_analytics/{docId} {
      allow write: if request.auth != null;
      allow read: if false;
    }
  }
}
```

## 📈 Analytics y Métricas

### Métricas disponibles:
- **Vistas de productos**: Qué productos se ven más
- **Creación de listas**: Cuántas listas se crean
- **Uso de sugerencias IA**: Qué sugerencias se aceptan
- **Patrones de compra**: Análisis de comportamiento

### Dashboard de Firebase:
1. Ve a **Analytics** en Firebase Console
2. Configura eventos personalizados
3. Visualiza métricas en tiempo real

## 🚀 Próximos Pasos

### Funcionalidades a implementar:
1. **Autenticación con Firebase Auth**
2. **Notificaciones push** para stock bajo
3. **Almacenamiento de imágenes** en Firebase Storage
4. **Tiempo real** para actualizaciones de productos
5. **Backup automático** de datos críticos

### Optimizaciones:
1. **Caché** con Redis para consultas frecuentes
2. **Sincronización incremental** para mejor rendimiento
3. **Compresión** de datos para reducir costos
4. **Monitoreo** de uso y costos de Firebase

## 🔧 Troubleshooting

### Problemas comunes:

**Error de credenciales:**
```bash
# Verifica que las variables de entorno estén correctas
python manage.py shell
>>> import os
>>> print(os.getenv('FIREBASE_PROJECT_ID'))
```

**Error de permisos:**
```bash
# Verifica las reglas de Firestore
# Asegúrate de que el service account tenga permisos
```

**Sincronización lenta:**
```bash
# Usa sincronización por lotes
# Implementa caché local
# Considera usar Cloud Functions
```

## 📞 Soporte

Para problemas específicos:
1. Revisa los logs de Django
2. Verifica la consola de Firebase
3. Consulta la documentación oficial de Firebase
4. Revisa las reglas de Firestore

---

**¡Firebase + Django = Potencia y Escalabilidad! 🚀** 