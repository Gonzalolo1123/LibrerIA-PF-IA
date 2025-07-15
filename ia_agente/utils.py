from asistente_compras.models import Product
import imaplib
import email
from email.header import decode_header
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_config import EMAIL_CONFIG
import re
from django.core.cache import cache
import hashlib
from email.utils import parsedate_to_datetime

def get_products_for_embeddings():
    productos = Product.objects.all()
    return [
        {
            "id": p.id,
            "text": f"{p.name} de {p.brand}. {p.description}",
            "metadata": {
                "price": float(p.price),
                "stock": p.stock,
                "quality": p.quality_category
            }
        }
        for p in productos
    ]


def leer_correos_gmail():
    """
    Lee los correos recibidos en la cuenta de Gmail configurada.
    Devuelve una lista de diccionarios con asunto, remitente y cuerpo.
    """
    correos = []
    usuario = EMAIL_CONFIG['EMAIL_HOST_USER']
    password = EMAIL_CONFIG['EMAIL_HOST_PASSWORD']
    imap_server = 'imap.gmail.com'
    
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(usuario, password)
    mail.select('inbox')
    status, mensajes = mail.search(None, 'ALL')
    for num in mensajes[0].split():
        status, data = mail.fetch(num, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])
        asunto, encoding = decode_header(msg['Subject'])[0]
        if isinstance(asunto, bytes):
            asunto = asunto.decode(encoding if encoding else 'utf-8')
        remitente = msg.get('From')
        cuerpo = ""
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get('Content-Disposition'))
                if ctype == 'text/plain' and 'attachment' not in cdispo:
                    cuerpo = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
        else:
            cuerpo = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        # Obtener fecha legible
        fecha_raw = msg.get('Date')
        try:
            fecha_dt = parsedate_to_datetime(fecha_raw)
            fecha_legible = fecha_dt.strftime('%d/%m/%Y %H:%M')
        except:
            fecha_legible = fecha_raw or ''
        correos.append({
            'asunto': asunto,
            'remitente': remitente,
            'cuerpo': cuerpo,
            'fecha': fecha_legible
        })
    mail.logout()
    return correos


def enviar_correo(destinatario, asunto, cuerpo):
    """
    Envía un correo desde la cuenta configurada a un destinatario.
    """
    usuario = EMAIL_CONFIG['EMAIL_HOST_USER']
    password = EMAIL_CONFIG['EMAIL_HOST_PASSWORD']
    smtp_server = 'smtp.gmail.com'
    puerto = 587
    
    msg = MIMEMultipart()
    msg['From'] = usuario
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(cuerpo, 'plain'))
    
    server = smtplib.SMTP(smtp_server, puerto)
    server.starttls()
    server.login(usuario, password)
    texto = msg.as_string()
    server.sendmail(usuario, destinatario, texto)
    server.quit()
    return True 


def es_pedido(correo):
    """
    Detecta si el correo es un pedido (por ejemplo, si contiene palabras clave como 'pedido', 'orden', 'comprar').
    """
    texto = (correo['asunto'] or '') + ' ' + (correo['cuerpo'] or '')
    palabras_clave = ['pedido', 'orden', 'comprar', 'solicito', 'necesito']
    return any(palabra in texto.lower() for palabra in palabras_clave)


def es_consulta_cotizacion(correo):
    """
    Detecta si el correo es una consulta, cotización o pregunta de precios.
    """
    texto = (correo['asunto'] or '') + ' ' + (correo['cuerpo'] or '')
    palabras_clave = [
        'cotización', 'cotizacion', 'consulta', 'precio', 'presupuesto', 'cuánto cuesta', 'valor', 'información', 'solicitud', 'requiero', 'me gustaría saber', 'pueden decirme', 'me podrían indicar', 'me pueden cotizar', 'me pueden enviar', 'me interesa', 'quiero saber', 'necesito saber', 'me gustaría recibir', 'me gustaría cotizar', 'me gustaría consultar'
    ]
    return any(palabra in texto.lower() for palabra in palabras_clave)


def extraer_productos_consulta(texto):
    """
    Busca nombres de productos en el texto del correo y devuelve una lista de coincidencias.
    """
    productos = Product.objects.all()
    encontrados = []
    for producto in productos:
        patron = re.compile(rf"\\b{re.escape(producto.name)}\\b", re.IGNORECASE)
        if patron.search(texto):
            encontrados.append(producto)
    return encontrados


def procesar_correos_gmail():
    """
    Procesa los correos recibidos: filtra pedidos y responde consultas de productos.
    """
    correos = leer_correos_gmail()
    for correo in correos:
        # 1. Si es pedido, guardar (aquí solo mostramos por consola)
        if es_pedido(correo):
            print(f"Pedido detectado de {correo['remitente']}: {correo['cuerpo']}")
            # Aquí podrías guardar en la base de datos o en Firebase
        else:
            # 2. Si es consulta de producto, responder automáticamente
            productos = extraer_productos_consulta(correo['cuerpo'])
            if productos:
                respuesta = ""
                for prod in productos:
                    respuesta += f"El producto '{prod.name}' cuesta ${prod.price} y es de la marca {prod.brand}.\n"
                enviar_correo(
                    destinatario=correo['remitente'],
                    asunto=f"Respuesta sobre productos consultados",
                    cuerpo=respuesta
                )
                print(f"Respuesta automática enviada a {correo['remitente']} sobre productos: {[p.name for p in productos]}") 


ELIMINADOS_CACHE_KEY = 'correos_eliminados_ids'

def obtener_ids_eliminados():
    return cache.get(ELIMINADOS_CACHE_KEY, set())

def marcar_correo_eliminado(correo_id):
    eliminados = obtener_ids_eliminados()
    eliminados.add(correo_id)
    cache.set(ELIMINADOS_CACHE_KEY, eliminados, timeout=None)

def filtrar_correos_no_eliminados(correos):
    eliminados = obtener_ids_eliminados()
    return [c for c in correos if c['id'] not in eliminados]

# Modificar leer_correos_gmail para agregar un id único a cada correo (por ejemplo, hash de remitente+asunto+cuerpo)
_original_leer_correos_gmail = leer_correos_gmail

def correo_hash(correo):
    base = (correo['remitente'] or '') + (correo['asunto'] or '') + (correo['cuerpo'] or '')
    return hashlib.md5(base.encode('utf-8')).hexdigest()

def leer_correos_gmail():
    correos = _original_leer_correos_gmail()
    for c in correos:
        c['id'] = correo_hash(c)
    # Filtrar solo correos que sean pedidos o consultas/cotizaciones/precios
    return filtrar_correos_no_eliminados([
        c for c in correos if es_pedido(c) or es_consulta_cotizacion(c)
    ]) 