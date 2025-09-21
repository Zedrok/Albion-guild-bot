# 🤖 Discord Recruitment Bot

Bot de Discord para gestión de reclutamiento con sistema de seguimiento de miembros y estadísticas.

## 📋 Requisitos del Sistema

- ✅ **Python 3.11+** (Compatible con 3.13)
- ✅ **discord.py 2.3.0+** (Actualizado para compatibilidad)
- ✅ **SQLite** (incluido con Python)
- ✅ **Git** (para despliegue)

### ⚠️ Importante para Python 3.13
Si usas Python 3.13, asegúrate de tener discord.py >= 2.3.0 para compatibilidad completa.

## 🚀 Inicio Rápido

### Opción 1: Instalación Automática (Linux/macOS)

```bash
# Clonar el repositorio
git clone <tu-repositorio>
cd discord-reclutador

# Ejecutar instalación automática
chmod +x install.sh
./install.sh

# Editar el archivo .env con tu token
nano .env

# Ejecutar el bot
python3 run_bot.py
```

### Opción 2: Instalación Manual

```bash
# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env
echo "DISCORD_TOKEN=tu_token_aqui" > .env

# Ejecutar
python3 run_bot.py
```

## 🐳 Despliegue con Docker

### Usando Docker Compose (Recomendado)

```bash
# Construir y ejecutar
docker-compose up -d

# Ver logs
docker-compose logs -f discord-bot

# Detener
docker-compose down
```

### Usando Docker directamente

```bash
# Construir imagen
docker build -t discord-recruitment-bot .

# Ejecutar contenedor
docker run -d \
  --name discord-bot \
  --env-file .env \
  -v $(pwd)/reclutador.db:/app/reclutador.db \
  discord-recruitment-bot
```

## 🖥️ Despliegue en VPS/Servidor

### Opción 1: Systemd (Linux)

```bash
# Copiar archivo de servicio
sudo cp discord-bot.service /etc/systemd/system/

# Editar rutas en el archivo de servicio
sudo nano /etc/systemd/system/discord-bot.service

# Recargar systemd
sudo systemctl daemon-reload

# Iniciar servicio
sudo systemctl start discord-bot

# Habilitar auto-inicio
sudo systemctl enable discord-bot

# Ver estado
sudo systemctl status discord-bot

# Ver logs
sudo journalctl -u discord-bot -f
```

### Opción 2: Screen/Tmux

```bash
# Instalar screen
sudo apt install screen

# Ejecutar en screen
screen -S discord-bot python3 run_bot.py

# Desconectar: Ctrl+A, D
# Reconectar: screen -r discord-bot
```

### Opción 3: PM2 (Node.js process manager)

```bash
# Instalar PM2
npm install -g pm2

# Ejecutar con PM2
pm2 start run_bot.py --name discord-bot --interpreter python3

# Ver estado
pm2 status

# Ver logs
pm2 logs discord-bot

# Reiniciar
pm2 restart discord-bot
```

## ☁️ Plataformas de Hosting Recomendadas

### Para principiantes:
- **Railway**: Fácil setup, gratuito para bots pequeños
- **Render**: Gratuito con PostgreSQL incluido
- **Fly.io**: Buen rendimiento, gratuito básico

### Para uso profesional:
- **DigitalOcean Droplet**: $6/mes, control total
- **Linode VPS**: Desde $5/mes
- **AWS EC2**: Escalabilidad, pero más complejo
- **Google Cloud Run**: Serverless, pago por uso

### Configuración específica:

#### Railway (Recomendado para principiantes)
```bash
# railway.json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python run_bot.py"
  }
}
```

#### Render
```yaml
# render.yaml
services:
  - type: web
    name: discord-bot
    env: python3
    buildCommand: pip install -r requirements.txt
    startCommand: python run_bot.py
    envVars:
      - key: DISCORD_TOKEN
        sync: false
```

## 📊 Monitoreo y Logs

### Archivos de log generados:
- `bot.log` - Logs del bot
- `bot_runner.log` - Logs del script de reinicio
- `reclutador.db` - Base de datos SQLite

### Comandos útiles:

```bash
# Ver logs en tiempo real
tail -f bot.log

# Ver logs del runner
tail -f bot_runner.log

# Buscar errores
grep "ERROR" bot.log

# Ver tamaño de base de datos
ls -lh reclutador.db
```

## ☁️ Despliegue en Render (24/7 Gratis)

### ¿Por qué Render?
- ✅ **Gratis**: 750 horas/mes en el plan free
- ✅ **Automático**: Despliegue desde Git
- ✅ **Escalable**: Actualizaciones automáticas
- ✅ **Monitoreo**: Health checks integrados
- ✅ **24/7**: Sin interrupciones

### Pasos para Desplegar

1. **Preparar Repositorio**
   ```bash
   # Asegúrate de tener todos los archivos
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Crear Servicio en Render**
   - Ve a [render.com](https://render.com)
   - Conecta tu repositorio Git
   - Crea un "Web Service" con Python 3

3. **Configurar Variables**
   - **DISCORD_TOKEN**: Tu token de bot (marcar como secreto)
   - El resto se configura automáticamente

4. **¡Listo!**
   - Tu bot estará ejecutándose 24/7
   - Monitorea logs en tiempo real
   - Health checks automáticos

### Ver Detalles
📖 Consulta `RENDER_DEPLOYMENT.md` para instrucciones detalladas.

## 🔧 Configuración Avanzada

### Variables de Entorno

```bash
# .env
DISCORD_TOKEN=tu_token_aqui
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
DB_PATH=./reclutador.db
```

### Configuración del Bot

```python
# En bot.py
intents = discord.Intents.default()
intents.members = True  # Necesario para ver miembros
intents.message_content = True  # Para comandos con prefijo
```

## 🛠️ Comandos Disponibles

- `/nuevo_miembro` - Registrar nuevo reclutado
- `/agregar_actividad` - Agregar actividad a reclutado
- `/ver_reclutador` - Ver estadísticas personales
- `/ver_reclutado` - Ver detalles de un reclutado
- `/ver_staff` - Ver todos los reclutadores con rol específico
- `/listar_roles` - Listar todos los roles del servidor

## 🔒 Seguridad

- ✅ Token almacenado en variables de entorno
- ✅ Base de datos con permisos restringidos
- ✅ Logging sin información sensible
- ✅ Reinicio automático en caso de errores

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs: `tail -f bot.log`
2. Verifica la conexión a Discord
3. Confirma que el token es válido
4. Revisa los permisos del bot en Discord

## 📝 Notas Importantes

- El bot requiere permisos de "Server Members Intent" en el portal de Discord
- La base de datos SQLite se crea automáticamente
- El bot se reconecta automáticamente si pierde conexión
- Los logs se rotan automáticamente para evitar archivos muy grandes

---

**¡Tu bot está listo para funcionar 24/7!** 🎉