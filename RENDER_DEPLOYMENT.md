# 🚀 Despliegue en Render

## Pasos para desplegar tu bot en Render

### 1. Preparar el repositorio
Asegúrate de que todos los archivos estén en tu repositorio Git:
- `bot.py`
- `database.py`
- `run_bot.py`
- `render_config.py`
- `render.yaml`
- `requirements.txt`
- `.env` (opcional, no subir el token)

### 2. Crear cuenta en Render
1. Ve a [render.com](https://render.com)
2. Crea una cuenta gratuita
3. Conecta tu repositorio Git (GitHub/GitLab/Bitbucket)

### 3. Crear el servicio web
1. En el dashboard de Render, haz clic en "New" → "Web Service"
2. Conecta tu repositorio
3. Configura el servicio:
   - **Name**: `discord-reclutador-bot` (o el nombre que prefieras)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python render_config.py && python run_bot.py`

### 4. Configurar variables de entorno
En la sección "Environment" del servicio, agrega:
- **DISCORD_TOKEN**: Tu token de Discord Bot (marcar como "Secret")

### 5. Configurar health checks
- **Health Check Path**: `/health`
- El health check se ejecutará automáticamente cada 30 segundos

### 6. Desplegar
1. Haz clic en "Create Web Service"
2. Espera a que se complete el build (puede tomar 5-10 minutos)
3. Una vez desplegado, tu bot estará ejecutándose 24/7

### 7. Monitoreo
- Revisa los logs en tiempo real en la pestaña "Logs"
- El health check te mostrará el estado del bot
- Si hay errores, Render reiniciará automáticamente el servicio

## Costos
- **Free tier**: 750 horas/mes, suficiente para un bot pequeño
- **Starter plan**: $7/mes para más recursos si necesitas

## Solución de problemas
- Si el bot no responde, verifica que el token sea correcto
- Revisa los logs para errores de conexión a Discord
- Asegúrate de que el bot tenga permisos en tu servidor de Discord

## URLs importantes
- Tu aplicación: `https://[tu-servicio].onrender.com`
- Health check: `https://[tu-servicio].onrender.com/health`