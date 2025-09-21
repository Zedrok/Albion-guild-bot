import discord
from discord import app_commands
from discord.ext import commands
import os
import sqlite3
from dotenv import load_dotenv
from database import create_tables, add_miembro, add_actividad, get_miembro_by_etiqueta, get_reclutados_by_reclutador, get_actividades_by_miembro, count_actividades_by_miembro, delete_miembro, clear_reclutador, get_reclutadores_with_count, get_all_reclutadores_with_count, get_reclutadores_last_activity, get_reclutadores_stats, initialize_reclutadores_table
import logging
import sys
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('discord_bot')

load_dotenv()

# Función helper para obtener el nombre actual de un reclutado
def get_reclutado_display_name(etiqueta_guardada, guild):
    """Intenta obtener el nickname actual del reclutado, si no está disponible usa la etiqueta guardada"""
    try:
        # Buscar el miembro en el servidor por diferentes métodos
        for member in guild.members:
            member_str = str(member)  # Formato completo: Usuario#1234 o @usuario
            
            # Comparar etiqueta completa
            if member_str == etiqueta_guardada:
                # Si tiene un nickname diferente al username, mostrar ambos
                if member.display_name != member.name:
                    return f"{member.display_name} ({etiqueta_guardada})"
                else:
                    # Si no tiene nickname especial, mostrar solo el display_name
                    return member.display_name
            
            # También buscar por nombre de usuario si no tiene discriminador
            if member.name == etiqueta_guardada:
                if member.display_name != member.name:
                    return f"{member.display_name} ({etiqueta_guardada})"
                else:
                    return member.display_name
                    
            # Buscar por username si la etiqueta tiene formato Usuario#1234
            if '#' in etiqueta_guardada:
                username = etiqueta_guardada.split('#')[0]
                if member.name == username:
                    if member.display_name != member.name:
                        return f"{member.display_name} ({etiqueta_guardada})"
                    else:
                        return member.display_name
                        
    except Exception as e:
        print(f"Error obteniendo display name para {etiqueta_guardada}: {e}")
        pass
    return etiqueta_guardada

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Clases de UI para los componentes interactivos
class ReclutadorView(discord.ui.View):
    def __init__(self, reclutador_etiqueta, reclutados):
        super().__init__(timeout=300)  # 5 minutos de timeout
        self.reclutador_etiqueta = reclutador_etiqueta
        self.reclutados = reclutados

    @discord.ui.button(label="Limpiar Reclutador", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def clear_reclutador(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Deshabilitar el botón para evitar múltiples clics
        button.disabled = True
        await interaction.response.edit_message(view=self)
        
        # Ejecutar la limpieza
        deleted_count = clear_reclutador(self.reclutador_etiqueta)
        
        await interaction.followup.send(f"EXITO: Se eliminaron {deleted_count} reclutados y todas sus actividades del reclutador {self.reclutador_etiqueta}", ephemeral=True)

    @discord.ui.button(label="Eliminar Reclutado", style=discord.ButtonStyle.secondary, emoji="👤")
    async def delete_reclutado(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if not self.reclutados:
                await interaction.followup.send("No hay reclutados para eliminar", ephemeral=True)
                return
            
            # Deshabilitar el botón para evitar múltiples clics
            button.disabled = True
            await interaction.response.edit_message(view=self)
            
            # Crear opciones para el select menu
            options = []
            for rec in self.reclutados:
                id_miembro, etiqueta, fecha = rec
                count_act = count_actividades_by_miembro(id_miembro)
                label = f"{etiqueta[:25]}..." if len(etiqueta) > 25 else etiqueta
                description = f"Ingreso: {fecha}, Actividades: {count_act}"
                options.append(discord.SelectOption(
                    label=label,
                    description=description,
                    value=str(id_miembro)
                ))
            
            # Crear el select menu
            select = ReclutadoSelect(options, self.reclutador_etiqueta)
            view = discord.ui.View()
            view.add_item(select)
            
            await interaction.followup.send("Selecciona el reclutado que quieres eliminar:", view=view, ephemeral=True)
        except Exception as e:
            try:
                await interaction.followup.send(f"Error al procesar la solicitud: {str(e)}", ephemeral=True)
            except:
                # Si followup también falla, intentar con response
                await interaction.response.send_message(f"Error al procesar la solicitud: {str(e)}", ephemeral=True)

class ReclutadoSelect(discord.ui.Select):
    def __init__(self, options, reclutador_etiqueta):
        super().__init__(placeholder="Selecciona un reclutado...", options=options)
        self.reclutador_etiqueta = reclutador_etiqueta

    async def callback(self, interaction: discord.Interaction):
        try:
            # Defer para mantener la interacción viva
            await interaction.response.defer(ephemeral=True)

            # Obtener la información del reclutado seleccionado
            conn = sqlite3.connect('reclutador.db')
            cursor = conn.cursor()
            cursor.execute('SELECT etiqueta_miembro FROM miembros WHERE id = ?', (int(self.values[0]),))
            result = cursor.fetchone()
            conn.close()

            if result:
                etiqueta_miembro = result[0]
                # Eliminar el reclutado
                deleted = delete_miembro(etiqueta_miembro)

                if deleted:
                    await interaction.followup.send(f"EXITO: Reclutado {etiqueta_miembro} y todas sus actividades han sido eliminados", ephemeral=True)
                else:
                    await interaction.followup.send("ERROR: No se pudo eliminar el reclutado", ephemeral=True)
            else:
                await interaction.followup.send("ERROR: Reclutado no encontrado", ephemeral=True)
        except Exception as e:
            # Log del error pero no intentar responder para evitar más errores
            logger.error(f"Error en eliminacion de reclutado: {e}")
            # No intentar followup aquí para evitar cascada de errores@bot.event
async def on_ready():
    logger.info(f'Bot conectado como {bot.user}')
    try:
        synced = await bot.tree.sync()
        logger.info(f'Sincronizados {len(synced)} comandos')
    except Exception as e:
        logger.error(f'Error sincronizando comandos: {e}')

@bot.event
async def on_disconnect():
    logger.warning('Bot desconectado de Discord')

@bot.event
async def on_resumed():
    logger.info('Bot reconectado a Discord')

@bot.event
async def on_error(event, *args, **kwargs):
    logger.error(f'Error en evento {event}: {args} {kwargs}')

@bot.tree.command(name='nuevo_miembro', description='Registra un nuevo miembro reclutado')
@app_commands.describe(miembro='Etiqueta del nuevo miembro', reclutador='Etiqueta del reclutador')
async def nuevo_miembro(interaction: discord.Interaction, miembro: discord.Member, reclutador: discord.Member):
    # Log del comando ejecutado
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_name = interaction.user.display_name
    print(f"[{timestamp}] {user_name} ejecutó comando: /nuevo_miembro")

    etiqueta_miembro = str(miembro)
    etiqueta_reclutador = str(reclutador)
    add_miembro(etiqueta_miembro, etiqueta_reclutador)
    await interaction.response.send_message(f'Nuevo miembro registrado: {etiqueta_miembro} por {etiqueta_reclutador}')

@bot.tree.command(name='agregar_actividad', description='Agrega una actividad a un reclutado')
@app_commands.describe(miembro='Etiqueta del reclutado', detalle='Detalle de la actividad')
async def agregar_actividad(interaction: discord.Interaction, miembro: discord.Member, detalle: str):
    # Log del comando ejecutado
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_name = interaction.user.display_name
    print(f"[{timestamp}] {user_name} ejecutó comando: /agregar_actividad")

    etiqueta_miembro = str(miembro)
    miembro_data = get_miembro_by_etiqueta(etiqueta_miembro)
    if miembro_data:
        add_actividad(miembro_data[0], detalle)
        await interaction.response.send_message(f'Actividad agregada a {etiqueta_miembro}: {detalle}')
    else:
        await interaction.response.send_message('Miembro no encontrado. Regístralo primero con /nuevo_miembro')

@bot.tree.command(name='ver_reclutador', description='Muestra estadísticas del reclutador')
@app_commands.describe(reclutador='Etiqueta del reclutador')
async def ver_reclutador(interaction: discord.Interaction, reclutador: discord.Member):
    # Log del comando ejecutado
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_name = interaction.user.display_name
    print(f"[{timestamp}] {user_name} ejecutó comando: /ver_reclutador")

    etiqueta_reclutador = str(reclutador)
    
    try:
        reclutados = get_reclutados_by_reclutador(etiqueta_reclutador)
        if reclutados:
            # Mostrar nickname actual y etiqueta guardada
            nickname_actual = reclutador.display_name
            mensaje = f'Reclutador: {nickname_actual}'
            if nickname_actual != reclutador.name:
                mensaje += f' ({etiqueta_reclutador})'
            mensaje += f'\nCantidad de reclutados: {len(reclutados)}\n\n'
            
            for rec in reclutados:
                id_miembro, etiqueta, fecha = rec
                count_act = count_actividades_by_miembro(id_miembro)
                
                # Obtener el nombre actual del reclutado
                nombre_actual = get_reclutado_display_name(etiqueta, interaction.guild)
                # Formatear fecha para mostrar solo el día
                fecha_formateada = fecha.split(' ')[0] if ' ' in fecha else fecha
                mensaje += f'- {nombre_actual}: Ingreso {fecha_formateada}, Actividades: {count_act}\n'
            
            # Verificar longitud del mensaje
            if len(mensaje) > 1900:
                mensaje = mensaje[:1900] + '\n\n[Mensaje truncado por límite de caracteres]'
            
            # Crear la vista con botones
            view = ReclutadorView(etiqueta_reclutador, reclutados)
            
            await interaction.response.send_message(mensaje, view=view)
        else:
            # Mostrar nickname actual incluso si no tiene reclutados
            nickname_actual = reclutador.display_name
            mensaje = f'Reclutador: {nickname_actual}'
            if nickname_actual != reclutador.name:
                mensaje += f' ({etiqueta_reclutador})'
            mensaje += '\nNo hay reclutados registrados para este reclutador'
            
            await interaction.response.send_message(mensaje)
            
    except Exception as e:
        # Solo intentar responder si no se ha respondido aún
        if not interaction.response.is_done():
            await interaction.response.send_message(f'Error al consultar datos: {str(e)}')

@bot.tree.command(name='ver_reclutado', description='Muestra detalles de un reclutado')
@app_commands.describe(miembro='Etiqueta del reclutado')
async def ver_reclutado(interaction: discord.Interaction, miembro: discord.Member):
    # Log del comando ejecutado
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_name = interaction.user.display_name
    print(f"[{timestamp}] {user_name} ejecutó comando: /ver_reclutado")

    etiqueta_miembro = str(miembro)
    
    try:
        miembro_data = get_miembro_by_etiqueta(etiqueta_miembro)
        if miembro_data:
            id_miembro, etiqueta_guardada, reclutador, fecha_ingreso = miembro_data
            actividades = get_actividades_by_miembro(id_miembro)
            count_act = len(actividades)
            
            # Mostrar nickname actual y etiqueta guardada
            nickname_actual = miembro.display_name
            mensaje = f'Reclutado: {nickname_actual}'
            if nickname_actual != miembro.name:
                mensaje += f' ({etiqueta_guardada})'
            # Formatear fecha para mostrar solo el día
            fecha_formateada = fecha_ingreso.split(' ')[0] if ' ' in fecha_ingreso else fecha_ingreso
            mensaje += f'\nFecha de ingreso: {fecha_formateada}\nCantidad de actividades: {count_act}\n\n'
            
            if actividades:
                mensaje += 'Actividades:\n'
                for act in actividades:
                    detalle, fecha = act
                    # Formatear fecha para mostrar solo el día
                    fecha_formateada = fecha.split(' ')[0] if ' ' in fecha else fecha
                    mensaje += f'- {fecha_formateada}: {detalle}\n'
            
            # Verificar longitud del mensaje (límite de Discord: 2000 caracteres)
            if len(mensaje) > 1900:  # Margen de seguridad
                mensaje = mensaje[:1900] + '\n\n[Mensaje truncado por límite de caracteres]'
            
            await interaction.response.send_message(mensaje)
        else:
            await interaction.response.send_message('Miembro no encontrado')
            
    except Exception as e:
        # Solo intentar responder si no se ha respondido aún
        if not interaction.response.is_done():
            await interaction.response.send_message(f'Error al consultar datos: {str(e)}')

@bot.tree.command(name='ver_staff', description='Ver todos los miembros con rol específico y sus reclutados activos')
async def ver_staff(interaction: discord.Interaction):
    # Log del comando ejecutado
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_name = interaction.user.display_name
    print(f"[{timestamp}] {user_name} ejecutó comando: /ver_staff")

    try:
        # ID del rol específico
        rol_id = 1404279446780772422
        
        # Buscar el rol por ID
        rol = interaction.guild.get_role(rol_id)
        
        if not rol:
            await interaction.response.send_message(f'Rol con ID {rol_id} no encontrado en este servidor')
            return
        
        # Obtener estadísticas completas de reclutadores
        reclutadores_stats = get_reclutadores_stats()
        
        # Crear diccionarios para búsqueda rápida
        stats_dict = {}
        for etiqueta, activos, total_historico, ultimo_reclutamiento, fecha_creacion in reclutadores_stats:
            stats_dict[etiqueta] = {
                'activos': activos,
                'total_historico': total_historico,
                'ultimo_reclutamiento': ultimo_reclutamiento,
                'fecha_creacion': fecha_creacion
            }
        
        # Obtener TODOS los miembros con el rol específico
        miembros_con_rol = []
        
        # Procesar todos los miembros del servidor que tienen el rol
        for member in interaction.guild.members:
            if rol in member.roles:
                # Buscar si este miembro es reclutador en la BD
                reclutados_activos = 0
                total_historico = 0
                ultima_actividad = 'Nunca'
                
                # Buscar por diferentes formatos de etiqueta
                posibles_etiquetas = [
                    str(member),  # Usuario#1234
                    member.name,  # Usuario
                    member.display_name  # Nickname
                ]
                
                for etiqueta in posibles_etiquetas:
                    if etiqueta in stats_dict:
                        stats = stats_dict[etiqueta]
                        reclutados_activos = stats['activos']
                        total_historico = stats['total_historico']
                        ultima_actividad = stats['ultimo_reclutamiento'] or 'Nunca'
                        break
                
                # Agregar el miembro a la lista con toda la información
                miembros_con_rol.append((member, reclutados_activos, total_historico, ultima_actividad))
        
        if not miembros_con_rol:
            await interaction.response.send_message(f'No se encontraron miembros con el rol **{rol.name}**')
            return
        
        mensaje = f'**Miembros con rol {rol.name}:**\n\n'
        
        for member, reclutados_activos, total_historico, ultima_actividad in miembros_con_rol:
            # Obtener el display name
            display_name = member.display_name if member.display_name != member.name else member.name
            discord_nick = f'{member.name}'
            
            # Formatear fecha para mostrar solo el día
            if ultima_actividad != 'Nunca':
                ultima_actividad = ultima_actividad.split(' ')[0] if ' ' in ultima_actividad else ultima_actividad
            
            mensaje += f'{display_name} ({discord_nick}) - reclutados activos: {reclutados_activos} - total histórico: {total_historico} - última actividad: {ultima_actividad}\n'
        
        # Verificar longitud del mensaje (límite de Discord: 2000 caracteres)
        if len(mensaje) > 1900:  # Margen de seguridad
            mensaje = mensaje[:1900] + '\n\n[Mensaje truncado por límite de caracteres]'
        
        await interaction.response.send_message(mensaje)
        
    except ValueError:
        await interaction.response.send_message('El ID del rol debe ser un número válido')
    except Exception as e:
        if not interaction.response.is_done():
            await interaction.response.send_message(f'Error al consultar datos: {str(e)}')

@bot.tree.command(name='listar_roles', description='Lista todos los roles del servidor con sus IDs')
async def listar_roles(interaction: discord.Interaction):
    # Log del comando ejecutado
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_name = interaction.user.display_name
    print(f"[{timestamp}] {user_name} ejecutó comando: /listar_roles")

    try:
        if not interaction.guild:
            await interaction.response.send_message('Este comando solo funciona en un servidor')
            return
        
        mensaje = '**Lista de roles del servidor:**\n\n'
        
        for rol in interaction.guild.roles:
            # Excluir @everyone ya que no es útil para este caso
            if rol.name != '@everyone':
                mensaje += f'**{rol.name}** - ID: `{rol.id}`\n'
        
        mensaje += '\n*Usa el ID del rol que quieres consultar en el comando /ver_staff*'
        
        # Verificar longitud del mensaje (límite de Discord: 2000 caracteres)
        if len(mensaje) > 1900:
            mensaje = mensaje[:1900] + '\n\n[Mensaje truncado por límite de caracteres]'
        
        await interaction.response.send_message(mensaje)
        
    except Exception as e:
        if not interaction.response.is_done():
            await interaction.response.send_message(f'Error al listar roles: {str(e)}')

if __name__ == '__main__':
    create_tables()
    initialize_reclutadores_table()
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print('Por favor, configura la variable de entorno DISCORD_TOKEN con tu token de bot')