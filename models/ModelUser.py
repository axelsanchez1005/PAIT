from .entities.User import User

class ModelUser:
    @classmethod
    def login(cls, db, codigo, password):
        try:
            cursor = db.connection.cursor()
            # Buscamos en la tabla unificada por código
            sql = "SELECT id, codigo, nombre, password, rol, correo, celular FROM usuarios WHERE codigo = %s"
            cursor.execute(sql, (codigo,))
            rows = cursor.fetchall()

            for row in rows:
                # Instanciamos la entidad para usar su método de verificación
                user_entity = User(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
                if User.check_password(user_entity.password, password, user_entity.rol):
                    return user_entity
            return None
        except Exception as ex:
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
    def obtener_disponibles(cls, db, carrera=None, grado=None, id_excluir=None):
        try:
            cursor = db.connection.cursor()
            # Consulta base: Alumnos (rol 'U') que no están en la tabla miembros_equipo
            sql = """
                SELECT id, codigo, nombre, correo, celular, carrera, grado, presentacion 
                FROM usuarios 
                WHERE rol = 'U' 
                AND id NOT IN (SELECT id_usuario FROM miembros_equipo)
            """
            params = []

            # Filtros dinámicos
            if carrera:
                sql += " AND carrera = %s"
                params.append(carrera)
            if grado:
                sql += " AND grado = %s"
                params.append(grado)
            
            # Evitar que el emisor se vea a sí mismo (por si acaso)
            if id_excluir:
                sql += " AND id != %s"
                params.append(id_excluir)

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            alumnos = []
            for r in rows:
                # Usamos la entidad User (id, codigo, nombre, password, rol, correo, celular)
                # Agregamos la presentación/bio como atributo extra si tu entidad lo permite
                u = User(r[0], r[1], r[2], None, 'U', r[3], r[4])
                u.carrera = r[5]
                u.grado = r[6]
                u.presentacion = r[7]
                alumnos.append(u)
            return alumnos
        except Exception as ex:
            raise Exception(ex)