#!/bin/bash
# Script de instalación para Discord Recruitment Bot

echo "🤖 Instalando Discord Recruitment Bot..."

# Verificar si estamos en Linux/macOS
if [[ "$OSTYPE" != "linux-gnu"* ]] && [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Este script es para Linux/macOS"
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    exit 1
fi

echo "✅ Python 3 encontrado"

# Verificar pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 no está instalado"
    exit 1
fi

echo "✅ pip3 encontrado"

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Error instalando dependencias"
    exit 1
fi

echo "✅ Dependencias instaladas"

# Verificar archivo .env
if [ ! -f ".env" ]; then
    echo "⚠️  Archivo .env no encontrado"
    echo "📝 Creando archivo .env de ejemplo..."
    echo "# Copia este archivo y reemplaza con tu token real" > .env
    echo "DISCORD_TOKEN=tu_token_de_discord_aqui" >> .env
    echo "✅ Archivo .env creado. Edítalo con tu token real."
else
    echo "✅ Archivo .env encontrado"
fi

# Crear directorio para logs si no existe
mkdir -p logs

echo ""
echo "🎉 Instalación completada!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Edita el archivo .env con tu token de Discord"
echo "2. Ejecuta: python3 run_bot.py"
echo ""
echo "📚 Comandos disponibles:"
echo "• python3 run_bot.py     - Ejecutar con reinicio automático"
echo "• python3 bot.py         - Ejecutar directamente"
echo "• docker-compose up -d   - Ejecutar con Docker"
echo ""
echo "📖 Para más información, revisa el README.md"