# 📚 LibreriaIA: Asistente de Compras de Librería con IA

## 🎯 Objetivo del Proyecto

[cite_start]`LibreriaIA` es un Producto Mínimo Viable (MVP) diseñado para optimizar el proceso de compra de útiles escolares y de oficina, especialmente durante picos de demanda que saturan las librerías físicas. La aplicación permite a los usuarios introducir listas de útiles escolares. [cite_start]Utilizando una funcionalidad simulada de Inteligencia Artificial, la aplicación sugiere productos del catálogo de una librería, ofreciendo comparativas de precios y categorías de calidad (económico, intermedio, calidad).

[cite_start]Este proyecto cumple con los requisitos de un MVP funcional que integra IA como herramienta principal de apoyo, cuenta con un frontend con interfaz de usuario, una API para comunicación entre frontend y backend, y un backend que utiliza Firebase como base de datos (aunque en este MVP inicial de Django, la base de datos es SQLite para el desarrollo, con el objetivo de integración futura con Firebase para persistencia y escalabilidad).

## 💡 Problema que Resuelve

Durante el inicio del año escolar, las listas de útiles estudiantiles generan una demanda masiva que a menudo desborda la capacidad de las librerías, llevando a largas filas y frustración para los clientes. [cite_start]`LibreriaIA` agiliza este proceso al permitir a los usuarios obtener recomendaciones de productos y precios directamente desde una aplicación, cotejando sus listas con el catálogo de la librería y ofreciendo diversas opciones para ajustarse a sus necesidades y presupuestos.

## ✨ Características (MVP)

* **Gestión de Listas de Compras:** Los usuarios pueden crear y gestionar múltiples listas de útiles.
* **Entrada de Ítems de Lista:** Interfaz para que los usuarios ingresen los artículos que necesitan.
* [cite_start]**Sugerencias de Productos con IA (Simuladas):** La aplicación (a través de lógica de backend) "sugiere" productos del catálogo que coinciden con los ítems de la lista del usuario, clasificándolos por calidad y precio.
* [cite_start]**Frontend Básico:** Interfaz de usuario con al menos dos vistas o pantallas funcionales para la gestión de listas y detalles.
* [cite_start]**Backend con Django:** Gestión de la lógica de la aplicación y la persistencia de datos.
* [cite_start]**Integración con Firebase (Planeado):** Aunque inicialmente usa SQLite, el diseño del modelo está preparado para la integración futura con Firestore o Realtime Database de Firebase para almacenar datos de usuarios o inputs.
* [cite_start]**API REST (Simulada):** El backend Django expone rutas que actúan como endpoints REST para la comunicación con el frontend.

## 🛠️ Tecnologías Utilizadas

* **Backend:**
    * Python 3.x
    * Django (Framework Web)
    * Django REST Framework (para la API, aunque no totalmente implementado en el MVP inicial)
    * SQLite (Base de datos por defecto para desarrollo)
    * [cite_start]Firebase (Objetivo futuro para base de datos y/o hosting) 
* **Frontend:**
    * HTML5
    * CSS3
    * [cite_start](Se recomienda React, Angular u otros para una implementación completa, pero este MVP usa HTML/CSS puros) 
* **Inteligencia Artificial:**
    * [cite_start]Conceptualización y campos de datos para futuras integraciones de IA (ej. procesamiento de lenguaje natural para listas, motores de recomendación).
    * [cite_start]Se pueden usar asistentes de código con IA como GitHub Copilot, ChatGPT, Gemini, etc., durante el desarrollo.

## 🚀 Estructura del Proyecto

```
LibreriaIA/
├── LibreriaIA/                 # Configuración principal del proyecto
│   ├── settings.py            # Configuraciones de Django
│   ├── urls.py                # URLs principales
│   └── wsgi.py                # Configuración WSGI
├── asistente_compras/         # Aplicación principal
│   ├── models.py              # Modelos de datos
│   ├── views.py               # Vistas y lógica de negocio
│   ├── urls.py                # URLs de la aplicación
│   ├── admin.py               # Configuración del admin
│   ├── templates/             # Plantillas HTML
│   │   └── asistente_compras/
│   │       ├── base.html      # Plantilla base
│   │       ├── home.html      # Página de inicio
│   │       ├── notes.html     # Formulario de creación
│   │       └── list_detail.html # Detalles de lista
│   ├── templatetags/          # Filtros personalizados
│   │   └── custom_filters.py
│   └── management/            # Comandos personalizados
│       └── commands/
│           └── populate_products.py
├── static/                    # Archivos estáticos
│   └── css/
│       └── style.css          # Estilos personalizados
├── manage.py                  # Script de gestión de Django
├── populate_db.py             # Script de población (legacy)
└── README.md                  # Este archivo
```

## 🔧 Comandos Útiles

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Poblar base de datos
python manage.py populate_products

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor de desarrollo
python manage.py runserver

# Ejecutar tests (cuando se implementen)
python manage.py test
```

## 🎨 Tecnologías Utilizadas

- **Backend**: Django 5.2.3
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Frontend**: HTML5, CSS3, JavaScript
- **Framework CSS**: Bootstrap 5.3.0
- **Iconos**: Font Awesome 6.0.0
- **Lenguaje**: Python 3.13

## 🔮 Próximas Mejoras

- [ ] Integración con modelo de IA real (OpenAI, Google AI, etc.)
- [ ] Sistema de autenticación de usuarios
- [ ] API REST para integración con aplicaciones móviles
- [ ] Sistema de notificaciones
- [ ] Exportación de listas a PDF/Excel
- [ ] Comparación de precios entre diferentes librerías
- [ ] Sistema de cupones y descuentos
- [ ] Integración con sistemas de pago

## 🤝 Contribución

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Contacto

Para preguntas o soporte, contacta al equipo de desarrollo.

---

**Desarrollado con ❤️ y Django**
