#!/bin/bash
# Script de instalación para Render

echo "🚀 Instalando dependencias para Discord Bot..."

# Actualizar pip
pip install --upgrade pip

# Instalar dependencias principales
pip install discord.py>=2.3.0 python-dotenv>=1.0.0 aiohttp>=3.8.0

# Verificar instalación
python -c "import discord; print('✅ discord.py versión:', discord.__version__)"
python -c "import dotenv; print('✅ python-dotenv instalado correctamente')"
python -c "import aiohttp; print('✅ aiohttp instalado correctamente')"

echo "🎉 Instalación completada"