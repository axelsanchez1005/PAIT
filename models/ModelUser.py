from .entities.User import User
from werkzeug.security import generate_password_hash

class ModelUser:
    @classmethod
    def login(cls, db, codigo, password):
        try:
            cursor = db.connection.cursor()
            # Buscamos al usuario por su código
            sql = "SELECT id, codigo, nombre, password, rol, correo, celular FROM usuarios WHERE codigo = %s"
            cursor.execute(sql, (codigo,))
            row = cursor.fetchone() # Usamos fetchone porque el código debe ser único

            if row:
                # Creamos la entidad usuario
                user_entity = User(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
                clave_en_db = row[3] # La columna 'password' de tu tabla

                # 1. CASO ESPECIAL: Si la contraseña en la DB es texto plano 'polimatute'
                if clave_en_db == "polimatute":
                    if password == "polimatute":
                        # --- AUTO-CIFRADO ---
                        # Aprovechamos que entró para corregir su contraseña en la DB
                        nueva_clave_hash = generate_password_hash("polimatute")
                        cursor_update = db.connection.cursor()
                        sql_update = "UPDATE usuarios SET password = %s WHERE id = %s"
                        cursor_update.execute(sql_update, (nueva_clave_hash, user_entity.id))
                        db.connection.commit()
                        
                        return user_entity
                    else:
                        return None

                # 2. CASO NORMAL: Verificación por Hash (el que ya tenías)
                if User.check_password(user_entity.password, password, user_entity.rol):
                    return user_entity
                    
            return None
        except Exception as ex:
            print(f"Error en Login: {ex}")
            raise Exception(ex)

    @classmethod
    def update_data(cls, db, user_id, celular, correo):
        try:
            cursor = db.connection.cursor()
            sql = "UPDATE usuarios SET celular = %s, correo = %s WHERE id = %s"
            cursor.execute(sql, (celular, correo, user_id))
            db.connection.commit()
        except Exception as ex:
            raise Exception(ex)
        
    @classmethod
    def actualizar_password(cls, db, correo, nueva_clave_cifrada):
        try:
            print(f"Intentando actualizar a: {correo}") # <--- Mira tu consola negra
            cursor = db.connection.cursor()
            # Solo actualizamos la clave donde el correo coincida
            sql = "UPDATE usuarios SET password = %s WHERE correo = %s"
            cursor.execute(sql, (nueva_clave_cifrada, correo))
            db.connection.commit()
            return True
        except Exception as ex:
            print(f"Error en DB: {ex}")
            return False

    @classmethod
    def obtener_disponibles(cls, db, carrera=None, grado=None, id_excluir=None, nombre=None):
        try:
            cursor = db.connection.cursor()
            # 1. Consulta base: Alumnos (rol 'U') que NO están en ningún equipo
            sql = """
                SELECT id, codigo, nombre, correo, celular, carrera, grado, presentacion 
                FROM usuarios 
                WHERE rol = 'U' 
                AND id NOT IN (SELECT id_usuario FROM miembros_equipo)
            """
            params = []

            # 2. FILTRO POR NOMBRE (Búsqueda parcial e insensible a mayúsculas/minúsculas)
            if nombre and nombre.strip():
                sql += " AND nombre LIKE %s"
                params.append(f"%{nombre}%")

            # 3. FILTRO POR CARRERA
            if carrera:
                sql += " AND carrera = %s"
                params.append(carrera)
            
            # 4. FILTRO POR SEMESTRE (GRADO)
            if grado:
                sql += " AND grado = %s"
                params.append(grado)
            
            # 5. EXCLUIR AL EMISOR (Seguridad)
            if id_excluir:
                sql += " AND id != %s"
                params.append(id_excluir)

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            alumnos = []
            for r in rows:
                # Mapeo a la entidad User
                u = User(r[0], r[1], r[2], None, 'U', r[3], r[4])
                u.carrera = r[5]
                u.grado = r[6]
                u.presentacion = r[7]
                alumnos.append(u)
                
            return alumnos
        except Exception as ex:
            print(f"Error en obtener_disponibles: {ex}")
            raise Exception(ex)