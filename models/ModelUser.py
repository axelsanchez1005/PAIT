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