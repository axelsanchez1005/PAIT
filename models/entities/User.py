from werkzeug.security import check_password_hash

class User:
    def __init__(self, id, codigo, nombre, password, rol, correo=None, celular=None):
        self.id = id
        self.codigo = codigo
        self.nombre = nombre
        self.password = password
        self.rol = rol
        self.correo = correo
        self.celular = celular

    @classmethod
    def check_password(self, hashed_password, password, rol):
        # Si es alumno y la contraseña es la general
        if rol == 'U' and password == 'polimatute':
            return True
        # En cualquier otro caso, verificar el hash
        return check_password_hash(hashed_password, password)