# Usar imagen base de Python más segura
FROM python:3.11-bookworm-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de requisitos
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorio para logs
RUN mkdir -p /app/logs

# Crear usuario no root
RUN useradd --create-home --shell /bin/bash discord-bot && \
    chown -R discord-bot:discord-bot /app

# Cambiar a usuario no root
USER discord-bot

# Comando para ejecutar
CMD ["python", "run_bot.py"]