class Equipo:
    def __init__(self, id, nombre, idea, id_lider, id_mentor=None, 
                 nombre_lider=None, nombre_mentor=None, 
                 busca_carrera='Cualquiera', busca_grado=None, link_whatsapp=None):
        self.id = id
        self.nombre = nombre
        self.idea = idea
        self.id_lider = id_lider
        self.id_mentor = id_mentor
        self.nombre_lider = nombre_lider
        self.nombre_mentor = nombre_mentor
        self.busca_carrera = busca_carrera
        self.busca_grado = busca_grado
        self.link_whatsapp = link_whatsapp