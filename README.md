# 📚 Biblioteca Personal

Sistema completo de inventario de libros físicos y digitales desarrollado con Python, Flask y SQLite. Perfecto para organizar tu colección personal de libros con una interfaz moderna y responsive.

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Flask Version](https://img.shields.io/badge/flask-3.0%2B-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## ✨ Características Principales

### 📖 Gestión de Libros
- **CRUD Completo**: Crear, leer, actualizar y eliminar libros
- **Doble Formato**: Soporte para libros físicos y digitales
- **Información Detallada**:
  - Título, autor(es), ISBN/Código de barras
  - Editorial, año de publicación
  - Género/Categoría
  - Estado de lectura (Leído/No leído/Leyendo)
  - Ubicación física y formato digital
  - Portada (URL o archivo subido)
  - Notas personales
  - Fecha de adquisición y precio

### 🔍 Búsqueda Avanzada
- Búsqueda por título, autor, ISBN
- Filtros por género, tipo, estado
- Búsqueda de texto completo
- Vista en tabla o tarjetas
- Paginación inteligente

### 📱 Escáner de Código de Barras
- Lectura de códigos ISBN con cámara web
- Integración con Google Books API
- Auto-completado de información del libro
- Verificación automática en tu biblioteca

### 📊 Dashboard con Estadísticas
- Total de libros (físicos vs digitales)
- Estado de lectura (leídos, leyendo, no leídos)
- Top géneros más comunes
- Libros agregados recientemente
- Préstamos activos y vencidos

### 🤝 Sistema de Préstamos
- Registrar préstamos con información del prestatario
- Fechas de préstamo y devolución
- Alertas de préstamos vencidos
- Historial completo de préstamos

### ❤️ Lista de Deseos
- Libros por comprar
- Priorización (Alta/Media/Baja)
- Precio estimado
- URLs de tiendas online
- Marcado de items adquiridos

### 🏷️ Sistema de Etiquetas
- Etiquetas personalizadas
- Colores personalizados
- Organización flexible

### 📤 Importación/Exportación
- Exportar inventario a CSV/Excel
- Importación masiva desde CSV
- Plantilla de ejemplo incluida

### 🔐 Seguridad
- Autenticación de usuario
- Contraseñas hasheadas
- Protección CSRF
- Sanitización de entradas
- Variables de entorno para credenciales

## 🚀 Instalación

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git (opcional)

### Instalación Local (Desarrollo)

1. **Clonar el repositorio**
```bash
git clone https://github.com/tu-usuario/biblioteca-personal.git
cd biblioteca-personal
```

2. **Crear entorno virtual**
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. **Inicializar base de datos**
```bash
flask init-db
```

6. **Crear usuario administrador**
```bash
flask create-admin
```

7. **Ejecutar la aplicación**
```bash
python run.py
```

La aplicación estará disponible en `http://localhost:5000`

## 🌐 Despliegue en VPS

### Despliegue Automatizado

Para desplegar en un VPS con Ubuntu/Debian:

```bash
# Copiar archivos al servidor
scp -r . usuario@tu-servidor:/tmp/biblioteca-personal

# Conectar al servidor
ssh usuario@tu-servidor

# Mover archivos y ejecutar script de despliegue
sudo mv /tmp/biblioteca-personal /var/www/
cd /var/www/biblioteca-personal
sudo chmod +x deploy/deploy.sh
sudo ./deploy/deploy.sh
```

El script automatizado:
- Instala todas las dependencias del sistema
- Configura Nginx como proxy reverso
- Configura Gunicorn como servidor WSGI
- Crea servicio systemd para inicio automático
- Configura firewall básico
- Inicializa la base de datos

### Configuración Manual

#### 1. Instalar dependencias del sistema
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv nginx supervisor git
```

#### 2. Configurar Gunicorn
```bash
# El archivo gunicorn_config.py ya está incluido
gunicorn -c gunicorn_config.py run:app
```

#### 3. Configurar Nginx
```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/biblioteca
sudo ln -s /etc/nginx/sites-available/biblioteca /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 4. Configurar servicio systemd
```bash
sudo cp deploy/biblioteca.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable biblioteca
sudo systemctl start biblioteca
```

### Configurar SSL con Let's Encrypt

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com
```

## 📖 Uso

### Comandos CLI Disponibles

```bash
# Inicializar base de datos
flask init-db

# Crear usuario administrador
flask create-admin

# Acceder al shell de Flask
flask shell

# Ejecutar servidor de desarrollo
flask run

# Ver todas las rutas disponibles
flask routes
```

### Importar Libros desde CSV

El formato del CSV debe incluir estas columnas:

```csv
Título,Autores,ISBN,Editorial,Año de Publicación,Género,Tipo,Estado,Ubicación,Formato,Descripción,Notas,Fecha de Adquisición,Precio,Etiquetas
"El Quijote","Miguel de Cervantes","9788420412146","RAE","2004","Novela","physical","read","Estante 1","","","Primera lectura","2023-01-15","25.50","clásicos,español"
```

### API de Google Books

Para habilitar el auto-completado con Google Books:

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto nuevo
3. Habilita la API de Google Books
4. Crea credenciales (API Key)
5. Añade la clave a tu archivo `.env`:
```
GOOGLE_BOOKS_API_KEY=tu-api-key-aqui
```

## 🗂️ Estructura del Proyecto

```
biblioteca-personal/
├── app/
│   ├── __init__.py              # Inicialización de Flask
│   ├── commands.py              # Comandos CLI
│   ├── forms/                   # Formularios WTForms
│   │   ├── auth_forms.py
│   │   ├── book_forms.py
│   │   ├── loan_forms.py
│   │   ├── wishlist_forms.py
│   │   └── tag_forms.py
│   ├── models/                  # Modelos de base de datos
│   │   ├── user.py
│   │   ├── book.py
│   │   ├── loan.py
│   │   ├── wishlist.py
│   │   └── tag.py
│   ├── views/                   # Vistas/Controladores
│   │   ├── auth.py              # Autenticación
│   │   ├── books.py             # Gestión de libros
│   │   ├── dashboard.py         # Dashboard
│   │   ├── loans.py             # Préstamos
│   │   ├── wishlist.py          # Lista de deseos
│   │   └── api.py               # API endpoints
│   ├── templates/               # Plantillas Jinja2
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── books/
│   │   ├── dashboard/
│   │   ├── loans/
│   │   └── wishlist/
│   ├── static/                  # Archivos estáticos
│   │   ├── css/
│   │   ├── js/
│   │   └── uploads/
│   └── utils/                   # Utilidades
│       └── helpers.py
├── config/                      # Configuraciones
│   ├── config.py
│   └── __init__.py
├── deploy/                      # Archivos de despliegue
│   ├── deploy.sh
│   ├── nginx.conf
│   └── biblioteca.service
├── instance/                    # Base de datos (no en git)
├── tests/                       # Pruebas (opcional)
├── .env.example                 # Plantilla de variables de entorno
├── .gitignore
├── gunicorn_config.py          # Configuración de Gunicorn
├── README.md
├── requirements.txt            # Dependencias Python
└── run.py                      # Punto de entrada
```

## 🛠️ Tecnologías Utilizadas

### Backend
- **Flask 3.0** - Framework web
- **SQLAlchemy** - ORM para base de datos
- **Flask-Login** - Gestión de sesiones
- **Flask-WTF** - Formularios y validación
- **SQLite** - Base de datos

### Frontend
- **Bootstrap 5** - Framework CSS
- **Bootstrap Icons** - Iconos
- **QuaggaJS** - Lector de códigos de barras
- **JavaScript (Vanilla)** - Interactividad

### Despliegue
- **Gunicorn** - Servidor WSGI
- **Nginx** - Proxy reverso
- **Systemd** - Gestión de servicios

## 📊 Capturas de Pantalla

### Dashboard
Vista general con estadísticas y libros recientes.

### Gestión de Libros
Lista de libros con filtros y búsqueda avanzada.

### Escáner de Código de Barras
Escanea ISBNs con tu cámara web.

### Préstamos
Registra y gestiona préstamos de libros.

## 🔧 Configuración Avanzada

### Optimización para VPS con 2GB RAM

El proyecto está optimizado para ejecutarse en VPS con recursos limitados:

- **Gunicorn**: 3 workers por defecto (ajustable)
- **SQLite**: Base de datos ligera sin servidor adicional
- **Caché**: Headers de caché para archivos estáticos
- **Timeouts**: Configurados para evitar procesos bloqueados

### Variables de Entorno

```bash
# Flask
FLASK_ENV=production              # development, production, testing
FLASK_DEBUG=False                 # True solo en desarrollo
SECRET_KEY=clave-secreta-segura   # Generar aleatoriamente

# Base de datos
DATABASE_URL=sqlite:///instance/biblioteca.db

# Google Books API
GOOGLE_BOOKS_API_KEY=tu-api-key   # Opcional

# Gunicorn
GUNICORN_WORKERS=3                # (2 x CPU cores) + 1
PORT=8000                         # Puerto interno
```

## 🐛 Solución de Problemas

### La aplicación no inicia

```bash
# Verificar logs del servicio
sudo journalctl -u biblioteca -n 50

# Verificar estado del servicio
sudo systemctl status biblioteca

# Reiniciar servicio
sudo systemctl restart biblioteca
```

### Errores de base de datos

```bash
# Eliminar base de datos y reinicializar
rm instance/biblioteca.db
flask init-db
flask create-admin
```

### Problemas con permisos de archivos

```bash
sudo chown -R www-data:www-data /var/www/biblioteca-personal
sudo chmod -R 755 /var/www/biblioteca-personal
sudo chmod -R 775 /var/www/biblioteca-personal/app/static/uploads
```

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📧 Contacto

Para preguntas o sugerencias, por favor abre un issue en GitHub.

## 🙏 Agradecimientos

- [Flask](https://flask.palletsprojects.com/)
- [Bootstrap](https://getbootstrap.com/)
- [QuaggaJS](https://github.com/ericblade/quagga2)
- [Google Books API](https://developers.google.com/books)

---

Hecho con ❤️ para amantes de los libros
