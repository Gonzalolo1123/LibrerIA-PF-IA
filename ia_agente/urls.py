from django.urls import path
from .views import IAQueryView

urlpatterns = [
    path('consulta/', IAQueryView.as_view(), name='consulta_ia'),
] 