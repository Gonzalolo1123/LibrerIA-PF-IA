from django.urls import path
from . import views
 
urlpatterns = [
    path('consulta/', views.IAQueryView.as_view(), name='consulta_ia'),
    path('generar_respuesta/', views.generar_respuesta, name='generar_respuesta'),
    path('enviar_respuesta/', views.enviar_respuesta, name='enviar_respuesta'),
] 