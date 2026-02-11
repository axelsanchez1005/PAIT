from .entities.Equipo import Equipo

class ModelEquipo:
    @classmethod
    def obtener_todos(cls, db):
        try:
            cursor = db.connection.cursor()
            # Hacemos JOIN con usuarios para traer los nombres del líder y mentor de una vez
            sql = """
                SELECT e.id, e.nombre, e.idea, e.id_lider, e.id_mentor, 
                       u_lider.nombre as nombre_lider, u_mentor.nombre as nombre_mentor
                FROM equipos e
                JOIN usuarios u_lider ON e.id_lider = u_lider.id
                LEFT JOIN usuarios u_mentor ON e.id_mentor = u_mentor.id
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            
            equipos = []
            for row in rows:
                # Creamos el objeto entidad para cada fila
                eq = Equipo(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
                equipos.append(eq)
            return equipos
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def crear_equipo(cls, db, id_lider, idea):
        cursor = db.connection.cursor()
        
        # 1. Autogenerar nombre: PAIT - Equipo X
        cursor.execute("SELECT COUNT(*) FROM equipos")
        proximo_numero = cursor.fetchone()[0] + 1
        nombre = f"PAIT - Equipo {proximo_numero}"

        # 2. Insertar equipo
        cursor.execute("INSERT INTO equipos (nombre, idea, id_lider) VALUES (%s, %s, %s)", 
                       (nombre, idea, id_lider))
        id_equipo = cursor.lastrowid

        # 3. Líder se une como primer miembro
        cursor.execute("INSERT INTO miembros_equipo (id_equipo, id_usuario) VALUES (%s, %s)", 
                       (id_equipo, id_lider))
        db.connection.commit()
        return id_equipo

    @classmethod
    def puede_unirse(cls, db, id_equipo, id_usuario):
        cursor = db.connection.cursor()
        
        # Regla 1: Máximo 5 alumnos
        cursor.execute("SELECT COUNT(*) FROM miembros_equipo WHERE id_equipo = %s", [id_equipo])
        if cursor.fetchone()[0] >= 5: return False, "El equipo está lleno."

        # Regla 2: Máximo 3 de la misma carrera
        cursor.execute("SELECT carrera FROM usuarios WHERE id = %s", [id_usuario])
        carrera_aspirante = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM usuarios u 
            JOIN miembros_equipo me ON u.id = me.id_usuario 
            WHERE me.id_equipo = %s AND u.carrera = %s
        """, (id_equipo, carrera_aspirante))
        
        if cursor.fetchone()[0] >= 3:
            return False, f"Ya hay 3 miembros de la carrera {carrera_aspirante}."
            
        return True, "OK"

    @classmethod
    def obtener_por_id(cls, db, id):
        cursor = db.connection.cursor()
        # Verifica que el orden coincida con tu __init__ de la clase Equipo
        sql = "SELECT id, nombre, idea, id_lider, id_mentor, link_whatsapp FROM equipos WHERE id = %s"
        cursor.execute(sql, (id,))
        row = cursor.fetchone()
        if row:
            # Si tu constructor es (id, nombre, idea, id_lider, id_mentor, link)
            return Equipo(row[0], row[1], row[2], row[3], row[4], row[5])
        return None

    @classmethod
    def obtener_miembros(cls, db, id_equipo):
        cursor = db.connection.cursor()
        # Filtramos por rol 'U' para traer solo alumnos
        sql = """
            SELECT u.id, u.codigo, u.nombre, u.password, u.rol 
            FROM usuarios u
            JOIN miembros_equipo me ON u.id = me.id_usuario
            WHERE me.id_equipo = %s AND u.rol = 'U'
        """
        cursor.execute(sql, [id_equipo])
        rows = cursor.fetchall()
        from .entities.User import User
        return [User(r[0], r[1], r[2], r[3], r[4]) for r in rows]


    @classmethod
    def obtener_equipo_usuario(cls, db, id_usuario):
        try:
            cursor = db.connection.cursor()
            # Buscamos si el usuario aparece en la tabla de miembros de cualquier equipo
            sql = """
                SELECT e.id, e.nombre, e.idea, e.id_lider
                FROM equipos e
                JOIN miembros_equipo me ON e.id = me.id_equipo
                WHERE me.id_usuario = %s
            """
            cursor.execute(sql, [id_usuario])
            row = cursor.fetchone()
            if row:
                return Equipo(row[0], row[1], row[2], row[3])
            return None
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def obtener_invitaciones_usuario(cls, db, id_usuario):
        cur = db.connection.cursor()
        # Esta consulta trae:
        # 1. Invitaciones donde YO soy el receptor (alguien me invitó)
        # 2. Solicitudes donde YO soy el emisor (yo pedí unirme)
        sql = """
            SELECT 
                i.id, 
                i.id_receptor, 
                i.id_emisor, 
                i.estado, 
                e.nombre AS nombre_equipo, 
                u.nombre as nombre_persona
            FROM invitaciones i
            JOIN equipos e ON i.id_equipo = e.id
            JOIN usuarios u ON (CASE WHEN i.id_receptor = %s THEN i.id_emisor ELSE i.id_receptor END) = u.id
            WHERE (i.id_receptor = %s OR i.id_emisor = %s) AND i.estado = 'PENDIENTE'
        """
        cur.execute(sql, (id_usuario, id_usuario, id_usuario))
        
        # Para que el modal reconozca los nombres de las columnas:
        columns = [column[0] for column in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]

    @classmethod
    def responder_invitacion(cls, db, id_invitacion, accion, id_usuario):
        cursor = db.connection.cursor()
        
        # 1. Obtener datos de la invitación
        cursor.execute("SELECT id_equipo, id_receptor, tipo FROM invitaciones WHERE id = %s", [id_invitacion])
        inv = cursor.fetchone()
        if not inv: return False, "Invitación no encontrada."
        
        id_equipo, id_receptor, tipo = inv

        if accion == 'ACEPTAR':
            # Validar reglas antes de unir
            puede, mensaje = cls.puede_unirse(db, id_equipo, id_receptor)
            if not puede: return False, mensaje

            # Unir al equipo
            cursor.execute("INSERT INTO miembros_equipo (id_equipo, id_usuario) VALUES (%s, %s)", (id_equipo, id_receptor))
            cursor.execute("UPDATE invitaciones SET estado = 'ACEPTADA' WHERE id = %s", [id_invitacion])
            
            # (Opcional) Rechazar automáticamente otras invitaciones pendientes del alumno
            cursor.execute("UPDATE invitaciones SET estado = 'RECHAZADA' WHERE id_receptor = %s AND estado = 'PENDIENTE'", [id_receptor])
            
        else:
            cursor.execute("UPDATE invitaciones SET estado = 'RECHAZADA' WHERE id = %s", [id_invitacion])

        db.connection.commit()
        return True, "Operación realizada con éxito."

    @classmethod
    def obtener_equipos_mentor(cls, db, id_mentor):
        try:
            cursor = db.connection.cursor()
            # Buscamos equipos donde el ID del mentor coincida
            sql = """
                SELECT e.id, e.nombre, e.idea, e.id_lider, u.nombre as nombre_lider
                FROM equipos e
                JOIN usuarios u ON e.id_lider = u.id
                WHERE e.id_mentor = %s
            """
            cursor.execute(sql, [id_mentor])
            rows = cursor.fetchall()
            
            equipos = []
            for row in rows:
                eq = Equipo(row[0], row[1], row[2], row[3], id_mentor, nombre_lider=row[4])
                equipos.append(eq)
            return equipos
        except Exception as ex:
            raise Exception(ex)
            
    @classmethod
    def asignar_mentor(cls, db, id_equipo, id_mentor):
        try:
            cursor = db.connection.cursor()
            
            # 1. (Opcional) Si quieres que el mentor solo tenga UN equipo:
            # cursor.execute("UPDATE equipos SET id_mentor = NULL WHERE id_mentor = %s", (id_mentor,))
            
            # 2. Asignar al nuevo equipo
            sql = "UPDATE equipos SET id_mentor = %s WHERE id = %s"
            cursor.execute(sql, (id_mentor, id_equipo))
            
            db.connection.commit()
            return True
        except Exception as ex:
            print(f"Error en el modelo: {ex}")
            return False  

@classmethod
def cambiar_lider(cls, db, id_equipo, id_nuevo_lider):
    try:
        cursor = db.connection.cursor()
        # Solo actualizamos la columna id_lider en la tabla equipos
        sql = "UPDATE equipos SET id_lider = %s WHERE id = %s"
        cursor.execute(sql, (id_nuevo_lider, id_equipo))
        db.connection.commit()
        return True
    except Exception as ex:
        print(f"Error al cambiar líder: {ex}")
        return False