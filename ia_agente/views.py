from django.views import View
from django.shortcuts import render
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
        return render(request, self.template_name, {
            'consulta': consulta,
            'productos': productos,
            'error': error
        })
