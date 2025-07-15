from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
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
from ia_agente.ai_agent import ai_agent # Importar el agente de IA real
from ia_agente.utils import leer_correos_gmail, marcar_correo_eliminado


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
    Procesa el formulario y utiliza el agente de IA real para sugerir productos.
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
        
        # Para cada ítem, crear un ShoppingListItem y obtener sugerencias del agente de IA
        for item_name, quantity in items:
            shopping_item = ShoppingListItem(
                shopping_list=shopping_list,
                item_name_raw=item_name,
                quantity_requested=quantity
            )
            
            # Obtener sugerencias del agente de IA real
            # La query puede ser el item_name_raw, la cantidad, y la preferencia de calidad
            ai_response = ai_agent.process_query(f"{item_name} (cantidad: {quantity}, calidad: {quality_preference})")
            
            ai_suggestions_data = {"suggestions": [], "primary_suggestion": None}

            if not ai_response["error"]:
                suggestions_list = ai_response["productos"]
                # Aquí podrías aplicar el filtro de calidad si el agente IA no lo hace internamente
                # o si necesitas una lógica de filtrado adicional en el backend
                
                # Asignar la primera sugerencia como primaria si existe
                if suggestions_list:
                    ai_suggestions_data["primary_suggestion"] = suggestions_list[0]
                ai_suggestions_data["suggestions"] = suggestions_list

            shopping_item.set_ai_suggestions(ai_suggestions_data)
            
            # Si hay una sugerencia principal, asignarla
            if ai_suggestions_data.get('primary_suggestion'):
                primary_product = _get_or_create_product(ai_suggestions_data['primary_suggestion'])
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
        
        # Obtener sugerencias del agente de IA real
        ai_response = ai_agent.process_query(f"{item_name} (cantidad: {quantity}, calidad: {quality_preference})")
        
        ai_suggestions_data = {"suggestions": [], "primary_suggestion": None}

        if not ai_response["error"]:
            suggestions_list = ai_response["productos"]
            # Aquí podrías aplicar el filtro de calidad si el agente IA no lo hace internamente
            # o si necesitas una lógica de filtrado adicional en el backend
            
            if suggestions_list:
                ai_suggestions_data["primary_suggestion"] = suggestions_list[0]
            ai_suggestions_data["suggestions"] = suggestions_list

        shopping_item.set_ai_suggestions(ai_suggestions_data)
        
        # Si hay una sugerencia principal, asignarla
        if ai_suggestions_data.get('primary_suggestion'):
            primary_product = _get_or_create_product(ai_suggestions_data['primary_suggestion'])
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
                return JsonResponse({'status': 'error', 'message': 'No tienes permiso para modificar esta lista.'}, status=403)

        # Obtener el ítem de la lista de compras
        shopping_item = get_object_or_404(ShoppingListItem, id=item_id, shopping_list=shopping_list)

        # Obtener el índice de la sugerencia seleccionada de los datos POST
        selected_index = request.POST.get('suggestion_index')
        
        if not selected_index:
            return JsonResponse({'status': 'error', 'message': 'No se seleccionó ninguna sugerencia.'}, status=400)

        try:
            selected_index = int(selected_index)
            ai_suggestions = shopping_item.get_ai_suggestions() # Ya retorna un diccionario
            
            if 'suggestions' not in ai_suggestions or not ai_suggestions['suggestions']:
                return JsonResponse({'status': 'error', 'message': 'No hay sugerencias de IA disponibles para este ítem.'}, status=404)

            if 0 <= selected_index < len(ai_suggestions['suggestions']):
                selected_suggestion_data = ai_suggestions['suggestions'][selected_index]
                
                # Obtener o crear el Producto basándose en la sugerencia
                primary_product = _get_or_create_product(selected_suggestion_data)
                
                shopping_item.suggested_product = primary_product
                shopping_item.save()
                
                # Recalcular el costo total de la lista
                shopping_list.refresh_from_db()
                total_estimated_cost = shopping_list.get_total_estimated_cost()
                total_items = shopping_list.get_total_items()

                return JsonResponse({
                    'status': 'success',
                    'message': f"Producto sugerido para '{shopping_item.item_name_raw}' actualizado correctamente.",
                    'item_id': shopping_item.id,
                    'suggested_product_name': primary_product.name,
                    'suggested_product_brand': primary_product.brand,
                    'suggested_product_price': str(primary_product.price), # Convertir Decimal a string para JSON
                    'item_total_cost': str(shopping_item.get_estimated_cost()),
                    'list_total_cost': str(total_estimated_cost),
                    'total_items': total_items,
                    'quality': primary_product.quality_category
                })
            else:
                return JsonResponse({'status': 'error', 'message': 'Índice de sugerencia no válido.'}, status=400)
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Índice de sugerencia no válido.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error al procesar la sugerencia: {e}'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)


def _parse_items_from_text(text):
    """
    Función auxiliar para parsear el texto de ítems y extraer nombres y cantidades.
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


def _get_or_create_product(product_data):
    """
    Función auxiliar para obtener o crear un objeto Product a partir de los datos de la sugerencia de IA.
    """
    product_name = product_data.get('producto')
    brand = product_data.get('marca', 'Genérica')
    price = Decimal(str(product_data.get('precio', 0)))
    quality_category_value = product_data.get('calidad', 'Económico') # Corregido de 'quality' a 'quality_category_value'
    stock = product_data.get('stock', 0)

    product, created = Product.objects.get_or_create(
        name=product_name,
        brand=brand,
        defaults={'price': price, 'quality_category': quality_category_value, 'stock': stock} # Corregido a 'quality_category'
    )
    if not created:
        # Si el producto ya existe, actualizar sus atributos si es necesario
        updated = False
        if product.price != price:
            product.price = price
            updated = True
        if product.quality_category != quality_category_value: # Corregido a 'product.quality_category'
            product.quality_category = quality_category_value
            updated = True
        if product.stock != stock:
            product.stock = stock
            updated = True
        if updated:
            product.save()
    return product

def normalizar_sugerencias(sugerencias):
    normalizadas = []
    for s in sugerencias:
        normalizadas.append({
            "product_name": s.get("producto", ""),
            "brand": s.get("marca", ""),
            "price": s.get("precio", 0),
            "quality": s.get("calidad", ""),
            "stock": s.get("stock", 0),
            "description": s.get("descripcion", ""),
        })
    return normalizadas

@csrf_exempt # Solo para desarrollo, en producción usar token CSRF
def edit_shopping_list_item(request, list_id, item_id):
    """
    Edita un item de una lista de compras. Permite actualizar la cantidad y el producto sugerido.
    """
    if request.method == 'POST':
        if request.user.is_authenticated:
            shopping_list = get_object_or_404(ShoppingList, id=list_id, user=request.user)
        else:
            shopping_list = get_object_or_404(ShoppingList, id=list_id)
            if shopping_list.user is not None:
                return JsonResponse({'status': 'error', 'message': 'No tienes permiso para modificar esta lista.'}, status=403)

        shopping_item = get_object_or_404(ShoppingListItem, id=item_id, shopping_list=shopping_list)

        try:
            # Obtener los datos del cuerpo de la solicitud JSON
            data = json.loads(request.body)
            new_quantity = int(data.get('quantity_requested', shopping_item.quantity_requested))
            selected_product_id = data.get('suggested_product_id')

            shopping_item.quantity_requested = new_quantity

            # Actualizar el producto sugerido si se proporciona uno
            if selected_product_id:
                product = get_object_or_404(Product, id=selected_product_id)
                shopping_item.suggested_product = product
            else:
                shopping_item.suggested_product = None # Si no se selecciona, se limpia

            shopping_item.save()
            
            # Recalcular el costo total de la lista
            shopping_list.refresh_from_db() # Asegura que la lista esté actualizada con los cambios en los ítems
            total_estimated_cost = shopping_list.get_total_estimated_cost()

            return JsonResponse({
                'status': 'success',
                'message': 'Ítem de la lista actualizado correctamente.',
                'item_total_cost': shopping_item.get_total_cost_item(),
                'list_total_cost': total_estimated_cost,
                'total_items': shopping_list.get_total_items()
            })
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Formato de solicitud JSON inválido.'}, status=400)
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Cantidad inválida.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error al editar el ítem: {e}'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)


@csrf_exempt
def delete_shopping_list_item(request, list_id, item_id):
    """
    Elimina un item de una lista de compras.
    """
    if request.method == 'POST':
        if request.user.is_authenticated:
            shopping_list = get_object_or_404(ShoppingList, id=list_id, user=request.user)
        else:
            shopping_list = get_object_or_404(ShoppingList, id=list_id)
            if shopping_list.user is not None:
                return JsonResponse({'status': 'error', 'message': 'No tienes permiso para modificar esta lista.'}, status=403)
        
        shopping_item = get_object_or_404(ShoppingListItem, id=item_id, shopping_list=shopping_list)
        item_name = shopping_item.item_name_raw
        shopping_item.delete()

        # Recalcular el costo total de la lista y la cantidad de ítems
        shopping_list.refresh_from_db()
        total_estimated_cost = shopping_list.get_total_estimated_cost()
        total_items = shopping_list.get_total_items()
        
        messages.success(request, f'Ítem "{item_name}" eliminado correctamente de la lista.')
        return JsonResponse({
            'status': 'success', 
            'message': f'Ítem "{item_name}" eliminado correctamente.',
            'list_total_cost': total_estimated_cost,
            'total_items': total_items
        })
    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)


@csrf_exempt
def add_shopping_list_item(request, list_id):
    """
    Agrega un nuevo ítem a una lista de compras existente.
    """
    if request.method == 'POST':
        if request.user.is_authenticated:
            shopping_list = get_object_or_404(ShoppingList, id=list_id, user=request.user)
        else:
            shopping_list = get_object_or_404(ShoppingList, id=list_id)
            if shopping_list.user is not None:
                return JsonResponse({'status': 'error', 'message': 'No tienes permiso para modificar esta lista.'}, status=403)

        try:
            data = json.loads(request.body)
            item_name = data.get('item_name', '').strip()
            quantity = int(data.get('quantity', 1))

            if not item_name:
                return JsonResponse({'status': 'error', 'message': 'El nombre del ítem no puede estar vacío.'}, status=400)
            if quantity <= 0:
                return JsonResponse({'status': 'error', 'message': 'La cantidad debe ser un número positivo.'}, status=400)
            
            shopping_item = ShoppingListItem(
                shopping_list=shopping_list,
                item_name_raw=item_name,
                quantity_requested=quantity
            )

            # Obtener sugerencias del agente de IA real para el nuevo ítem
            ai_response = ai_agent.process_query(f"{item_name} (cantidad: {quantity}, calidad: {shopping_list.quality_preference})")
            
            ai_suggestions_data = {"suggestions": [], "primary_suggestion": None}

            if not ai_response["error"]:
                suggestions_list = ai_response["productos"]
                normalizadas = normalizar_sugerencias(suggestions_list)
                if normalizadas:
                    ai_suggestions_data["primary_suggestion"] = normalizadas[0]
                ai_suggestions_data["suggestions"] = normalizadas

            shopping_item.set_ai_suggestions(ai_suggestions_data)
            
            if ai_suggestions_data.get('primary_suggestion'):
                primary_product = _get_or_create_product(ai_suggestions_data['primary_suggestion'])
                shopping_item.suggested_product = primary_product
            
            shopping_item.save()

            # Recalcular el costo total de la lista
            shopping_list.refresh_from_db()
            total_estimated_cost = shopping_list.get_total_estimated_cost()
            total_items = shopping_list.get_total_items()

            return JsonResponse({
                'status': 'success',
                'message': 'Ítem agregado correctamente.',
                'item_html': render(request, 'asistente_compras/partials/shopping_list_item.html', {'item': shopping_item}).content.decode('utf-8'),
                'list_total_cost': total_estimated_cost,
                'total_items': total_items
            })
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Formato de solicitud JSON inválido.'}, status=400)
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Cantidad inválida.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error al agregar el ítem: {e}'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)


def product_list(request):
    """
    Vista para mostrar la lista de todos los productos en el inventario.
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
    Crea un nuevo producto.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name').strip()
            brand = data.get('brand', 'Genérica').strip()
            price = Decimal(data.get('price'))
            quality = data.get('quality', 'Económico').strip()
            stock = int(data.get('stock'))

            if not name or price is None or stock is None:
                return JsonResponse({'status': 'error', 'message': 'Nombre, precio y stock son campos requeridos.'}, status=400)
            if price <= 0:
                return JsonResponse({'status': 'error', 'message': 'El precio debe ser un número positivo.'}, status=400)
            if stock < 0:
                return JsonResponse({'status': 'error', 'message': 'El stock no puede ser negativo.'}, status=400)

            product = Product.objects.create(
                name=name,
                brand=brand,
                price=price,
                quality=quality,
                stock=stock
            )
            return JsonResponse({'status': 'success', 'message': 'Producto creado exitosamente.', 'product_id': product.id})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Formato JSON inválido.'}, status=400)
        except ValueError as e:
            return JsonResponse({'status': 'error', 'message': f'Error de validación: {e}'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error al crear producto: {e}'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)


@csrf_exempt
def product_update(request, product_id):
    """
    Actualiza un producto existente.
    """
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        try:
            data = json.loads(request.body)
            product.name = data.get('name', product.name).strip()
            product.brand = data.get('brand', product.brand).strip()
            product.price = Decimal(data.get('price', product.price))
            product.quality = data.get('quality', product.quality).strip()
            product.stock = int(data.get('stock', product.stock))

            if product.price <= 0:
                return JsonResponse({'status': 'error', 'message': 'El precio debe ser un número positivo.'}, status=400)
            if product.stock < 0:
                return JsonResponse({'status': 'error', 'message': 'El stock no puede ser negativo.'}, status=400)

            product.save()
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado exitosamente.'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Formato JSON inválido.'}, status=400)
        except ValueError as e:
            return JsonResponse({'status': 'error', 'message': f'Error de validación: {e}'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error al actualizar producto: {e}'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)

@csrf_exempt
def product_delete(request, product_id):
    """
    Elimina un producto.
    """
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        product_name = product.name
        product.delete()
        return JsonResponse({'status': 'success', 'message': f'Producto "{product_name}" eliminado exitosamente.'})
    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)


@csrf_exempt
def search_products(request):
    """
    Busca productos por nombre o marca.
    """
    query = request.GET.get('query', '').strip()
    if query:
        products = Product.objects.filter(name__icontains=query) | Product.objects.filter(brand__icontains=query)
        products = products.order_by('name')
    else:
        products = Product.objects.all().order_by('name')

    # Renderizar solo el fragmento de la tabla de productos
    context = {'products': products}
    return render(request, 'asistente_compras/partials/product_table_rows.html', context)


def export_list_to_pdf(request, list_id):
    """
    Exporta una lista de compras a un archivo PDF.
    """
    shopping_list = get_object_or_404(ShoppingList, id=list_id)

    # Crear un buffer para el PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=inch, leftMargin=inch,
                            topMargin=inch, bottomMargin=inch)

    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(name='CenteredTitle',
                              parent=styles['h1'],
                              alignment=TA_CENTER,
                              spaceAfter=14))
    styles.add(ParagraphStyle(name='LeftHeading',
                              parent=styles['h2'],
                              alignment=TA_LEFT,
                              spaceAfter=8))
    styles.add(ParagraphStyle(name='RightParagraph',
                              parent=styles['Normal'],
                              alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name='NormalLeft',
                              parent=styles['Normal'],
                              alignment=TA_LEFT))

    elements = []

    # Logo (asegúrate de que la ruta sea correcta y el archivo exista)
    # logo_path = os.path.join(settings.STATIC_ROOT, 'img', 'logo.png') # Usar STATIC_ROOT si está desplegado
    # Para desarrollo, podrías usar una ruta relativa si el staticfiles_dirs está configurado
    # o simplemente omitirlo si no es crítico.
    # Por simplicidad, si no hay un logo específico, se puede omitir esta parte.
    # if os.path.exists(logo_path):
    #     logo = Image(logo_path, width=1.5*inch, height=0.5*inch)
    #     elements.append(logo)
    #     elements.append(Spacer(1, 0.2*inch))


    # Título del documento
    elements.append(Paragraph("LISTA DE COMPRAS - LibrerIA", styles['CenteredTitle']))
    elements.append(Spacer(1, 0.2 * inch))

    # Información de la lista
    elements.append(Paragraph(f"<b>Nombre de la Lista:</b> {shopping_list.name}", styles['NormalLeft']))
    elements.append(Paragraph(f"<b>Creada:</b> {shopping_list.created_at.strftime('%d/%m/%Y %H:%M')}", styles['NormalLeft']))
    elements.append(Paragraph(f"<b>Última Actualización:</b> {shopping_list.updated_at.strftime('%d/%m/%Y %H:%M')}", styles['NormalLeft']))
    if shopping_list.user:
        elements.append(Paragraph(f"<b>Usuario:</b> {shopping_list.user.username}", styles['NormalLeft']))
    elements.append(Spacer(1, 0.2 * inch))

    # Tabla de ítems
    data = [["Cantidad", "Producto Solicitado", "Producto Sugerido", "Marca", "Precio Unitario", "Subtotal"]]
    total_cost = Decimal('0.00')

    for item in shopping_list.shoppinglistitem_set.all():
        product_name = "N/A"
        brand = "N/A"
        price = Decimal('0.00')
        subtotal = Decimal('0.00')

        if item.suggested_product:
            product_name = item.suggested_product.name
            brand = item.suggested_product.brand
            price = item.suggested_product.price
            subtotal = item.suggested_product.price * item.quantity_requested
        
        data.append([
            str(item.quantity_requested),
            item.item_name_raw,
            product_name,
            brand,
            f"${price:,.2f}",
            f"${subtotal:,.2f}"
        ])
        total_cost += subtotal
    
    # Fila total
    data.append(["", "", "", "", "<b>Costo Total Estimado:</b>", f"<b>${total_cost:,.2f}</b>"])

    table = Table(data, colWidths=[1*inch, 2*inch, 1.5*inch, 1*inch, 1*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ADD8E6')), # Azul claro para encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (4, -1), (5, -1), 'Helvetica-Bold'), # Total en negrita
        ('ALIGN', (4, -1), (5, -1), 'RIGHT'), # Total alineado a la derecha
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.5 * inch))

    elements.append(Paragraph("Gracias por usar LibrerIA para tus compras.", styles['CenteredTitle']))

    doc.build(elements)
    
    # Obtener el valor del buffer y crear la respuesta HTTP
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="lista_compras_{shopping_list.name.replace(" ", "_")}.pdf"'
    return response

def list_detail_ia(request):
    """
    Vista para mostrar los productos sugeridos por la IA como una lista temporal, usando el template de detalle de lista.
    """
    productos = request.session.get('productos_sugeridos', [])
    # Limpiar la sesión para evitar mostrar la misma lista en recargas
    if 'productos_sugeridos' in request.session:
        del request.session['productos_sugeridos']
    # Adaptar los datos para el template list_detail.html
    class TempList:
        name = 'Sugerencia Inteligente'
        created_at = updated_at = None
        def get_total_estimated_cost(self):
            return sum(p.get('precio', 0) * p.get('cantidad_sugerida', 1) for p in productos)
        def get_total_items(self):
            return sum(p.get('cantidad_sugerida', 1) for p in productos)
    class TempItem:
        def __init__(self, p):
            self.item_name_raw = p.get('producto', '')
            self.quantity_requested = p.get('cantidad_sugerida', 1)
            self.suggested_product = type('Prod', (), {
                'name': p.get('producto', ''),
                'brand': p.get('marca', ''),
                'quality_category': p.get('calidad', ''),
                'get_quality_category_display': lambda self: p.get('calidad', ''),
                'price': p.get('precio', 0),
                'stock': p.get('stock', 0)
            })()
            self.get_estimated_cost = lambda: p.get('precio', 0) * p.get('cantidad_sugerida', 1)
    items = [TempItem(p) for p in productos]
    context = {
        'title': 'Sugerencia Inteligente de Productos',
        'shopping_list': TempList(),
        'items': items,
        'total_estimated_cost': sum(p.get('precio', 0) * p.get('cantidad_sugerida', 1) for p in productos),
        'total_items': sum(p.get('cantidad_sugerida', 1) for p in productos)
    }
    return render(request, 'asistente_compras/list_detail.html', context)

def correos_recibidos(request):
    """
    Vista para mostrar todos los correos recibidos y permitir actualizar la lista.
    """
    if request.method == 'POST':
        # Petición AJAX para actualizar correos
        correos = leer_correos_gmail()
        return JsonResponse({'correos': correos})
    else:
        correos = leer_correos_gmail()
        return render(request, 'asistente_compras/correos_recibidos.html', {'correos': correos})

@csrf_exempt
def eliminar_correo(request):
    if request.method == 'POST':
        correo_id = request.POST.get('id')
        if correo_id:
            marcar_correo_eliminado(correo_id)
            return JsonResponse({'success': True})
        else:
            return HttpResponseBadRequest('Falta el id del correo')
    return HttpResponseBadRequest('Método no permitido')
