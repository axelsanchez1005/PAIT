class Equipo:
    def __init__(self, id, nombre, idea, id_lider, id_mentor=None, nombre_lider=None, nombre_mentor=None):
        self.id = id
        self.nombre = nombre
        self.idea = idea
        self.id_lider = id_lider
        self.id_mentor = id_mentor
        self.nombre_lider = nombre_lider
        self.nombre_mentor = nombre_mentor