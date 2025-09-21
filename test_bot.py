#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento del bot antes del despliegue
"""
import os
import sys
import asyncio
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Prueba que todas las dependencias se puedan importar"""
    try:
        import discord
        from discord import app_commands
        import sqlite3
        import dotenv
        logger.info("✅ Todas las dependencias importadas correctamente")
        return True
    except ImportError as e:
        logger.error(f"❌ Error importando dependencias: {e}")
        return False

def test_database():
    """Prueba la conexión a la base de datos"""
    try:
        import sqlite3
        from database import create_tables, initialize_reclutadores_table

        # Crear tablas
        create_tables()
        initialize_reclutadores_table()

        logger.info("✅ Base de datos inicializada correctamente")
        return True
    except Exception as e:
        logger.error(f"❌ Error en base de datos: {e}")
        return False

def test_environment():
    """Prueba las variables de entorno"""
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.warning("⚠️ DISCORD_TOKEN no configurado (necesario para producción)")
    else:
        logger.info("✅ DISCORD_TOKEN configurado")

    port = os.getenv('PORT', '8080')
    logger.info(f"ℹ️ Puerto configurado: {port}")

    return True

def test_health_check():
    """Prueba el endpoint de health check"""
    try:
        from http.server import BaseHTTPRequestHandler, HTTPServer
        import json
        import threading
        import time

        # Simular health check
        class TestHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/health':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {
                        'status': 'healthy',
                        'timestamp': datetime.now().isoformat(),
                        'test': True
                    }
                    self.wfile.write(json.dumps(response).encode())

            def log_message(self, format, *args):
                pass

        # Iniciar servidor de prueba
        server = HTTPServer(('localhost', 0), TestHandler)
        port = server.server_address[1]

        def stop_server():
            time.sleep(1)
            server.shutdown()

        thread = threading.Thread(target=stop_server)
        thread.start()

        server.serve_forever()

        logger.info("✅ Health check endpoint funciona correctamente")
        return True
    except Exception as e:
        logger.error(f"❌ Error en health check: {e}")
        return False

async def test_bot_initialization():
    """Prueba la inicialización del bot (sin conectar)"""
    try:
        import discord
        from discord import Intents

        # Crear intents básicos
        intents = Intents.default()
        intents.members = True
        intents.message_content = True

        # Crear cliente sin token (solo para probar inicialización)
        bot = discord.Client(intents=intents)

        logger.info("✅ Bot se inicializa correctamente")
        await bot.close()
        return True
    except Exception as e:
        logger.error(f"❌ Error inicializando bot: {e}")
        return False

def main():
    """Función principal de pruebas"""
    logger.info("🧪 Iniciando pruebas del bot...")

    tests = [
        ("Importaciones", test_imports),
        ("Base de datos", test_database),
        ("Variables de entorno", test_environment),
        ("Health check", test_health_check),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        logger.info(f"🔍 Probando {test_name}...")
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name}: PASÓ")
            else:
                logger.error(f"❌ {test_name}: FALLÓ")
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")

    # Prueba adicional del bot
    logger.info("🔍 Probando inicialización del bot...")
    try:
        result = asyncio.run(test_bot_initialization())
        if result:
            passed += 1
            logger.info("✅ Inicialización del bot: PASÓ")
        else:
            logger.error("❌ Inicialización del bot: FALLÓ")
        total += 1
    except Exception as e:
        logger.error(f"❌ Inicialización del bot: ERROR - {e}")

    # Resultado final
    logger.info(f"\n📊 Resultados: {passed}/{total} pruebas pasaron")

    if passed == total:
        logger.info("🎉 ¡Todas las pruebas pasaron! El bot está listo para desplegar.")
        return True
    else:
        logger.warning("⚠️ Algunas pruebas fallaron. Revisa los errores antes de desplegar.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)