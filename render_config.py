# Configuración de Python para Render
import os
import sys

# Configurar variables de entorno para mejor rendimiento
os.environ.setdefault('PYTHONUNBUFFERED', '1')
os.environ.setdefault('PYTHONHASHSEED', 'random')

# Optimizar para entornos de contenedor
if 'RENDER' in os.environ:
    # Configurar para Render
    os.environ.setdefault('PYTHONPATH', '/opt/render/project/src')

# Configurar asyncio para mejor rendimiento
import asyncio
asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

# Configurar logging para Render
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)