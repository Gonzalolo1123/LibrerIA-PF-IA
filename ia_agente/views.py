from django.views import View
from django.shortcuts import render, redirect
from .ai_agent import ai_agent

# Create your views here.

class IAQueryView(View):
    template_name = 'ia_agente/consulta_ia.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        consulta = request.POST.get('consulta')
        productos = []
        error = None
        if consulta:
            resultado = ai_agent.process_query(consulta)
            productos = resultado.get('productos', [])
            error = resultado.get('error')
            print(f"[DEPURACIÓN] Productos IA: {productos}")
            print(f"[DEPURACIÓN] Error IA: {error}")
            if productos and not error:
                try:
                    from asistente_compras.models import ShoppingList, ShoppingListItem
                    from django.utils import timezone
                    user = request.user if request.user.is_authenticated else None
                    nombre_lista = f'Sugerencia IA {timezone.now().strftime("%d/%m/%Y %H:%M")}'
                    shopping_list = ShoppingList.objects.create(
                        user=user,
                        name=nombre_lista,
                        quality_preference='cualquiera'
                    )
                    print(f"[DEPURACIÓN] Lista creada: {shopping_list}")
                    for p in productos:
                        item = ShoppingListItem.objects.create(
                            shopping_list=shopping_list,
                            item_name_raw=p.get('producto', ''),
                            quantity_requested=p.get('cantidad_sugerida', 1)
                        )
                        # Asignar ai_suggestions_json vacío para compatibilidad con el template
                        item.ai_suggestions_json = '{}'
                        item.save()
                        # Si el producto existe en catálogo, asignar como sugerido
                        from asistente_compras.models import Product
                        prod = Product.objects.filter(name__icontains=p.get('producto', '')).first()
                        if prod:
                            item.suggested_product = prod
                            item.save()
                            print(f"[DEPURACIÓN] Producto sugerido asignado: {prod}")
                    print(f"[DEPURACIÓN] Redirigiendo a list_detail con id {shopping_list.id}")
                    return redirect('asistente_compras:list_detail', list_id=shopping_list.id)
                except Exception as e:
                    print(f"[DEPURACIÓN][ERROR] Fallo al crear lista o redirigir: {e}")
        return render(request, self.template_name, {
            'consulta': consulta,
            'productos': productos,
            'error': error
        })
