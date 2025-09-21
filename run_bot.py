#!/usr/bin/env python3
"""
Script de inicio para el Bot de Reclutamiento de Discord
Este script maneja el reinicio automático en caso de errores
"""

import subprocess
import time
import logging
import sys
import os
import threading
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_runner.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('bot_runner')

class HealthCheckHandler(BaseHTTPRequestHandler):
    """Handler simple para health checks de Render"""
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suprimir logs del servidor HTTP
        return

def start_health_server():
    """Inicia servidor HTTP para health checks"""
    try:
        port = int(os.environ.get('PORT', 8080))
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        logger.info(f"🌐 Health check server started on port {port}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"❌ Error starting health server: {e}")

def check_requirements():
    """Verifica que todos los requisitos estén instalados"""
    try:
        import discord
        import dotenv
        import sqlite3
        logger.info("✅ Todos los requisitos están instalados")
        return True
    except ImportError as e:
        logger.error(f"❌ Falta instalar dependencias: {e}")
        logger.info("Ejecuta: pip install -r requirements.txt")
        return False

def create_env_file():
    """Verifica que el DISCORD_TOKEN esté disponible (desde .env o variables de entorno)"""
    # Primero intentar desde variables de entorno (Render)
    token = os.environ.get('DISCORD_TOKEN')

    if not token:
        # Si no está en variables de entorno, intentar desde .env
        if not Path('.env').exists():
            logger.error("❌ Archivo .env no encontrado y DISCORD_TOKEN no está en variables de entorno")
            logger.info("Crea un archivo .env con tu DISCORD_TOKEN o configura la variable de entorno")
            return False

        # Verificar que tenga el token en .env
        from dotenv import load_dotenv
        load_dotenv()
        token = os.getenv('DISCORD_TOKEN')

    if not token:
        logger.error("❌ DISCORD_TOKEN no encontrado en .env ni en variables de entorno")
        return False

    logger.info("✅ DISCORD_TOKEN encontrado")
    return True

def run_bot():
    """Ejecuta el bot con manejo de reinicio automático"""
    max_retries = 10  # Más reintentos para Render
    retry_count = 0

    while retry_count < max_retries:
        try:
            logger.info(f"🚀 Iniciando bot (intento {retry_count + 1}/{max_retries})")

            # Ejecutar el bot
            process = subprocess.Popen([
                sys.executable, 'bot.py'
            ], cwd=os.getcwd())

            # Esperar a que termine
            return_code = process.wait()

            if return_code == 0:
                logger.info("✅ Bot terminó correctamente")
                break
            else:
                logger.warning(f"⚠️ Bot terminó con código {return_code}")
                retry_count += 1

                if retry_count < max_retries:
                    wait_time = min(120 * retry_count, 1800)  # Máximo 30 minutos
                    logger.info(f"⏳ Esperando {wait_time} segundos antes de reiniciar...")
                    time.sleep(wait_time)

        except KeyboardInterrupt:
            logger.info("🛑 Interrupción detectada")
            break
        except Exception as e:
            logger.error(f"❌ Error ejecutando el bot: {e}")
            retry_count += 1

            if retry_count < max_retries:
                wait_time = min(60 * retry_count, 1800)
                logger.info(f"⏳ Esperando {wait_time} segundos antes de reiniciar...")
                time.sleep(wait_time)

    if retry_count >= max_retries:
        logger.error("❌ Máximo número de reintentos alcanzado")
        return False

    return True

def main():
    """Función principal"""
    logger.info("🤖 Iniciando Discord Recruitment Bot en Render")

    # Iniciar servidor de health check en un hilo separado
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()

    # Verificar requisitos
    if not check_requirements():
        return False

    if not create_env_file():
        return False

    # Ejecutar el bot
    success = run_bot()

    if success:
        logger.info("✅ Bot Runner terminó correctamente")
    else:
        logger.error("❌ Bot Runner terminó con errores")

    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)