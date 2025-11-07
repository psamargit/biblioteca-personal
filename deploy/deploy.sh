#!/bin/bash

###############################################################################
# Script de despliegue para Biblioteca Personal en VPS
# Este script automatiza la instalación y configuración en Ubuntu/Debian
###############################################################################

set -e  # Salir si hay algún error

echo "========================================="
echo "Despliegue de Biblioteca Personal"
echo "========================================="
echo ""

# Variables de configuración
APP_NAME="biblioteca-personal"
APP_DIR="/var/www/$APP_NAME"
APP_USER="www-data"
PYTHON_VERSION="python3"
VENV_DIR="$APP_DIR/venv"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funciones de ayuda
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Verificar que se ejecuta como root
if [ "$EUID" -ne 0 ]; then
    error "Este script debe ejecutarse como root (usa sudo)"
fi

# 1. Actualizar sistema
info "Actualizando sistema..."
apt-get update
apt-get upgrade -y

# 2. Instalar dependencias del sistema
info "Instalando dependencias del sistema..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    nginx \
    git \
    supervisor

# 3. Crear directorio de la aplicación
info "Creando directorio de aplicación en $APP_DIR..."
mkdir -p $APP_DIR
cd $APP_DIR

# 4. Clonar/copiar código (ajustar según tu caso)
# Si el código ya está en el servidor:
# info "Código ya presente en el servidor"
# Si necesitas clonar desde git:
# git clone https://github.com/tu-usuario/biblioteca-personal.git $APP_DIR

# 5. Crear entorno virtual
info "Creando entorno virtual de Python..."
$PYTHON_VERSION -m venv $VENV_DIR

# 6. Activar entorno virtual e instalar dependencias
info "Instalando dependencias de Python..."
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 7. Configurar variables de entorno
info "Configurando variables de entorno..."
if [ ! -f "$APP_DIR/.env" ]; then
    cp $APP_DIR/.env.example $APP_DIR/.env

    # Generar SECRET_KEY aleatoria
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i "s/tu-clave-secreta-muy-segura-cambiar-en-produccion/$SECRET_KEY/" $APP_DIR/.env
    sed -i "s/FLASK_ENV=development/FLASK_ENV=production/" $APP_DIR/.env
    sed -i "s/FLASK_DEBUG=True/FLASK_DEBUG=False/" $APP_DIR/.env

    warn "Se ha creado el archivo .env. Por favor, revísalo y ajusta las configuraciones necesarias."
else
    info "Archivo .env ya existe, no se sobreescribe"
fi

# 8. Crear directorios necesarios
info "Creando directorios necesarios..."
mkdir -p $APP_DIR/instance
mkdir -p $APP_DIR/app/static/uploads/covers
mkdir -p $APP_DIR/logs

# 9. Inicializar base de datos
info "Inicializando base de datos..."
export FLASK_APP=run.py
flask init-db

# 10. Crear usuario administrador (interactivo)
info "Creando usuario administrador..."
warn "Ingresa las credenciales para el usuario administrador:"
flask create-admin

# 11. Configurar permisos
info "Configurando permisos..."
chown -R $APP_USER:$APP_USER $APP_DIR
chmod -R 755 $APP_DIR
chmod -R 775 $APP_DIR/app/static/uploads
chmod -R 775 $APP_DIR/instance
chmod -R 775 $APP_DIR/logs

# 12. Configurar systemd service
info "Configurando servicio systemd..."
cp $APP_DIR/deploy/biblioteca.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable biblioteca.service
systemctl start biblioteca.service

# 13. Configurar Nginx
info "Configurando Nginx..."
cp $APP_DIR/deploy/nginx.conf /etc/nginx/sites-available/biblioteca
ln -sf /etc/nginx/sites-available/biblioteca /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Verificar configuración de Nginx
nginx -t

# Reiniciar Nginx
systemctl restart nginx

# 14. Configurar firewall (UFW)
info "Configurando firewall..."
ufw allow 'Nginx Full'
ufw allow OpenSSH
ufw --force enable

info "========================================="
info "¡Despliegue completado exitosamente!"
info "========================================="
echo ""
info "La aplicación está corriendo en:"
echo "  - http://$(hostname -I | awk '{print $1}')"
echo ""
info "Para ver el estado del servicio:"
echo "  sudo systemctl status biblioteca"
echo ""
info "Para ver los logs:"
echo "  sudo journalctl -u biblioteca -f"
echo ""
warn "IMPORTANTE: No olvides:"
echo "  1. Configurar tu dominio en /etc/nginx/sites-available/biblioteca"
echo "  2. Instalar certificado SSL con Let's Encrypt (certbot)"
echo "  3. Revisar las configuraciones en $APP_DIR/.env"
echo "  4. Configurar backups regulares de la base de datos"
echo ""
