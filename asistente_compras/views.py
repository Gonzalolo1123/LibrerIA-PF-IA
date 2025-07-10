from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import Product, ShoppingList, ShoppingListItem
import json
import re
from decimal import Decimal
from .standard_lists import get_standard_list, get_all_standard_lists
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime


def home_view(request):
    """
    Vista principal que muestra la página de inicio con opciones para crear listas
    y ver las listas existentes del usuario.
    """
    context = {
        'title': 'Bienvenido al Asistente de Compras de Librería con IA',
        'user_lists': []
    }
    
    # Si el usuario está autenticado, mostrar sus listas
    if request.user.is_authenticated:
        context['user_lists'] = ShoppingList.objects.filter(user=request.user)[:5]
    
    return render(request, 'asistente_compras/home.html', context)


def create_shopping_list(request):
    """
    Vista para crear una nueva lista de compras.
    Procesa el formulario y simula la lógica de IA para sugerir productos.
    Permite a usuarios autenticados y no autenticados crear listas.
    """
    if request.method == 'POST':
        list_name = request.POST.get('list_name', '').strip()
        items_text = request.POST.get('items_text', '').strip()
        quality_preference = request.POST.get('quality_preference', 'cualquiera')
        
        if not list_name or not items_text:
            messages.error(request, 'Por favor, completa todos los campos requeridos.')
            return render(request, 'asistente_compras/notes.html', {
                'title': 'Crear Nueva Lista de Compras',
                'list_name': list_name,
                'items_text': items_text,
                'quality_preference': quality_preference
            })
        
        # Asignar el usuario si está autenticado, de lo contrario será nulo
        user = request.user if request.user.is_authenticated else None
        
        # Crear la lista de compras
        shopping_list = ShoppingList.objects.create(
            user=user,
            name=list_name,
            quality_preference=quality_preference
        )
        
        # Procesar los ítems del texto ingresado
        items = _parse_items_from_text(items_text)
        
        # Para cada ítem, crear un ShoppingListItem y simular sugerencias de IA
        for item_name, quantity in items:
            shopping_item = ShoppingListItem(
                shopping_list=shopping_list,
                item_name_raw=item_name,
                quantity_requested=quantity
            )
            
            # Simular sugerencias de IA con filtro de calidad
            ai_suggestions = _simulate_ai_suggestions(item_name, quantity, quality_preference)
            shopping_item.set_ai_suggestions(ai_suggestions)
            
            # Si hay una sugerencia principal, asignarla
            if ai_suggestions.get('primary_suggestion'):
                primary_product = _get_or_create_product(ai_suggestions['primary_suggestion'])
                shopping_item.suggested_product = primary_product
            
            # Guardar el item una sola vez después de asignar todo
            shopping_item.save()
        
        messages.success(request, f'Lista "{list_name}" creada exitosamente con {len(items)} ítems.')
        return redirect('asistente_compras:list_detail', list_id=shopping_list.id)
    
    return render(request, 'asistente_compras/notes.html', {
        'title': 'Crear Nueva Lista de Compras'
    })


def create_standard_list(request, list_type):
    """
    Vista para crear una lista de compras basada en una lista estándar predefinida.
    """
    # Obtener la lista estándar
    standard_list = get_standard_list(list_type)
    if not standard_list:
        messages.error(request, 'Tipo de lista estándar no válido.')
        return redirect('asistente_compras:create_shopping_list')
    
    # Obtener la preferencia de calidad de los parámetros GET
    quality_preference = request.GET.get('quality_preference', 'cualquiera')
    
    # Asignar el usuario si está autenticado, de lo contrario será nulo
    user = request.user if request.user.is_authenticated else None
    
    # Crear la lista de compras
    shopping_list = ShoppingList.objects.create(
        user=user,
        name=standard_list['name'],
        quality_preference=quality_preference
    )
    
    # Agregar los ítems de la lista estándar
    for item_name, quantity in standard_list['items']:
        shopping_item = ShoppingListItem(
            shopping_list=shopping_list,
            item_name_raw=item_name,
            quantity_requested=quantity
        )
        
        # Simular sugerencias de IA con filtro de calidad
        ai_suggestions = _simulate_ai_suggestions(item_name, quantity, quality_preference)
        shopping_item.set_ai_suggestions(ai_suggestions)
        
        # Si hay una sugerencia principal, asignarla
        if ai_suggestions.get('primary_suggestion'):
            primary_product = _get_or_create_product(ai_suggestions['primary_suggestion'])
            shopping_item.suggested_product = primary_product
        
        shopping_item.save()
    
    messages.success(request, f'Lista "{standard_list["name"]}" creada exitosamente con {len(standard_list["items"])} ítems.')
    return redirect('asistente_compras:list_detail', list_id=shopping_list.id)


def list_detail(request, list_id):
    """
    Vista para mostrar los detalles de una lista de compras específica.
    Muestra los ítems con sus sugerencias de IA.
    Permite a usuarios autenticados y no autenticados ver la lista.
    """
    # Si el usuario es anónimo, intentar obtener la lista sin filtrar por usuario
    # Si el usuario está autenticado, obtener la lista que le pertenece
    if request.user.is_authenticated:
        shopping_list = get_object_or_404(ShoppingList, id=list_id, user=request.user)
    else:
        shopping_list = get_object_or_404(ShoppingList, id=list_id)
        # Opcional: Si quieres que solo las listas creadas por invitados sean accesibles sin login,
        # podrías añadir: and shopping_list.user is None

    items = shopping_list.shoppinglistitem_set.all()
    
    context = {
        'title': f'Detalles de la Lista: {shopping_list.name}',
        'shopping_list': shopping_list,
        'items': items,
        'total_estimated_cost': shopping_list.get_total_estimated_cost(),
        'total_items': shopping_list.get_total_items()
    }
    
    return render(request, 'asistente_compras/list_detail.html', context)


def select_suggestion_for_item(request, list_id, item_id):
    """
    Vista para que el usuario seleccione una sugerencia de producto de la IA
    para un ítem específico de la lista de compras.
    """
    if request.method == 'POST':
        # Obtener la lista de compras, respetando la autenticación del usuario
        if request.user.is_authenticated:
            shopping_list = get_object_or_404(ShoppingList, id=list_id, user=request.user)
        else:
            # Para usuarios anónimos, verificar que la lista exista y no pertenezca a un usuario autenticado
            shopping_list = get_object_or_404(ShoppingList, id=list_id)
            if shopping_list.user is not None:
                messages.error(request, "No tienes permiso para modificar esta lista.")
                return redirect('asistente_compras:list_detail', list_id=list_id)

        # Obtener el ítem de la lista de compras
        shopping_item = get_object_or_404(ShoppingListItem, id=item_id, shopping_list=shopping_list)

        # Obtener el índice de la sugerencia seleccionada de los datos POST
        selected_index = request.POST.get('suggestion_index')
        
        if not selected_index:
            messages.error(request, "No se seleccionó ninguna sugerencia.")
            return redirect('asistente_compras:list_detail', list_id=list_id)

        try:
            selected_index = int(selected_index)
            ai_suggestions = shopping_item.get_ai_suggestions() # Ya retorna un diccionario
            
            if 'suggestions' not in ai_suggestions or not ai_suggestions['suggestions']:
                messages.error(request, "No hay sugerencias de IA disponibles para este ítem.")
                return redirect('asistente_compras:list_detail', list_id=list_id)

            if 0 <= selected_index < len(ai_suggestions['suggestions']):
                selected_suggestion_data = ai_suggestions['suggestions'][selected_index]
                
                # Obtener o crear el Producto basándose en la sugerencia
                primary_product = _get_or_create_product(selected_suggestion_data)
                
                shopping_item.suggested_product = primary_product
                shopping_item.save()
                messages.success(request, f"Producto sugerido para \'{shopping_item.item_name_raw}\' actualizado correctamente.")
            else:
                messages.error(request, "Índice de sugerencia no válido.")
        except ValueError:
            messages.error(request, "Índice de sugerencia no válido.")
        except Exception as e:
            messages.error(request, f"Error al procesar la sugerencia: {e}")

    return redirect('asistente_compras:list_detail', list_id=list_id)


def _parse_items_from_text(text):
    """
    Función auxiliar para parsear el texto de ítems y extraer nombres y cantidades.
    Simula el procesamiento que haría la IA para entender la entrada del usuario.
    """
    items = []
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Patrón para extraer cantidad y nombre del ítem
        # Ejemplos: "3 cuadernos", "2 lápices", "1 mochila", etc.
        quantity_match = re.match(r'^(\d+)\s+(.+)$', line)
        if quantity_match:
            quantity = int(quantity_match.group(1))
            item_name = quantity_match.group(2).strip()
        else:
            # Si no hay cantidad especificada, asumir 1
            quantity = 1
            item_name = line
        
        items.append((item_name, quantity))
    
    return items


def _simulate_ai_suggestions(item_name, quantity, quality_preference='cualquiera'):
    """
    Simula las sugerencias de IA para un ítem específico.
    Ahora incluye filtro de calidad según la preferencia del usuario.
    """
    item_lower = item_name.lower()
    suggestions = {
        'confidence_score': 0.85,
        'suggestions': []
    }
    
    # Función auxiliar para filtrar sugerencias por calidad
    def filter_by_quality(suggestions_list, quality_pref):
        if quality_pref == 'cualquiera':
            return suggestions_list
        elif quality_pref == 'economico':
            return [s for s in suggestions_list if s['quality'] == 'economico']
        elif quality_pref == 'intermedio':
            return [s for s in suggestions_list if s['quality'] == 'intermedio']
        elif quality_pref == 'calidad':
            return [s for s in suggestions_list if s['quality'] == 'calidad']
        return suggestions_list
    
    if 'cuaderno' in item_lower:
        all_suggestions = [
            {
                'product_name': 'Cuaderno A4 Básico 100 hojas',
                'brand': 'Genérica',
                'price': 800.00,
                'quality': 'economico',
                'stock': 50,
                'description': 'Cuaderno básico para uso escolar'
            },
            {
                'product_name': 'Cuaderno A4 Tapa Dura 200 hojas',
                'brand': 'Faber-Castell',
                'price': 1200.00,
                'quality': 'intermedio',
                'stock': 30,
                'description': 'Cuaderno de calidad intermedia con tapa dura'
            },
            {
                'product_name': 'Cuaderno A4 Premium 300 hojas',
                'brand': 'Oxford',
                'price': 2500.00,
                'quality': 'calidad',
                'stock': 15,
                'description': 'Cuaderno premium con papel de alta calidad'
            }
        ]
        suggestions['suggestions'] = filter_by_quality(all_suggestions, quality_preference)
        
    elif 'lápiz' in item_lower or 'lapiz' in item_lower:
        all_suggestions = [
            {
                'product_name': 'Lápiz HB N°2 Caja x12',
                'brand': 'Faber-Castell',
                'price': 350.00,
                'quality': 'economico',
                'stock': 100,
                'description': 'Lápices escolares básicos'
            },
            {
                'product_name': 'Lápiz HB Ecológico x10',
                'brand': 'Staedtler',
                'price': 800.00,
                'quality': 'intermedio',
                'stock': 60,
                'description': 'Lápices ecológicos de calidad media'
            },
            {
                'product_name': 'Lápiz HB Profesional x12',
                'brand': 'Mitsubishi',
                'price': 1500.00,
                'quality': 'calidad',
                'stock': 25,
                'description': 'Lápices profesionales de alta calidad'
            }
        ]
        suggestions['suggestions'] = filter_by_quality(all_suggestions, quality_preference)
        
    elif 'mochila' in item_lower:
        all_suggestions = [
            {
                'product_name': 'Mochila Escolar Básica',
                'brand': 'Genérica',
                'price': 2500.00,
                'quality': 'economico',
                'stock': 25,
                'description': 'Mochila escolar básica con múltiples compartimentos'
            },
            {
                'product_name': 'Mochila Escolar con Ruedas',
                'brand': 'Samsonite',
                'price': 8500.00,
                'quality': 'intermedio',
                'stock': 10,
                'description': 'Mochila de calidad media con sistema de ruedas'
            },
            {
                'product_name': 'Mochila Escolar Premium',
                'brand': 'Nike',
                'price': 15000.00,
                'quality': 'calidad',
                'stock': 8,
                'description': 'Mochila premium con tecnología avanzada'
            }
        ]
        suggestions['suggestions'] = filter_by_quality(all_suggestions, quality_preference)
        
    else:
        # Sugerencia genérica para ítems no reconocidos
        all_suggestions = [
            {
                'product_name': f'Producto: {item_name}',
                'brand': 'Genérica',
                'price': 500.00,
                'quality': 'economico',
                'stock': 20,
                'description': 'Producto sugerido por IA'
            },
            {
                'product_name': f'Producto: {item_name}',
                'brand': 'Marca Media',
                'price': 1200.00,
                'quality': 'intermedio',
                'stock': 15,
                'description': 'Producto de calidad media'
            },
            {
                'product_name': f'Producto: {item_name}',
                'brand': 'Marca Premium',
                'price': 2500.00,
                'quality': 'calidad',
                'stock': 10,
                'description': 'Producto de alta calidad'
            }
        ]
        suggestions['suggestions'] = filter_by_quality(all_suggestions, quality_preference)
        suggestions['confidence_score'] = 0.60
    
    # Si no hay sugerencias después del filtro, usar la primera disponible
    if not suggestions['suggestions']:
        suggestions['suggestions'] = [all_suggestions[0]] if 'all_suggestions' in locals() else [{
            'product_name': f'Producto: {item_name}',
            'brand': 'Genérica',
            'price': 500.00,
            'quality': 'economico',
            'stock': 20,
            'description': 'Producto sugerido por IA'
        }]
    
    suggestions['primary_suggestion'] = suggestions['suggestions'][0]
    
    return suggestions


def _get_or_create_product(product_data):
    """
    Función auxiliar para obtener o crear un producto basado en los datos de la IA.
    En una implementación real, esto se conectaría con el catálogo existente.
    """
    # Buscar si ya existe un producto similar
    existing_product = Product.objects.filter(
        name__icontains=product_data['product_name'][:50]
    ).first()
    
    if existing_product:
        return existing_product
    
    # Crear un nuevo producto
    return Product.objects.create(
        name=product_data['product_name'],
        description=product_data['description'],
        price=Decimal(str(product_data['price'])),
        brand=product_data['brand'],
        quality_category=product_data['quality'],
        stock=product_data['stock']
    )

@csrf_exempt # Solo para desarrollo, en producción usar token CSRF
def edit_shopping_list_item(request, list_id, item_id):
    """
    Vista para editar un ítem específico de la lista de compras.
    Recibe datos por POST y actualiza el item_name_raw y quantity_requested.
    """
    if request.method == 'POST':
        try:
            # Obtener el ítem de la lista de compras
            shopping_item = get_object_or_404(ShoppingListItem, id=item_id, shopping_list__id=list_id)
            
            # Obtener los datos del cuerpo de la solicitud JSON
            data = json.loads(request.body)
            new_item_name = data.get('item_name', '').strip()
            new_quantity = data.get('quantity', 0)
            
            if not new_item_name or not new_quantity:
                return JsonResponse({'success': False, 'message': 'Nombre del ítem y cantidad son requeridos.'}, status=400)
            
            # Actualizar el ítem
            shopping_item.item_name_raw = new_item_name
            shopping_item.quantity_requested = new_quantity
            shopping_item.save()
            
            messages.success(request, 'Ítem actualizado correctamente.')
            return JsonResponse({'success': True, 'message': 'Ítem actualizado correctamente.'})
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Solicitud JSON inválida.'}, status=400)
        except ShoppingListItem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Ítem de lista no encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error al actualizar el ítem: {e}'}, status=500)
            
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

@csrf_exempt
def delete_shopping_list_item(request, list_id, item_id):
    """
    Vista para eliminar un ítem específico de la lista de compras.
    """
    if request.method == 'POST':
        try:
            shopping_item = get_object_or_404(ShoppingListItem, id=item_id, shopping_list__id=list_id)
            item_name = shopping_item.item_name_raw # Guardar nombre para el mensaje
            shopping_item.delete()
            messages.success(request, f'Ítem "{item_name}" eliminado correctamente.')
            return JsonResponse({'success': True, 'message': 'Ítem eliminado correctamente.'})
        except ShoppingListItem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Ítem de lista no encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error al eliminar el ítem: {e}'}, status=500)
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

@csrf_exempt
def add_shopping_list_item(request, list_id):
    """
    Vista para agregar un nuevo ítem a una lista de compras existente.
    """
    if request.method == 'POST':
        try:
            shopping_list = get_object_or_404(ShoppingList, id=list_id)
            data = json.loads(request.body)
            item_name = data.get('item_name', '').strip()
            quantity = data.get('quantity', 0)
            
            if not item_name or not quantity:
                return JsonResponse({'success': False, 'message': 'Nombre del ítem y cantidad son requeridos.'}, status=400)
            
            shopping_item = ShoppingListItem(
                shopping_list=shopping_list,
                item_name_raw=item_name,
                quantity_requested=quantity
            )
            
            # Simular sugerencias de IA para el nuevo ítem
            ai_suggestions = _simulate_ai_suggestions(item_name, quantity)
            shopping_item.set_ai_suggestions(ai_suggestions)
            
            if ai_suggestions.get('primary_suggestion'):
                primary_product = _get_or_create_product(ai_suggestions['primary_suggestion'])
                shopping_item.suggested_product = primary_product
            
            # Guardar el item una sola vez después de asignar todo
            shopping_item.save()
                
            messages.success(request, f'Ítem "{item_name}" agregado exitosamente.')
            return JsonResponse({'success': True, 'message': 'Ítem agregado correctamente.'})
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Solicitud JSON inválida.'}, status=400)
        except ShoppingList.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Lista de compras no encontrada.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error al agregar el ítem: {e}'}, status=500)
            
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

# --- Vistas para CRUD de Productos ---

def product_list(request):
    """
    Muestra una lista de todos los productos en el inventario.
    """
    products = Product.objects.all().order_by('name')
    context = {
        'title': 'Inventario de Productos',
        'products': products
    }
    return render(request, 'asistente_compras/product_inventory.html', context)

@csrf_exempt
def product_create(request):
    """
    Crea un nuevo producto en el inventario.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name', '').strip()
            description = data.get('description', '').strip()
            price = Decimal(str(data.get('price', 0)))
            brand = data.get('brand', '').strip()
            quality_category = data.get('quality_category', '').strip()
            stock = int(data.get('stock', 0))
            
            if not all([name, description, price, brand, quality_category]):
                return JsonResponse({'success': False, 'message': 'Todos los campos son requeridos.'}, status=400)

            if price < 0 or stock < 0:
                 return JsonResponse({'success': False, 'message': 'Precio y stock no pueden ser negativos.'}, status=400)

            product = Product.objects.create(
                name=name,
                description=description,
                price=price,
                brand=brand,
                quality_category=quality_category,
                stock=stock
            )
            messages.success(request, f'Producto "{name}" creado exitosamente.')
            return JsonResponse({'success': True, 'message': 'Producto creado correctamente.', 'product_id': product.id})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Solicitud JSON inválida.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error al crear el producto: {e}'}, status=500)
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

@csrf_exempt
def product_update(request, product_id):
    """
    Actualiza un producto existente en el inventario.
    """
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, id=product_id)
            data = json.loads(request.body)
            
            product.name = data.get('name', product.name).strip()
            product.description = data.get('description', product.description).strip()
            product.price = Decimal(str(data.get('price', product.price)))
            product.brand = data.get('brand', product.brand).strip()
            product.quality_category = data.get('quality_category', product.quality_category).strip()
            product.stock = int(data.get('stock', product.stock))

            if product.price < 0 or product.stock < 0:
                 return JsonResponse({'success': False, 'message': 'Precio y stock no pueden ser negativos.'}, status=400)

            product.save()
            messages.success(request, f'Producto "{product.name}" actualizado exitosamente.')
            return JsonResponse({'success': True, 'message': 'Producto actualizado correctamente.'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Solicitud JSON inválida.'}, status=400)
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Producto no encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error al actualizar el producto: {e}'}, status=500)
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

@csrf_exempt
def product_delete(request, product_id):
    """
    Elimina un producto del inventario.
    """
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, id=product_id)
            product_name = product.name # Guardar nombre para el mensaje
            product.delete()
            messages.success(request, f'Producto "{product_name}" eliminado exitosamente.')
            return JsonResponse({'success': True, 'message': 'Producto eliminado correctamente.'})
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Producto no encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error al eliminar el producto: {e}'}, status=500)
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

@csrf_exempt
def search_products(request):
    """
    Vista para buscar productos en el inventario.
    Retorna productos que coincidan con el término de búsqueda.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            search_term = data.get('search_term', '').strip()
            
            if not search_term:
                return JsonResponse({'success': False, 'message': 'Término de búsqueda requerido.'}, status=400)
            
            # Buscar productos que coincidan con el término de búsqueda
            products = Product.objects.filter(
                name__icontains=search_term
            ).order_by('name')[:10]  # Limitar a 10 resultados
            
            # Convertir productos a formato JSON
            products_data = []
            for product in products:
                products_data.append({
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'price': float(product.price),
                    'brand': product.brand,
                    'quality_category': product.quality_category,
                    'stock': product.stock
                })
            
            return JsonResponse({
                'success': True, 
                'products': products_data,
                'count': len(products_data)
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Solicitud JSON inválida.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error al buscar productos: {e}'}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

def export_list_to_pdf(request, list_id):
    """
    Vista para exportar una lista de compras a PDF como comprobante de compra.
    """
    # Obtener la lista de compras
    if request.user.is_authenticated:
        shopping_list = get_object_or_404(ShoppingList, id=list_id, user=request.user)
    else:
        shopping_list = get_object_or_404(ShoppingList, id=list_id)
    
    # Crear el buffer para el PDF
    buffer = BytesIO()
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # Obtener estilos
    styles = getSampleStyleSheet()
    
    # Crear estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=20,
        alignment=TA_LEFT,
        textColor=colors.darkgreen
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=12,
        allowMarkup=1  # Aseguramos que el marcado HTML esté habilitado
    )

    bold_normal_style = ParagraphStyle(
        'CustomNormalBold',
        parent=normal_style, # Hereda propiedades de normal_style
        fontName='Helvetica-Bold' # Establece explícitamente la fuente negrita
    )
    
    # Título principal
    title = Paragraph("COMPROBANTE DE COMPRA", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Información de la lista
    list_info = [
        [Paragraph("Nombre de la Lista:", bold_normal_style), shopping_list.name],
        [Paragraph("Fecha de Creación:", bold_normal_style), shopping_list.created_at.strftime("%d/%m/%Y %H:%M")],
        [Paragraph("Total de Ítems:", bold_normal_style), str(shopping_list.get_total_items())],
        [Paragraph("Preferencia de Calidad:", bold_normal_style), shopping_list.get_quality_preference_display()],
    ]
    
    if shopping_list.user:
        list_info.append([Paragraph("Cliente:", bold_normal_style), shopping_list.user.get_full_name() or shopping_list.user.username])
    
    list_table = Table(list_info, colWidths=[2*inch, 4*inch])
    list_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    story.append(list_table)
    story.append(Spacer(1, 20))
    
    # Título de la tabla de productos
    subtitle = Paragraph("DETALLE DE PRODUCTOS", subtitle_style)
    story.append(subtitle)
    
    # Obtener los ítems de la lista
    items = shopping_list.shoppinglistitem_set.all()
    
    if items:
        # Encabezados de la tabla
        headers = [
            "N°", "Producto", "Marca", "Calidad", "Cantidad", "Precio Unit.", "Subtotal"
        ]
        
        # Datos de la tabla
        table_data = [headers]
        total_general = 0
        
        for i, item in enumerate(items, 1):
            if item.suggested_product:
                product = item.suggested_product
                subtotal = float(product.price) * item.quantity_requested
                total_general += subtotal
                
                row = [
                    str(i),
                    product.name,
                    product.brand,
                    product.get_quality_category_display(),
                    str(item.quantity_requested),
                    f"${int(product.price):,}",
                    f"${int(subtotal):,}"
                ]
            else:
                row = [
                    str(i),
                    item.item_name_raw,
                    "N/A",
                    "N/A",
                    str(item.quantity_requested),
                    "N/A",
                    "N/A"
                ]
            
            table_data.append(row)
        
        # Agregar fila de total
        table_data.append([
            "", "", "", "", Paragraph("TOTAL:", bold_normal_style), "", Paragraph(f"${int(total_general):,}", bold_normal_style)
        ])
        
        # Crear la tabla
        table = Table(table_data, colWidths=[0.5*inch, 2*inch, 1*inch, 1*inch, 0.8*inch, 1*inch, 1*inch])
        
        # Estilo de la tabla
        table.setStyle(TableStyle([
            # Encabezados
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            
            # Datos
            ('ALIGN', (0, 1), (-1, -2), 'LEFT'),
            ('ALIGN', (4, 1), (6, -2), 'CENTER'),  # Cantidad, precio y subtotal centrados
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 9),
            
            # Fila de total
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTSIZE', (0, -1), (-1, -1), 10),
            ('ALIGN', (0, -1), (-1, -1), 'CENTER'),
            
            # Bordes
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (1, 1), (-1, -2), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Información adicional
        if total_general > 0:
            info_text = f"""
            <br/><b>Resumen de la Compra:</b><br/>
            • Total de productos: {len(items)}<br/>
            • Monto total: ${int(total_general):,}<br/>
            • Fecha de emisión: {datetime.now().strftime("%d/%m/%Y %H:%M")}<br/>
            • Este documento sirve como comprobante de compra para la lista "{shopping_list.name}"
            """
        else:
            info_text = f"""
            <br/><b>Nota:</b><br/>
            • Esta lista contiene {len(items)} productos<br/>
            • Los precios se calcularán cuando se seleccionen productos específicos<br/>
            • Fecha de emisión: {datetime.now().strftime("%d/%m/%Y %H:%M")}
            """
        
        # Ensure that normal_style can handle markup.
        normal_style.allowBreakups = 1
        normal_style.wordWrap = 'CJK'

        info_paragraph = Paragraph(info_text, normal_style)
        story.append(info_paragraph)
        
    else:
        # Lista vacía
        empty_text = Paragraph("Esta lista no contiene productos.", normal_style)
        story.append(empty_text)
    
    # Pie de página
    story.append(Spacer(1, 30))
    footer_text = """
    <b>Librería IA - Asistente de Compras</b><br/>
    Documento generado automáticamente por el sistema de IA<br/>
    Para consultas, contactar al administrador del sistema
    """
    footer = Paragraph(footer_text, normal_style)
    story.append(footer)
    
    # Construir el PDF
    doc.build(story)
    
    # Obtener el valor del buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Crear la respuesta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="comprobante_{shopping_list.name}_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf"'
    response.write(pdf)
    
    return response
