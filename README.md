# LibrerIA

LibrerIA es una plataforma inteligente para la gestión de pedidos, consultas y cotizaciones de productos en una librería, automatizando la atención de correos electrónicos y la generación de respuestas usando IA local.

## Tecnologías principales
- **Django**: Framework web principal (backend y frontend).
- **llama-cpp-python**: Motor de IA local basado en modelos Llama (formato GGUF, sin depender de la nube).
- **Gmail IMAP/SMTP**: Integración para leer y responder correos electrónicos automáticamente.
- **Python 3.10+**
- **Bootstrap**: Para la interfaz web.

## ¿Qué hace LibrerIA?
- Lee automáticamente los correos recibidos en la cuenta configurada (Gmail).
- Filtra y muestra solo los correos que sean consultas, cotizaciones, pedidos o preguntas de precios.
- Permite ver el detalle de cada correo y responder con un solo clic usando IA local.
- La respuesta generada es formal, en español, personalizada y centrada en los productos solicitados, precios, stock y condiciones.
- Permite editar la respuesta antes de enviarla.
- Elimina correos del sistema para mantener la bandeja limpia.
- Gestiona inventario y listas de productos sugeridos por IA.

## Instalación y configuración rápida
1. **Clona el repositorio y entra al directorio:**
   ```bash
   git clone ...
   cd librerIA-main
   ```
2. **Crea y activa un entorno virtual:**
   ```bash
   python -m venv env
   source env/bin/activate  # Linux/Mac
   .\env\Scripts\activate  # Windows
   ```
3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configura tu cuenta de Gmail:**
   - Edita `email_config.py` con tus credenciales de Gmail (usa una contraseña de aplicación).
5. **Descarga un modelo Llama en formato GGUF:**
   - Descarga desde HuggingFace (por ejemplo, TheBloke/Llama-2-7B-GGUF) y colócalo en la carpeta `models/`.
6. **Configura variables de entorno si usas `django-environ` (opcional).**
7. **Ejecuta las migraciones y el servidor:**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## Uso del sistema
- Accede a la web y entra a la sección "Correos Recibidos".
- Solo verás correos que sean consultas, cotizaciones, pedidos o preguntas de precios.
- Haz clic en un correo para ver el detalle y pulsa "Responder con IA" para generar una respuesta automática.
- Puedes editar la respuesta antes de enviarla.
- El sistema también permite gestionar inventario y listas de productos sugeridos por IA.

## ¿Cómo funciona la respuesta automática?
- El cuerpo del correo se limpia y optimiza automáticamente.
- Se extraen los productos y datos relevantes.
- Se genera un prompt detallado para el modelo Llama local, que responde en español, de forma formal y centrada en los productos y condiciones solicitadas.
- La respuesta es revisable y editable antes de enviarse.

## Personalización y mejoras
- Puedes ajustar las palabras clave para filtrar correos en `ia_agente/utils.py`.
- Puedes cambiar el modelo Llama por otro compatible en la carpeta `models/`.
- El sistema es extensible para otros proveedores de correo o IA local.

## Requisitos
- Python 3.10+
- Cuenta de Gmail con IMAP y SMTP habilitados
- Modelo Llama en formato GGUF (recomendado: 7B o 13B, versión cuantizada para CPU)
- 8GB de RAM mínimo (recomendado 16GB para modelos grandes)

## Licencia
MIT
