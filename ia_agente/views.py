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
        if consulta:
            # Usar el agente IA real
            respuesta = ai_agent.process_query(consulta)
        else:
            respuesta = "Por favor, ingresa una consulta."
        
        return render(request, self.template_name, {
            'consulta': consulta, 
            'respuesta': respuesta
        })
