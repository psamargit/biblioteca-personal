"""
Configuración de Gunicorn para producción
"""
import multiprocessing
import os

# Dirección de bind
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# Workers
# Fórmula recomendada: (2 x $num_cores) + 1
# Para VPS con 2GB RAM, 2-4 workers es adecuado
workers = int(os.getenv('GUNICORN_WORKERS', '3'))
worker_class = 'sync'
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Timeouts
timeout = 30
keepalive = 2
graceful_timeout = 30

# Logging
accesslog = os.getenv('GUNICORN_ACCESS_LOG', '-')  # '-' para stdout
errorlog = os.getenv('GUNICORN_ERROR_LOG', '-')    # '-' para stderr
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'biblioteca_personal'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (si se usa)
# keyfile = '/path/to/key.pem'
# certfile = '/path/to/cert.pem'
