from django.urls import path
from . import views

app_name = 'asistente_compras'

urlpatterns = [
    # Vista principal - página de inicio
    path('', views.home_view, name='home'),
    
    # Crear nueva lista de compras
    path('crear-lista/', views.create_shopping_list, name='create_shopping_list'),
    
    # Crear lista estándar
    path('crear-lista-estandar/<str:list_type>/', views.create_standard_list, name='create_standard_list'),
    
    # Ver detalles de una lista específica
    path('lista/<int:list_id>/', views.list_detail, name='list_detail'),
    
    # Exportar lista a PDF
    path('lista/<int:list_id>/exportar-pdf/', views.export_list_to_pdf, name='export_list_to_pdf'),
    
    # URL para seleccionar un producto sugerido para un ítem de la lista
    path('lista/<int:list_id>/item/<int:item_id>/seleccionar-sugerencia/', 
         views.select_suggestion_for_item, name='select_suggestion_for_item'),
    
    # URL para editar un ítem específico de la lista
    path('lista/<int:list_id>/item/<int:item_id>/editar/', 
         views.edit_shopping_list_item, name='edit_shopping_list_item'),

    # URL para eliminar un ítem
    path('lista/<int:list_id>/item/<int:item_id>/eliminar/', 
         views.delete_shopping_list_item, name='delete_shopping_list_item'),

    # URL para agregar un nuevo ítem a una lista existente
    path('lista/<int:list_id>/agregar-item/', 
         views.add_shopping_list_item, name='add_shopping_list_item'),

    # URLs para CRUD de Productos
    path('productos/', views.product_list, name='product_list'),
    path('productos/crear/', views.product_create, name='product_create'),
    path('productos/<int:product_id>/actualizar/', views.product_update, name='product_update'),
    path('productos/<int:product_id>/eliminar/', views.product_delete, name='product_delete'),
    path('productos/buscar/', views.search_products, name='search_products'),
] 