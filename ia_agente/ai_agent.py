import os
import json
import re
from typing import List, Dict, Any
from ia_agente.embeddings_manager import embeddings_manager
from llama_cpp import Llama
import unicodedata


def limpiar_cuerpo_correo(cuerpo: str, max_length: int = 1500) -> str:
    """
    Limpia el cuerpo del correo para optimizar el prompt a la IA:
    - Decodifica unicode y saltos de línea
    - Elimina saludos y firmas comunes
    - Elimina espacios y saltos de línea redundantes
    - Recorta si es muy largo
    """
    # Decodificar unicode y saltos de línea
    cuerpo = bytes(cuerpo, "utf-8").decode("unicode_escape")
    cuerpo = cuerpo.replace('\r', '\n').replace('\u000D', '\n').replace('\u000A', '\n')
    # Eliminar saludos y firmas comunes
    saludos = [r"^estimad[oa]s?,?", r"^buen[oa]s? d[ií]as,?", r"^hola,?", r"^saludos,?", r"^cordial saludo,?", r"^atentamente,?", r"^quedo atento", r"^gracias,?", r"^un saludo,?"]
    for saludo in saludos:
        cuerpo = re.sub(saludo, '', cuerpo, flags=re.IGNORECASE|re.MULTILINE)
    # Eliminar líneas de firma típicas
    cuerpo = re.sub(r"(?i)\n*--+.*", '', cuerpo)
    cuerpo = re.sub(r"(?i)\n*\*\[Nombre del remitente\]\*.*", '', cuerpo)
    cuerpo = re.sub(r"(?i)\n*correo:.*", '', cuerpo)
    cuerpo = re.sub(r"(?i)\n*tel[eé]fono:.*", '', cuerpo)
    # Unificar espacios y saltos de línea
    cuerpo = re.sub(r'\s+', ' ', cuerpo)
    cuerpo = cuerpo.strip()
    # Recortar si es muy largo
    if len(cuerpo) > max_length:
        cuerpo = cuerpo[:max_length] + "..."
    return cuerpo

def extraer_productos_de_correo(cuerpo: str) -> list:
    """
    Extrae líneas que parecen productos de una cotización (ej: '50 Cuadernos universitarios ...')
    """
    productos = []
    # Buscar líneas con patrón: cantidad + descripción
    for linea in cuerpo.split('\n'):
        match = re.match(r"\s*(\d+)\s+([A-Za-zÁÉÍÓÚáéíóúñÑ0-9\-\s,\.]+)", linea)
        if match:
            productos.append(linea.strip())
    return productos

def limpiar_y_optimizar_correo(cuerpo: str, max_length: int = 1200) -> str:
    """
    Limpia y optimiza el cuerpo del correo para el prompt de la IA:
    - Decodifica unicode y normaliza caracteres especiales
    - Elimina secuencias unicode (\u000D, \u000A, etc.) y caracteres de escape
    - Elimina saludos, firmas y metadatos
    - Extrae y preserva las líneas con productos
    - Elimina espacios y saltos de línea redundantes
    - Elimina líneas vacías
    - Recorta el texto si es muy largo
    """
    # Decodificar unicode y normalizar
    cuerpo = bytes(cuerpo, "utf-8").decode("unicode_escape", errors="ignore")
    cuerpo = unicodedata.normalize("NFKC", cuerpo)
    
    # Eliminar secuencias unicode y caracteres de escape
    cuerpo = re.sub(r"\\u[0-9A-Fa-f]{4}", " ", cuerpo)  # elimina \u000D, \u000A, etc.
    cuerpo = re.sub(r"\\[trn]", " ", cuerpo)  # elimina \t, \r, \n
    cuerpo = re.sub(r"\u002D", "-", cuerpo)   # reemplaza \u002D con guión normal
    
    # Eliminar firmas y metadatos
    cuerpo = re.sub(r"\*\[Nombre del remitente\]\*.*", "", cuerpo, flags=re.IGNORECASE)
    cuerpo = re.sub(r"Librería.*", "", cuerpo, flags=re.IGNORECASE)
    cuerpo = re.sub(r"Correo:.*", "", cuerpo, flags=re.IGNORECASE)
    cuerpo = re.sub(r"Tel[ée]fono:.*", "", cuerpo, flags=re.IGNORECASE)
    
    # Eliminar saludos comunes (al inicio y final)
    saludos_inicio = [
        r"^estimad[oa]s?\b.*", r"^buen[oa]s?\b.*", r"^hola\b.*", 
        r"^junto con saludar.*", r"^cordial saludo.*", r"^saludos cordiales.*"
    ]
    saludos_final = [
        r"^atentamente.*", r"^gracias.*", r"^quedamos atentos.*", 
        r"^me despido.*", r"^sin otro particular.*", r"^sinceramente.*",
        r"^saludos\b.*"
    ]
    
    # Procesar línea por línea
    lineas = cuerpo.splitlines()
    lineas_limpias = []
    en_seccion_productos = False
    
    for linea in lineas:
        linea = linea.strip()
        if not linea:
            continue
            
        # Verificar si estamos en la sección de productos
        if any(palabra in linea.lower() for palabra in ["cantidad", "descripción", "artículo", "productos"]):
            en_seccion_productos = True
            
        # Saltar saludos al inicio/final
        if (len(lineas_limpias) == 0 and any(re.match(pat, linea, re.IGNORECASE) for pat in saludos_inicio)):
            continue
        if any(re.match(pat, linea, re.IGNORECASE) for pat in saludos_final):
            continue
            
        # Mantener líneas con productos o información relevante
        if en_seccion_productos or re.match(r"\d+\s+[A-Za-zÁÉÍÓÚáéíóúñÑ]", linea):
            lineas_limpias.append(linea)
        elif "cotización" in linea.lower() or "solicit" in linea.lower():
            lineas_limpias.append(linea)
            
    cuerpo_limpio = "\n".join(lineas_limpias)
    
    # Eliminar espacios múltiples y unificar formato
    cuerpo_limpio = re.sub(r"\s+", " ", cuerpo_limpio)
    cuerpo_limpio = re.sub(r"(\d)\s+([A-Za-z])", r"\1 \2", cuerpo_limpio)  # unir cantidad con producto
    
    # Recortar si es muy largo preservando los productos
    if len(cuerpo_limpio) > max_length:
        # Primero extraer los productos claramente identificados
        productos = extraer_productos_de_correo(cuerpo_limpio)
        productos_str = "\n".join(productos)
        resto = cuerpo_limpio.replace(productos_str, "")
        if len(resto) > max_length // 2:
            resto = resto[:max_length // 2] + "..."
        cuerpo_limpio = productos_str + "\n" + resto
    
    return cuerpo_limpio.strip()

def extraer_productos_de_correo(cuerpo: str) -> list:
    """
    Extrae líneas que parecen productos de una cotización mejorado para el formato recibido
    """
    productos = []
    # Patrones mejorados para capturar productos
    patrones = [
        r"(\d+)\s+([A-Za-zÁÉÍÓÚáéíóúñÑ0-9\-\s,\.]+?)\s*(?=\d+|$)",  # Cantidad + Descripción
        r"-\s*(\d+)\s*([A-Za-zÁÉÍÓÚáéíóúñÑ0-9\-\s,\.]+)"  # Con viñetas
    ]
    
    for patron in patrones:
        for match in re.finditer(patron, cuerpo):
            cantidad = match.group(1).strip()
            descripcion = match.group(2).strip()
            # Filtrar descripciones muy cortas o que son parte de otros textos
            if len(descripcion) > 3 and not any(p in descripcion.lower() 
               for p in ["cotización", "solicit", "agradecería", "valores"]):
                producto = f"{cantidad} {descripcion}"
                productos.append(producto)
    
    return productos


class LlamaLocalLLM:
    """
    LLM local usando llama-cpp-python y un modelo GGUF en disco.
    """
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'llama-2-7b.Q4_K_M.gguf')
            model_path = os.path.abspath(model_path)
        self.model_path = model_path
        # Aumentar ventana de contexto
        self.llm = Llama(model_path=self.model_path, n_ctx=2048)

    def generate_response(self, context: Dict[str, Any], max_tokens: int = 512) -> str:
        prompt = context["system_prompt"]
        # Limitar el prompt a 700 tokens aprox (unos 2800 caracteres)
        if len(prompt) > 2800:
            prompt = prompt[:2800] + "..."
        print(f"[DEBUG] Prompt enviado a Llama: {prompt}")
        output = self.llm(prompt, max_tokens=max_tokens, temperature=0.7)
        print(f"[DEBUG] Output Llama: {output}")
        return output['choices'][0]['text']


class AIAgent:
    """
    Agente IA optimizado para respuestas precisas y manejo robusto de JSON.
    Usa solo LlamaLocalLLM (modelo local con llama-cpp-python).
    """
    def __init__(self, model_path=None):
        self.llm = LlamaLocalLLM(model_path=model_path)

    def process_query(self, query: str) -> dict:
        try:
            requested_items = self._parse_requested_items(query)
            relevant_products = []
            for item in requested_items:
                products = embeddings_manager.search_similar(item['name'], k=2)
                for p in products:
                    p['requested_quantity'] = item['quantity']
                relevant_products.extend(products)
            context = self._prepare_context(query, requested_items, relevant_products)
            # Limitar el contexto a los datos más relevantes
            if 'system_prompt' in context and len(context['system_prompt']) > 2800:
                context['system_prompt'] = context['system_prompt'][:2800] + "..."
            raw_response = self.llm.generate_response(context)
            print("[DEBUG] Raw AI response:", raw_response)
            return self._validate_and_clean_response(raw_response, requested_items, relevant_products)
        except Exception as e:
            print(f"[ERROR] process_query: {str(e)}")
            return {"productos": [], "error": f"Error procesando consulta: {str(e)}"}

    def generar_respuesta(self, cuerpo_correo: str) -> str:
        # Limpiar el cuerpo del correo antes de enviarlo a la IA
        cuerpo_correo_limpio = limpiar_y_optimizar_correo(cuerpo_correo)
        productos = extraer_productos_de_correo(cuerpo_correo_limpio)
        productos_str = "\n".join(productos)
        prompt = (
            "Eres un encargado de ventas de una librería en Chile. Redacta una respuesta formal y cordial, SOLO en español, para el siguiente correo de solicitud de cotización. "
            "La respuesta debe ser únicamente texto plano, sin formato, sin listas, sin negritas, sin HTML, sin Markdown. "
            "Para cada producto solicitado, responde de forma sencilla pero bien explicada, detallando: nombre del producto, cantidad solicitada, precio unitario, precio total, cantidad disponible en stock y si el stock es suficiente para la cantidad pedida. Si lo consideras útil, puedes añadir una breve descripción de los beneficios o características clave de cada producto. "
            "Incluye plazos de entrega, condiciones de pago y garantías si es posible. No repitas el texto original, responde como un humano profesional. Bajo ninguna circunstancia respondas en inglés ni en otro idioma que no sea español. Si el correo está en otro idioma, responde igualmente SOLO en español.\n\n"
            f"Productos solicitados:\n{productos_str}"
        )
        try:
            return self.llm.generate_response({"system_prompt": prompt}, max_tokens=512)
        except Exception as e:
            return f"[Error generando respuesta: {str(e)}]"

    def _parse_requested_items(self, query: str) -> List[Dict[str, Any]]:
        """
        Extrae los productos y cantidades solicitadas de la consulta.
        Ejemplo: "2 cuadernos 1 lapiz" -> [{'name': 'cuadernos', 'quantity': 2}, ...]
        """
        pattern = r'(\d+)\s+([a-zA-ZáéíóúñÑ\s]+)'
        matches = re.findall(pattern, query.lower())
        
        if not matches:
            # Si no encuentra patrones, asume cantidad 1 para toda la consulta
            return [{'name': query.strip(), 'quantity': 1}]
        
        return [{'name': name.strip(), 'quantity': int(q)} for q, name in matches]
    
    def _prepare_context(self, query: str, requested_items: List[Dict], products: List[Dict]) -> Dict[str, Any]:
        """Prepara el contexto para el LLM con énfasis en los items solicitados."""
        # Formatear productos disponibles usando el campo 'text' como nombre estándar
        products_str = "\n".join([
            f"- {p['text']} (Marca: {p['metadata'].get('brand', 'Genérica')}, "
            f"Precio: ${p['metadata'].get('price', 0)}, "
            f"Calidad: {p['metadata'].get('quality', 'Estándar')})"
            for p in products
        ])
        # Formatear items solicitados
        requested_str = "\n".join([
            f"- {item['quantity']} x {item['name']}" for item in requested_items
        ])
        return {
            "query": query,
            "requested_items": requested_items,
            "products": products,
            "system_prompt": (
                "INSTRUCCIONES CRÍTICAS:\n"
                "1. Responde ÚNICAMENTE con un array JSON válido.\n"
                "2. Solo incluye productos que coincidan EXACTAMENTE con los ITEMS SOLICITADOS.\n"
                "3. Cada objeto debe tener estas claves: 'producto', 'marca', 'precio', 'calidad', 'stock', 'cantidad_sugerida'.\n"
                "4. El campo 'producto' debe ser exactamente el nombre que aparece en la lista de productos disponibles (campo 'text').\n"
                "5. 'cantidad_sugerida' DEBE ser igual a la cantidad solicitada por el usuario.\n"
                "6. Si no hay coincidencias exactas, devuelve array vacío.\n\n"
                "ITEMS SOLICITADOS:\n"
                f"{requested_str}\n\n"
                "PRODUCTOS DISPONIBLES:\n"
                f"{products_str}\n\n"
                "RESPUESTA (solo JSON):"
            )
        }
    
    def _validate_and_clean_response(self, raw_response: str, requested_items: List[Dict], products: List[Dict]=None) -> dict:
        """Valida y limpia la respuesta del LLM con chequeos menos estrictos para nombres de producto."""
        def clean_name(name):
            return name.lower().replace('producto:', '').strip()
        try:
            cleaned = self._clean_json_response(raw_response)
            json_match = re.search(r'(\[\s*\{.*?\}\s*\])', cleaned, re.DOTALL)
            if not json_match:
                return {"productos": [], "error": "Formato de respuesta inválido"}
            productos = json.loads(json_match.group(1))
            if not isinstance(productos, list):
                return {"productos": [], "error": "La respuesta no es una lista"}
            valid_products = []
            required_keys = {"producto", "marca", "precio", "calidad", "stock", "cantidad_sugerida"}
            product_names = set()
            if products:
                product_names = set(p['text'].lower() for p in products)
            for prod in productos:
                if not isinstance(prod, dict):
                    continue
                if not required_keys.issubset(prod.keys()):
                    continue
                product_name = prod['producto'].strip().lower()
                # Permitir coincidencias aunque la IA agregue prefijos como 'Producto: '
                if product_names and not any(clean_name(n) == clean_name(product_name) for n in product_names):
                    continue
                clean_prod = {
                    'producto': prod.get('producto', '').strip(),
                    'marca': prod.get('marca', 'Genérica').strip(),
                    'precio': float(prod.get('precio', 0)),
                    'calidad': prod.get('calidad', 'Estándar').strip(),
                    'stock': int(prod.get('stock', 0)),
                    'cantidad_sugerida': int(prod.get('cantidad_sugerida', 1))
                }
                for item in requested_items:
                    if clean_name(item['name']) in clean_name(product_name):
                        clean_prod['cantidad_sugerida'] = item['quantity']
                        break
                valid_products.append(clean_prod)
            return {"productos": valid_products, "error": None}
        except Exception as e:
            print(f"[ERROR] Validating response: {str(e)}")
            return {"productos": [], "error": f"Error procesando respuesta: {str(e)}"}
    
    def _clean_json_response(self, text: str) -> str:
        """Limpia la respuesta JSON del LLM."""
        # Eliminar caracteres problemáticos
        replacements = [
            (r'\\"', '"'),
            (r'\\n', ''),
            (r'```json', ''),
            (r'```', ''),
            (r'"{', '{'),
            (r'}"', '}'),
            (r'"(?=\w)', '" '),  # Arregla comillas pegadas a palabras
            (r'\bnull\b', '0'),   # Reemplaza nulls por 0
        ]
        
        for pattern, repl in replacements:
            text = re.sub(pattern, repl, text)
        
        # Corregir claves duplicadas
        text = re.sub(r'("[a-zA-Z_]+"):\s*\1:\s*', r'\1: ', text)
        
        return text.strip()


# Instancia global del agente
ai_agent = AIAgent(model_path="models/llama-2-7b.Q4_K_M.gguf")