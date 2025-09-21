import sqlite3
from datetime import datetime

def create_tables():
    conn = sqlite3.connect('reclutador.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS miembros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            etiqueta_miembro TEXT NOT NULL,
            etiqueta_reclutador TEXT NOT NULL,
            fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS actividades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_miembro INTEGER,
            detalle TEXT NOT NULL,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(id_miembro) REFERENCES miembros(id)
        )
    ''')
    
    # Nueva tabla para reclutadores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reclutadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            etiqueta_reclutador TEXT UNIQUE NOT NULL,
            ultimo_reclutamiento DATETIME,
            total_reclutados INTEGER DEFAULT 0,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def add_miembro(etiqueta_miembro, etiqueta_reclutador):
    conn = sqlite3.connect('reclutador.db')
    cursor = conn.cursor()
    
    # Agregar el miembro
    cursor.execute('INSERT INTO miembros (etiqueta_miembro, etiqueta_reclutador) VALUES (?, ?)', (etiqueta_miembro, etiqueta_reclutador))
    
    # Actualizar o crear registro del reclutador
    cursor.execute('''
        INSERT INTO reclutadores (etiqueta_reclutador, ultimo_reclutamiento, total_reclutados)
        VALUES (?, CURRENT_TIMESTAMP, 1)
        ON CONFLICT(etiqueta_reclutador) DO UPDATE SET
            ultimo_reclutamiento = CURRENT_TIMESTAMP,
            total_reclutados = total_reclutados + 1
    ''', (etiqueta_reclutador,))
    
    conn.commit()
    conn.close()

def add_actividad(id_miembro, detalle):
    conn = sqlite3.connect('reclutador.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO actividades (id_miembro, detalle) VALUES (?, ?)', (id_miembro, detalle))
    conn.commit()
    conn.close()

def get_miembro_by_etiqueta(etiqueta):
    conn = sqlite3.connect('reclutador.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, etiqueta_miembro, etiqueta_reclutador, fecha_registro FROM miembros WHERE etiqueta_miembro = ?', (etiqueta,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_reclutados_by_reclutador(etiqueta_reclutador):
    conn = sqlite3.connect('reclutador.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, etiqueta_miembro, fecha_registro FROM miembros WHERE etiqueta_reclutador = ?', (etiqueta_reclutador,))
    result = cursor.fetchall()
    conn.close()
    return result

def get_actividades_by_miembro(id_miembro):
    conn = sqlite3.connect('reclutador.db')
    cursor = conn.cursor()
    cursor.execute('SELECT detalle, fecha FROM actividades WHERE id_miembro = ? ORDER BY fecha', (id_miembro,))
    result = cursor.fetchall()
    conn.close()
    return result

def count_actividades_by_miembro(id_miembro):
    conn = sqlite3.connect('reclutador.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM actividades WHERE id_miembro = ?', (id_miembro,))
    result = cursor.fetchone()[0]
    conn.close()
    return result

def delete_miembro(etiqueta_miembro):
    """Elimina un miembro y todas sus actividades"""
    conn = sqlite3.connect('reclutador.db')
    cursor = conn.cursor()
    
    # Primero obtener el ID del miembro
    cursor.execute('SELECT id FROM miembros WHERE etiqueta_miembro = ?', (etiqueta_miembro,))
    miembro = cursor.fetchone()
    
    if miembro:
        id_miembro = miembro[0]
        # Eliminar actividades primero (por la foreign key)
        cursor.execute('DELETE FROM actividades WHERE id_miembro = ?', (id_miembro,))
        # Luego eliminar el miembro
        cursor.execute('DELETE FROM miembros WHERE id = ?', (id_miembro,))
        conn.commit()
        deleted = True
    else:
        deleted = False
    
    conn.close()
    return deleted

def clear_reclutador(etiqueta_reclutador):
    """Elimina todos los reclutados de un reclutador y sus actividades, pero mantiene el registro del reclutador"""
    conn = sqlite3.connect('reclutador.db')
    cursor = conn.cursor()
    
    # Obtener todos los IDs de miembros del reclutador
    cursor.execute('SELECT id FROM miembros WHERE etiqueta_reclutador = ?', (etiqueta_reclutador,))
    miembros = cursor.fetchall()
    
    deleted_count = 0
    for miembro in miembros:
        id_miembro = miembro[0]
        # Eliminar actividades
        cursor.execute('DELETE FROM actividades WHERE id_miembro = ?', (id_miembro,))
        # Eliminar miembro
        cursor.execute('DELETE FROM miembros WHERE id = ?', (id_miembro,))
        deleted_count += 1
    
    # Resetear el conteo de reclutados activos del reclutador (mantener el registro y última fecha)
    cursor.execute('''
        UPDATE reclutadores 
        SET total_reclutados = 0 
        WHERE etiqueta_reclutador = ?
    ''', (etiqueta_reclutador,))
    
    conn.commit()
    conn.close()
    return deleted_count

def get_reclutadores_with_count():
    """Obtiene una lista de reclutadores únicos con el conteo de sus reclutados activos"""
    conn = sqlite3.connect('reclutador.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT etiqueta_reclutador, COUNT(*) as reclutados_activos
        FROM miembros 
        GROUP BY etiqueta_reclutador
        ORDER BY etiqueta_reclutador
    ''')
    
    reclutadores = cursor.fetchall()
    conn.close()
    
    return reclutadores

def get_all_reclutadores_with_count():
    """Obtiene TODOS los reclutadores con su conteo actual de reclutados activos"""
    conn = sqlite3.connect('reclutador.db')
    cursor = conn.cursor()
    
    # Obtener todos los reclutadores únicos con su conteo actual
    cursor.execute('''
        SELECT r.etiqueta_reclutador, COUNT(m.id) as reclutados_activos
        FROM reclutadores r
        LEFT JOIN miembros m ON r.etiqueta_reclutador = m.etiqueta_reclutador
        GROUP BY r.etiqueta_reclutador
        ORDER BY r.etiqueta_reclutador
    ''')
    
    reclutadores = cursor.fetchall()
    conn.close()
    
    return reclutadores

def get_reclutadores_last_activity():
    """Obtiene la última fecha de actividad para cada reclutador desde la tabla reclutadores"""
    conn = sqlite3.connect('reclutador.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT etiqueta_reclutador, ultimo_reclutamiento
        FROM reclutadores
        WHERE ultimo_reclutamiento IS NOT NULL
        ORDER BY etiqueta_reclutador
    ''')
    
    actividades = cursor.fetchall()
    conn.close()
    
    return actividades

def get_reclutadores_stats():
    """Obtiene estadísticas completas de los reclutadores"""
    conn = sqlite3.connect('reclutador.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            r.etiqueta_reclutador,
            COUNT(m.id) as reclutados_activos,
            r.total_reclutados as total_historico,
            r.ultimo_reclutamiento,
            r.fecha_creacion
        FROM reclutadores r
        LEFT JOIN miembros m ON r.etiqueta_reclutador = m.etiqueta_reclutador
        GROUP BY r.etiqueta_reclutador, r.total_reclutados, r.ultimo_reclutamiento, r.fecha_creacion
        ORDER BY r.etiqueta_reclutador
    ''')
    
    stats = cursor.fetchall()
    conn.close()
    
    return stats

def initialize_reclutadores_table():
    """Inicializa la tabla de reclutadores con datos existentes de la tabla miembros"""
    conn = sqlite3.connect('reclutador.db')
    cursor = conn.cursor()
    
    # Obtener todos los reclutadores existentes con sus estadísticas
    cursor.execute('''
        SELECT 
            etiqueta_reclutador,
            COUNT(*) as total_reclutados,
            MAX(fecha_registro) as ultimo_reclutamiento,
            MIN(fecha_registro) as fecha_creacion
        FROM miembros
        GROUP BY etiqueta_reclutador
    ''')
    
    reclutadores_existentes = cursor.fetchall()
    
    # Insertar o actualizar cada reclutador
    for etiqueta, total, ultimo, creacion in reclutadores_existentes:
        cursor.execute('''
            INSERT INTO reclutadores (etiqueta_reclutador, ultimo_reclutamiento, total_reclutados, fecha_creacion)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(etiqueta_reclutador) DO UPDATE SET
                ultimo_reclutamiento = CASE 
                    WHEN ultimo_reclutamiento IS NULL OR ultimo_reclutamiento < ? 
                    THEN ? ELSE ultimo_reclutamiento END,
                total_reclutados = CASE 
                    WHEN total_reclutados < ? 
                    THEN ? ELSE total_reclutados END
        ''', (etiqueta, ultimo, total, creacion, ultimo, ultimo, total, total))
    
    conn.commit()
    conn.close()