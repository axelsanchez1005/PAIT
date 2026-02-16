from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect
from config import config
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash
from itsdangerous import URLSafeTimedSerializer
# Modelos
from models.ModelUser import ModelUser
from models.ModelEquipo import ModelEquipo


paitApp = Flask(__name__)
# Configuración Flask,para decirle quien es el proveedor de correos
paitApp.config['MAIL_SERVER'] = 'smtp.gmail.com'
paitApp.config['MAIL_PORT'] = 587
paitApp.config['MAIL_USE_TLS'] = True
paitApp.config['MAIL_USERNAME'] = 'proyectospaitoficial@gmail.com' #bspz lvwj cltp uces
paitApp.config['MAIL_PASSWORD'] = 'yqyoovwtnxbapocf' # Clave especial de Google
mail = Mail(paitApp) # Inicializamos el motor
# Resto de la configuración de la app
paitApp.config['SECRET_KEY'] = 'Cl4v3Sup3rm3g4S3gur4PAIT2026!'
generador = URLSafeTimedSerializer(paitApp.config['SECRET_KEY'])
csrf = CSRFProtect(paitApp) # Protección CSRF Global
db = MySQL(paitApp)


@paitApp.route('/')
def index():
    return render_template('registro.html')

#---------------------------------------login-------------------------------------
@paitApp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return redirect(url_for('index'))
    
    codigo = request.form.get('codigo')
    password = request.form.get('password')

    if not codigo or not password:
        flash("Código y contraseña son requeridos", "warning")
        return redirect(url_for('index'))

    user_logged = ModelUser.login(db, codigo, password)
    if user_logged:
        try:
            cur = db.connection.cursor()
            # Suponiendo que tu columna se llama 'ultima_conexion'
            sql = "UPDATE usuarios SET ingreso = NOW() WHERE id = %s"
            cur.execute(sql, [user_logged.id])
            db.connection.commit()
            cur.close()
        except Exception as e:
            print(f"Error al registrar conexión: {e}")
            # No hacemos redirect aquí para que el usuario pueda entrar 
            # aunque falle el registro de la fecha

        session['user_id'] = user_logged.id # Guardamos el ID real de la DB
        session['codigo'] = user_logged.codigo
        session['rol'] = user_logged.rol
        session['nombre'] = user_logged.nombre
        
        session['datos_completos'] = bool(user_logged.correo and user_logged.celular)

        #Identificar Roles
        if user_logged.rol == 'A':
            return redirect(url_for('dashboard_admin'))
        elif user_logged.rol == 'M':
            return redirect(url_for('dashboard_mentor'))
        else:
            return redirect(url_for('dashboard_alumno'))
    
    flash("Código o contraseña incorrectos.", "danger")
    return redirect(url_for('index'))

#-----------------------------------SingOut---------------------------------------
@paitApp.route('/signout', methods=['GET'])
def signout():
    session.clear()
    return redirect(url_for('index'))

#-------------------Actualización de datos (celular y correo)---------------------
@paitApp.route('/actualizar_perfil', methods=['POST'])
def actualizar_perfil():
    if 'user_id' not in session: return redirect(url_for('index'))
    
    id_user = session['user_id']
    celular = request.form.get('celular').strip()
    correo = request.form.get('correo').lower().strip()
    presentacion = request.form.get('presentacion', '')

    # 1. Definimos el dominio obligatorio
    DOMINIO_ESCUELA = "@alumnos.udg.mx"

    # 2. VALIDACIÓN ESTRICTA
    if not correo.endswith(DOMINIO_ESCUELA):
        flash(f"Error: El correo que debes utilizar es el institucional ({DOMINIO_ESCUELA}).", "danger")
        return redirect(url_for('dashboard_alumno'))

    # VALIDACIÓN DE CELULAR: ¿Son 10 caracteres y son todos números?
    if not (len(celular) == 10 and celular.isdigit()):
        flash("Error: El número de celular debe tener exactamente 10 dígitos numéricos.", "danger")
        return redirect(url_for('dashboard_alumno'))
    
    if len(presentacion) > 200:
        flash("Error: La presentación no puede exceder los 200 caracteres.", "danger")
        return redirect(url_for('dashboard_alumno'))
    
    try:
        cur = db.connection.cursor()
        cur.execute("""
            UPDATE usuarios 
            SET celular = %s, correo = %s, presentacion = %s 
            WHERE id = %s
        """, (celular, correo, presentacion, id_user))
        db.connection.commit()
        
        session['datos_completos'] = True # Actualizamos sesión
        flash("Perfil actualizado con éxito", "success")
        return redirect(url_for('dashboard_alumno'))
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('dashboard_alumno'))

# ---- ------------------------------Dashboards --------------------------------
@paitApp.route('/dashboard_alumno')
def dashboard_alumno():
    if 'user_id' not in session: return redirect(url_for('index'))
    id_u = session['user_id']
    # 1. Obtener el objeto equipo
    equipo_usuario = ModelEquipo.obtener_equipo_usuario(db, id_u)
    # 2. DEFINIR id_equipo (Aquí es donde estaba el fallo)
    id_equipo = equipo_usuario.id if equipo_usuario else None
    invitaciones = ModelEquipo.obtener_invitaciones_usuario(db, id_u)
    # 3. Consulta de Anuncios
    cur = db.connection.cursor()
    # Buscamos los datos actualizados del usuario, incluyendo la conexión
    cur.execute("SELECT id, nombre, correo, celular, presentacion, ingreso FROM usuarios WHERE id = %s", [id_u])
    # Usamos .fetchone() porque es un solo usuario. 
    # Para que sea fácil de usar, lo convertiremos en un diccionario.
    col_names = [desc[0] for desc in cur.description]
    ingreso = dict(zip(col_names, cur.fetchone()))
    sql = """
        SELECT a.id, a.contenido, a.fecha_publicacion, a.fijado, u.nombre, a.id_equipo, u.rol,
               (SELECT COUNT(*) FROM lecturas_anuncios la WHERE la.id_anuncio = a.id AND la.id_usuario = %s) as leido
        FROM anuncios a
        JOIN usuarios u ON a.id_usuario = u.id
        WHERE a.id_equipo IS NULL 
    """
    params = [id_u]
    
    if id_equipo:
        sql += " OR a.id_equipo = %s "
        params.append(id_equipo)
        
    sql += " ORDER BY a.fijado DESC, a.fecha_publicacion DESC"
    cur.execute(sql, params)
    todos_los_anuncios = cur.fetchall()
    # Tomamos los 3 principales para la tarjeta del dashboard
    anuncios_principales = todos_los_anuncios[:3]
    return render_template('dashboardAl.html', 
                           usuario=ingreso,
                           equipo_usuario=equipo_usuario, 
                           invitaciones=invitaciones,
                           anuncios_principales=anuncios_principales,
                           todos_los_anuncios=todos_los_anuncios)

@paitApp.route('/dashboard_mentor')
def dashboard_mentor():
    if 'user_id' not in session: return redirect(url_for('index'))
    id_u = session['user_id']
    
    # 1. Obtener equipos asignados al mentor
    equipos_mentor = ModelEquipo.obtener_equipos_mentor(db, id_u)
    tiene_equipos = len(equipos_mentor) > 0
    ids_equipos = [e.id for e in equipos_mentor]

    # 2. Consulta de Anuncios con estado de lectura
    cur = db.connection.cursor()
    # Traemos anuncios globales (NULL) o de sus equipos asignados
    sql = """
        SELECT a.id, a.contenido, a.fecha_publicacion, a.fijado, u.nombre, a.id_equipo, u.rol,
               (SELECT COUNT(*) FROM lecturas_anuncios la WHERE la.id_anuncio = a.id AND la.id_usuario = %s) as leido,
               e.nombre as nombre_equipo
        FROM anuncios a
        JOIN usuarios u ON a.id_usuario = u.id
        LEFT JOIN equipos e ON a.id_equipo = e.id
        WHERE a.id_equipo IS NULL 
    """
    params = [id_u]
    
    if ids_equipos:
        # Filtramos por todos los equipos que supervisa
        placeholders = ', '.join(['%s'] * len(ids_equipos))
        sql += f" OR a.id_equipo IN ({placeholders}) "
        params.extend(ids_equipos)
        
    sql += " ORDER BY a.fijado DESC, a.fecha_publicacion DESC"
    cur.execute(sql, params)
    
    todos_los_anuncios = cur.fetchall()
    anuncios_principales = todos_los_anuncios[:3]

    return render_template('dashboardMe.html', 
                           tiene_equipos=tiene_equipos,
                           anuncios_principales=anuncios_principales,
                           todos_los_anuncios=todos_los_anuncios)

@paitApp.route('/dashboard_admin')
def dashboard_admin():
    if 'user_id' not in session or session.get('rol') != 'A':
        return redirect(url_for('index'))
    
    return render_template('dashboardAd.html')



# Ruta para la página de recuperación de contraseña
@paitApp.route('/enviar_recuperacion', methods=['GET', 'POST'])
def enviar_recuperacion():
    # 1. Atrapamos el dato del formulario
    correo_usuario = request.form['email_usuario']

    token = generador.dumps(correo_usuario, salt='recuperar-password')

    # subject = Asunto, sender = Quien envía, recipients = Quien recibe (en lista [])
    msg = Message(subject="Recuperar Contraseña",
                  sender=paitApp.config['MAIL_USERNAME'],
                  recipients=[correo_usuario])
    
    link = url_for('restablecerClave', token=token, _external=True)
    # 3. Escribimos el cuerpo del mensaje
    msg.body = f"Hola! Para cambiar tu clave entra a este link: {link}"
    
    # 4. El acto de magia: enviar
    try:
        mail.send(msg)
        return render_template('enviodecorreo.html')
    except Exception as e:
        return f"Error al enviar: {str(e)}"

# Ruta para restablecer la contraseña
@paitApp.route('/restablecer/<token>', methods=['GET', 'POST'])
def restablecerClave(token):
    try:
        correo = generador.loads(token, salt='recuperar-password', max_age=300)
    except:
        return "<h1>El link es inválido o ya caducó.</h1>"

    if request.method == 'POST':
        nueva_clave = request.form['nueva_clave']
        confirmar = request.form['confirmar_clave']
        
        if nueva_clave == confirmar:
            # 1. Ciframos la nueva clave
            pass_hash = generate_password_hash(nueva_clave)           
            # 2. Llamamos al modelo (aquí necesitarás saber de quién es el token)
            ModelUser.actualizar_password(db, correo, pass_hash)
            
            flash("¡Contraseña actualizada!")
            return redirect(url_for('index'))
        else:
            flash("Las contraseñas no coinciden")
            
    return render_template('reestablecer.html', token=token)

# Ruta para abrir el formulario de recuperación de contraseña
@paitApp.route('/Recuperar')
def recuperar():
    return render_template('recuperar.html')



@paitApp.route('/equipos')
def lista_equipos():
    if 'user_id' not in session: return redirect(url_for('index'))
    id_u = session['user_id']
    
    # 1. Obtenemos tus datos (Carrera y Grado)
    cur = db.connection.cursor()
    cur.execute("SELECT carrera, grado FROM usuarios WHERE id = %s", [id_u])
    user_data = cur.fetchone()
    mi_carrera = user_data[0]
    mi_grado = user_data[1]

    # 2. Obtenemos todos los equipos
    todos = ModelEquipo.obtener_todos(db)
    
    recomendados = []
    otros = []

    for eq in todos:
        # Lógica de Matchmaking:
        # Prioridad 1: Carrera exacta
        # Prioridad 2: Carrera "Cualquiera" pero semestre exacto
        if eq.busca_carrera == mi_carrera:
            eq.match_type = "Carrera" # Etiqueta para el HTML
            recomendados.append(eq)
        elif eq.busca_carrera == 'Cualquiera' and eq.busca_grado == mi_grado:
            eq.match_type = "Semestre"
            recomendados.append(eq)
        else:
            otros.append(eq)

    return render_template('equipos.html', 
                           recomendados=recomendados, 
                           otros=otros,
                           mi_carrera=mi_carrera)

@paitApp.route('/crear_equipo', methods=['POST'])
def crear_equipo():
    if 'user_id' not in session: return redirect(url_for('index'))
    id_lider = session['user_id']
    idea = request.form.get('idea')
    # El modelo maneja el nombre "PAIT - Equipo X" automáticamente
    try:
        nuevo_id = ModelEquipo.crear_equipo(db, id_lider, idea)
        if nuevo_id:
            flash("Equipo creado con éxito. Ahora eres el jefe de equipo.", "success")
        return redirect(url_for('dashboard_alumno'))
    except Exception as e:
        flash(f"Error al crear equipo: {str(e)}", "danger")
        return redirect(url_for('dashboard_alumno'))

@paitApp.route('/api/equipo/<int:id>')
def api_equipo(id):
    # Esta ruta sirve los datos para el modal de "Unirse"
    equipo = ModelEquipo.obtener_por_id(db, id) # Deberás añadir este método en el modelo
    miembros = ModelEquipo.obtener_miembros(db, id) # Y este también
    return jsonify({
        "nombre": equipo.nombre,
        "idea": equipo.idea,
        "miembros": [m.nombre for m in miembros]
    })
#----------------------------Funcion para hacer solicitudes---------------------------------

@paitApp.route('/solicitar_unirse/<int:id_equipo>', methods=['POST'])
def solicitar_unirse(id_equipo):
    if 'user_id' not in session: return redirect(url_for('index'))
    id_usuario = session['user_id']
    # 1. VALIDACIÓN: ¿El usuario ya tiene equipo?
    if ModelEquipo.obtener_equipo_usuario(db, id_usuario):
        flash("Ya perteneces a un equipo. No puedes solicitar unirte a otro.", "warning")
        return redirect(url_for('lista_equipos'))
    # 2. Obtener quién es el líder de ese equipo para enviarle la solicitud
    cur = db.connection.cursor()
    cur.execute("SELECT id_lider FROM equipos WHERE id = %s", [id_equipo])
    equipo = cur.fetchone()
    # 3. Insertar la solicitud en la tabla de invitaciones 
    if equipo:
        id_lider = equipo[0]
        try:
            cur.execute("""
                INSERT INTO invitaciones (id_emisor, id_receptor, id_equipo, tipo, estado) 
                VALUES (%s, %s, %s, 'SOLICITAR', 'PENDIENTE')
            """, (id_usuario, id_lider, id_equipo))
            db.connection.commit()
            flash("Solicitud enviada correctamente.", "success")
        except Exception:
            flash("Ya tienes una solicitud pendiente con este equipo.", "warning")
            
    return redirect(url_for('lista_equipos'))

#-------------------------Funcion para cancelar las invitaciones----------------------------------

@paitApp.route('/cancelar_solicitud/<int:id_invitacion>', methods=['POST'])
def cancelar_solicitud(id_invitacion):
    if 'user_id' not in session: return redirect(url_for('index'))
    
    cur = db.connection.cursor()
    # Seguridad: Solo permitimos borrar si el usuario en sesión es el emisor
    cur.execute("DELETE FROM invitaciones WHERE id = %s AND id_emisor = %s", 
                (id_invitacion, session['user_id']))
    db.connection.commit()
    
    flash("Solicitud cancelada correctamente.", "info")
    return redirect(url_for('dashboard_alumno'))

#-------------------------Funcion para procesar a las invitaciones----------------------------------
@paitApp.route('/procesar_invitacion/<int:id_inv>/<string:accion>', methods=['POST'])
def procesar_invitacion(id_inv, accion):
    if 'user_id' not in session: return redirect(url_for('index'))
    
    cur = db.connection.cursor()
    
    # 1. Obtenemos los protagonistas de la invitación
    cur.execute("SELECT id_equipo, id_receptor, id_emisor, tipo FROM invitaciones WHERE id = %s", [id_inv])
    invitacion = cur.fetchone()
    
    if not invitacion:
        flash("Invitación no encontrada.", "danger")
        return redirect(url_for('dashboard_alumno'))
    
    id_equipo = invitacion[0]
    id_receptor = invitacion[1] # El que recibe (Líder en caso de SOLICITAR)
    id_emisor = invitacion[2]   # El que envía (Alumno en caso de SOLICITAR)
    tipo = invitacion[3]

    if accion == 'ACEPTAR':
        # 2. Lógica CORRECTA: 
        # Si el alumno pidió unirse (SOLICITAR), el que debe entrar al equipo es el EMISOR.
        # Si el líder invitó al alumno (INVITAR), el que debe entrar es el RECEPTOR.
        if tipo == 'SOLICITAR':
            alumno_a_unir = id_emisor
        else:
            alumno_a_unir = id_receptor
        
        try:
            # 3. Insertamos al ALUMNO, no al usuario que tiene la sesión abierta
            cur.execute("INSERT INTO miembros_equipo (id_usuario, id_equipo) VALUES (%s, %s)", 
                        (alumno_a_unir, id_equipo))
            
            # 4. Marcamos como aceptada
            cur.execute("UPDATE invitaciones SET estado = 'ACEPTADA' WHERE id = %s", [id_inv])
            
            # 5. Limpiamos otras solicitudes pendientes que tenga ese alumno
            cur.execute("UPDATE invitaciones SET estado = 'RECHAZADA' WHERE id_emisor = %s AND estado = 'PENDIENTE'", [alumno_a_unir])
            
            db.connection.commit()
            flash("Solicitud aceptada. El integrante ha sido añadido al equipo.", "success")
            
        except Exception as e:
            db.connection.rollback()
            # ESTO te dirá el error real en la página (solo para pruebas)
            flash(f"Error real de la DB: {str(e)}", "danger") 
            print(f"DEBUG: {e}")

    elif accion == 'RECHAZAR':
        cur.execute("UPDATE invitaciones SET estado = 'RECHAZADO' WHERE id = %s", [id_inv])
        db.connection.commit()
        flash("Solicitud rechazada.", "info")

    return redirect(url_for('dashboard_alumno'))
#--------------------------------------------TABLON ------------------------------------------------
@paitApp.route('/tablon/<int:id_equipo>')
def tablon(id_equipo):
    if 'user_id' not in session: return redirect(url_for('index'))
    id_usuario = session['user_id']
    
    equipo = ModelEquipo.obtener_por_id(db, id_equipo)
    if not equipo: return redirect(url_for('dashboard_alumno'))

    # 1. Traemos solo a los alumnos (el modelo ya los filtra por rol 'U')
    integrantes = ModelEquipo.obtener_miembros(db, id_equipo)
    total_miembros = len(integrantes) 

    # 2. Traemos al Mentor por separado usando el id_mentor de la tabla equipos
    mentor_obj = None
    if equipo.id_mentor:
        cur_m = db.connection.cursor()
        cur_m.execute("SELECT id, nombre, correo FROM usuarios WHERE id = %s", [equipo.id_mentor])
        m_data = cur_m.fetchone()
        if m_data:
            mentor_obj = {"id": m_data[0], "nombre": m_data[1], "correo": m_data[2]}

    es_mentor = (session.get('rol') == 'M' and equipo.id_mentor == id_usuario)
    es_lider = (equipo.id_lider == id_usuario)
    
    # 5. Obtener anuncios
    cur = db.connection.cursor()
    cur.execute("""
        SELECT a.id, a.contenido, a.fecha_publicacion, u.nombre, a.id_usuario, u.rol
        FROM anuncios a 
        JOIN usuarios u ON a.id_usuario = u.id 
        WHERE a.id_equipo = %s OR a.id_equipo IS NULL 
        ORDER BY a.fecha_publicacion DESC
    """, [id_equipo])
    anuncios = cur.fetchall()
    
    return render_template('tablon.html', 
                           equipo=equipo, 
                           anuncios=anuncios, 
                           integrantes=integrantes,
                           mentor_obj=mentor_obj,
                           total_miembros=total_miembros,
                           es_mentor=es_mentor,
                           es_lider=es_lider)

@paitApp.route('/eliminar_miembro/<int:id_equipo>/<int:id_usuario>', methods=['POST'])
def eliminar_miembro(id_equipo, id_usuario):
    # 1. Seguridad: Solo mentores pueden entrar aquí
    if 'user_id' not in session or session.get('rol') != 'M':
        flash("Acceso denegado.", "danger")
        return redirect(url_for('index'))

    id_mentor_sesion = session['user_id']
    cur = db.connection.cursor()

    # 2. Verificar que el mentor sea el dueño de este equipo
    cur.execute("SELECT id_lider, id_mentor FROM equipos WHERE id = %s", [id_equipo])
    equipo_data = cur.fetchone()

    if not equipo_data or equipo_data[1] != id_mentor_sesion:
        flash("No tienes autoridad sobre este equipo.", "danger")
        return redirect(url_for('dashboard_mentor'))

    try:
        # 3. Eliminar de la tabla de miembros
        cur.execute("DELETE FROM miembros_equipo WHERE id_equipo = %s AND id_usuario = %s", 
                    (id_equipo, id_usuario))

        # 4. Caso especial: Si el eliminado era el JEFE (id_lider)
        if equipo_data[0] == id_usuario:
            # Dejamos el liderazgo vacante para que el mentor asigne a otro después
            cur.execute("UPDATE equipos SET id_lider = NULL WHERE id = %s", [id_equipo])
            flash("Has eliminado al Jefe de Equipo. El cargo quedó vacante.", "warning")
        else:
            flash("Alumno eliminado del equipo correctamente.", "success")

        db.connection.commit()
    except Exception as e:
        db.connection.rollback()
        flash(f"Error al procesar la baja: {str(e)}", "danger")

    return redirect(url_for('tablon', id_equipo=id_equipo))

@paitApp.route('/asignar_lider/<int:id_equipo>/<int:id_usuario>', methods=['POST'])
def asignar_lider(id_equipo, id_usuario):
    if 'user_id' not in session: return redirect(url_for('index'))
    id_solicitante = session['user_id']
    cur = db.connection.cursor()
    
    # Obtenemos quién es el líder y el mentor actual del equipo
    cur.execute("SELECT id_lider, id_mentor FROM equipos WHERE id = %s", [id_equipo])
    equipo_data = cur.fetchone()

    if not equipo_data:
        flash("Equipo no encontrado.", "danger")
        return redirect(url_for('dashboard_alumno'))

    id_lider_actual = equipo_data[0]
    id_mentor_actual = equipo_data[1]

    # REGLA DE SEGURIDAD: Solo el Mentor O el Jefe actual pueden cambiar al líder
    if id_solicitante == id_lider_actual or id_solicitante == id_mentor_actual:
        if ModelEquipo.cambiar_lider(db, id_equipo, id_usuario):
            flash("Cambio de liderazgo realizado con éxito.", "success")
        else:
            flash("No se pudo procesar el cambio.", "danger")
    else:
        flash("No tienes permisos para designar a un nuevo jefe.", "danger")

    return redirect(url_for('tablon', id_equipo=id_equipo))

#FUNCIONES PARA LINK DE WASAP Y ANUNCIOS
@paitApp.route('/publicar_anuncio/<int:id_equipo>', methods=['POST'])
def publicar_anuncio(id_equipo):
    # Seguridad: Solo Mentores pueden publicar
    if session.get('rol') != 'M':
        flash("No tienes permiso para publicar anuncios.", "danger")
        return redirect(url_for('tablon', id_equipo=id_equipo))

    contenido = request.form.get('contenido')
    if contenido:
        cur = db.connection.cursor()
        cur.execute("""
            INSERT INTO anuncios (id_equipo, id_usuario, contenido) 
            VALUES (%s, %s, %s)
        """, (id_equipo, session['user_id'], contenido))
        db.connection.commit()
        flash("Anuncio publicado.", "success")
    
    return redirect(url_for('tablon', id_equipo=id_equipo))

@paitApp.route('/actualizar_link/<int:id_equipo>', methods=['POST'])
def actualizar_link(id_equipo):
    id_usuario = session['user_id']
    link = request.form.get('link_whatsapp')
    
    # Verificamos si es el Mentor o el Líder antes de actualizar
    cur = db.connection.cursor()
    cur.execute("SELECT id_lider, id_mentor FROM equipos WHERE id = %s", [id_equipo])
    equipo_data = cur.fetchone()
    
    if equipo_data and (id_usuario == equipo_data[0] or id_usuario == equipo_data[1]):
        cur.execute("UPDATE equipos SET link_whatsapp = %s WHERE id = %s", (link, id_equipo))
        db.connection.commit()
        flash("Link de comunicación actualizado.", "success")
    else:
        flash("No tienes permiso para modificar el link.", "danger")

    return redirect(url_for('tablon', id_equipo=id_equipo))



# --- RUTAS PARA GESTIÓN DE ANUNCIOS ---

# --- RUTAS PROTEGIDAS PARA GESTIÓN DE ANUNCIOS ---

@paitApp.route('/editar_anuncio/<int:id_anuncio>', methods=['POST'])
def editar_anuncio(id_anuncio):
    id_usuario_sesion = session.get('user_id')
    rol_sesion = session.get('rol')
    nuevo_contenido = request.form.get('contenido')
    
    cur = db.connection.cursor()
    # Obtenemos el id_equipo y el id_usuario (creador) del anuncio
    cur.execute("SELECT id_equipo, id_usuario FROM anuncios WHERE id = %s", [id_anuncio])
    anuncio_data = cur.fetchone() # anuncio_data[1] es el ID del creador
    
    if anuncio_data:
        # REGLA: Admin puede todo OR Mentor solo si es dueño
        if rol_sesion == 'A' or (rol_sesion == 'M' and anuncio_data[1] == id_usuario_sesion):
            cur.execute("UPDATE anuncios SET contenido = %s WHERE id = %s", (nuevo_contenido, id_anuncio))
            db.connection.commit()
            flash("Anuncio actualizado correctamente.", "success")
            return redirect(url_for('tablon', id_equipo=anuncio_data[0]))
    
    flash("No tienes permiso para editar este anuncio.", "danger")
    return redirect(url_for('dashboard_alumno'))

@paitApp.route('/eliminar_anuncio/<int:id_anuncio>', methods=['POST'])
def eliminar_anuncio(id_anuncio):
    id_usuario_sesion = session.get('user_id')
    rol_sesion = session.get('rol')
    
    cur = db.connection.cursor()
    cur.execute("SELECT id_equipo, id_usuario FROM anuncios WHERE id = %s", [id_anuncio])
    anuncio_data = cur.fetchone()
    
    if anuncio_data:
        if rol_sesion == 'A' or (rol_sesion == 'M' and anuncio_data[1] == id_usuario_sesion):
            cur.execute("DELETE FROM anuncios WHERE id = %s", [id_anuncio])
            db.connection.commit()
            flash("Anuncio eliminado.", "info")
            
            if anuncio_data[0] is None:
                return redirect(url_for('acciones_admin'))
            return redirect(url_for('tablon', id_equipo=anuncio_data[0]))
    
    flash("No tienes permiso para eliminar este anuncio.", "danger")
    return redirect(url_for('dashboard_alumno'))

@paitApp.route('/admin/publicar_anuncio_general', methods=['POST'])
def publicar_anuncio_general():
    if session.get('rol') != 'A': return redirect(url_for('index'))
    
    contenido = request.form.get('contenido')
    if contenido:
        cur = db.connection.cursor()
        # id_equipo = NULL significa que es un anuncio general para todos
        cur.execute("""
            INSERT INTO anuncios (id_equipo, id_usuario, contenido) 
            VALUES (NULL, %s, %s)
        """, (session['user_id'], contenido))
        db.connection.commit()
        flash("Anuncio general publicado con éxito.", "success")
    
    return redirect(url_for('acciones_admin'))

@paitApp.route('/admin/editar_anuncio_general/<int:id_anuncio>', methods=['POST'])
def editar_anuncio_general(id_anuncio):
    if session.get('rol') != 'A': return redirect(url_for('index'))
    
    nuevo_contenido = request.form.get('contenido')
    cur = db.connection.cursor()
    cur.execute("UPDATE anuncios SET contenido = %s WHERE id = %s", (nuevo_contenido, id_anuncio))
    db.connection.commit()
    flash("Anuncio global actualizado.", "success")
    return redirect(url_for('acciones_admin'))

@paitApp.route('/admin/fijar_anuncio/<int:id_anuncio>')
def fijar_anuncio(id_anuncio):
    if session.get('rol') != 'A': return redirect(url_for('index'))
    
    cur = db.connection.cursor()
    # Cambiamos el estado (si es 0 pasa a 1, si es 1 pasa a 0)
    cur.execute("UPDATE anuncios SET fijado = NOT fijado WHERE id = %s", [id_anuncio])
    db.connection.commit()
    flash("Prioridad de anuncio actualizada.", "success")
    return redirect(url_for('acciones_admin'))

@paitApp.route('/marcar_leido/<int:id_anuncio>', methods=['POST'])
def marcar_leido(id_anuncio):
    if 'user_id' not in session: return jsonify({"success": False}), 401
    
    id_u = session['user_id']
    cur = db.connection.cursor()
    # INSERT IGNORE evita errores si el usuario le da click varias veces
    cur.execute("INSERT IGNORE INTO lecturas_anuncios (id_usuario, id_anuncio) VALUES (%s, %s)", (id_u, id_anuncio))
    db.connection.commit()
    return jsonify({"success": True})



#MI EQUIPO  
@paitApp.route('/mi_equipo')
def mi_equipo():
    if 'user_id' not in session: 
        return redirect(url_for('index'))
    
    # Buscamos el equipo del usuario en la DB
    equipo = ModelEquipo.obtener_equipo_usuario(db, session['user_id'])
    
    if equipo:
        # Redirigimos al tablon usando el ID del equipo encontrado
        return redirect(url_for('tablon', id_equipo=equipo.id))
    else:
        flash("Aún no tienes un equipo.", "info")
        return redirect(url_for('dashboard_alumno'))
    
#MIS EQUIPOS MENTORES
@paitApp.route('/mis_equipos_mentor')
def mis_equipos_mentor():  # <--- ESTE NOMBRE es el que busca url_for
    if 'user_id' not in session or session.get('rol') != 'M':
        return redirect(url_for('index'))
        
    equipos = ModelEquipo.obtener_equipos_mentor(db, session['user_id'])
    return render_template('equiposMe.html', equipos=equipos)


@paitApp.route('/buscar_alumnos')
def buscar_alumnos():
    if 'user_id' not in session: return redirect(url_for('index'))
    
    # Atrapamos los 3 filtros
    nombre = request.args.get('nombre') # <--- Nuevo
    carrera = request.args.get('carrera')
    grado = request.args.get('grado')

    # Pasamos el nombre al modelo
    alumnos = ModelUser.obtener_disponibles(db, carrera, grado, id_excluir=session['user_id'], nombre=nombre)
    
    return render_template('buscar_alumnos.html', alumnos=alumnos)

@paitApp.route('/enviar_invitacion/<int:id_receptor>', methods=['POST'])
def enviar_invitacion(id_receptor):
    if 'user_id' not in session: return redirect(url_for('index'))
    
    id_emisor = session['user_id']
    # Buscamos el equipo del emisor (Líder o Mentor)
    equipo = ModelEquipo.obtener_equipo_usuario(db, id_emisor)
    
    if not equipo:
        flash("No tienes permiso para invitar alumnos.", "danger")
        return redirect(url_for('dashboard_alumno'))

    # Validaciones de reglas de negocio
    puede_unirse, mensaje = ModelEquipo.puede_unirse(db, equipo.id, id_receptor)
    
    if puede_unirse:
        try:
            cur = db.connection.cursor()
            # Insertamos la invitación con estado PENDIENTE
            cur.execute("""
                INSERT INTO invitaciones (id_emisor, id_receptor, id_equipo, tipo, estado) 
                VALUES (%s, %s, %s, 'INVITAR', 'PENDIENTE')
            """, (id_emisor, id_receptor, equipo.id))
            db.connection.commit()
            flash(f"Invitación enviada con éxito.", "success")
        except Exception:
            flash("Ya has enviado una invitación a este alumno.", "warning")
    else:
        flash(mensaje, "danger")
        
    return redirect(url_for('buscar_alumnos'))

# --- RUTA PARA ABANDONAR EQUIPO ---
@paitApp.route('/abandonar_equipo/<int:id_equipo>', methods=['POST'])
def abandonar_equipo(id_equipo):
    if 'user_id' not in session: return redirect(url_for('index'))
    
    id_usuario = session['user_id']
    cur = db.connection.cursor()
    
    # 1. Verificar si es el líder
    cur.execute("SELECT id_lider FROM equipos WHERE id = %s", [id_equipo])
    equipo = cur.fetchone()
    
    if equipo and equipo[0] == id_usuario:
        flash("Como Jefe de Equipo, no puedes salir sin antes transferir el mando a otro compañero.", "warning")
        return redirect(url_for('tablon', id_equipo=id_equipo))

    # 2. Eliminar de miembros_equipo
    cur.execute("DELETE FROM miembros_equipo WHERE id_equipo = %s AND id_usuario = %s", (id_equipo, id_usuario))
    db.connection.commit()
    
    flash("Has salido del equipo correctamente.", "info")
    return redirect(url_for('dashboard_alumno'))

# --- RUTA PARA CONFIGURAR RECLUTAMIENTO ---
@paitApp.route('/configurar_reclutamiento/<int:id_equipo>', methods=['POST'])
def configurar_reclutamiento(id_equipo):
    if 'user_id' not in session: return redirect(url_for('index'))
    
    # Solo Mentor o Líder pueden configurar
    carrera = request.form.get('busca_carrera')
    grado = request.form.get('busca_grado') # Puede ser '' (Cualquiera)
    
    # Convertir grado a None si es "Cualquiera"
    grado_val = int(grado) if grado and grado != '' else None
    
    cur = db.connection.cursor()
    cur.execute("""
        UPDATE equipos 
        SET busca_carrera = %s, busca_grado = %s 
        WHERE id = %s
    """, (carrera, grado_val, id_equipo))
    db.connection.commit()
    
    flash("Preferencias de reclutamiento actualizadas.", "success")
    return redirect(url_for('tablon', id_equipo=id_equipo))


# ----  ADMIN ----
@paitApp.route('/admin/acciones')
def acciones_admin():
    if session.get('rol') != 'A': 
        return redirect(url_for('index'))
    
    cur = db.connection.cursor()
    # Traemos los anuncios generales (id_equipo es NULL)
    # Ordenamos por fijado primero y luego por fecha
    cur.execute("""
        SELECT id, contenido, fecha_publicacion, fijado 
        FROM anuncios 
        WHERE id_equipo IS NULL 
        ORDER BY fijado DESC, fecha_publicacion DESC
    """)
    anuncios = cur.fetchall()
    
    # Pasamos los anuncios al template
    return render_template('acciones.html', anuncios=anuncios)


# parte de administrar mentores mediante el admin
@paitApp.route('/admin/mentores')
def vista_mentores():
    if session.get('rol') != 'A':
        return redirect(url_for('login'))

    cursor = db.connection.cursor()
    # 1. Traemos a los mentores
    cursor.execute("SELECT id, nombre, codigo FROM usuarios WHERE rol = 'M'")
    mentores = cursor.fetchall()
    # 2. Traemos los equipos
    cursor.execute("SELECT id, nombre FROM equipos")
    equipos = cursor.fetchall()
    return render_template('mentor.html', mentores=mentores, equipos=equipos)

# ÚNICA RUTA PARA ASIGNAR
@paitApp.route('/admin/guardar_asignacion', methods=['POST'])
def guardar_asignacion():
    # Seguridad: Solo admin
    if session.get('rol') != 'A': 
        return redirect(url_for('login'))
    
    id_mentor = request.form.get('id_mentor')
    id_equipo = request.form.get('id_equipo')
    
    if not id_mentor or not id_equipo:
        flash("Datos incompletos", "warning")
        return redirect(url_for('vista_mentores'))

    # Usamos el modelo para procesar la lógica pesada
    if ModelEquipo.asignar_mentor(db, id_equipo, id_mentor):
        flash("Mentor asignado correctamente al equipo.", "success")
    else:
        flash("Hubo un error al realizar la asignación.", "danger")
        
    return redirect(url_for('vista_mentores'))



if __name__ == '__main__':
    paitApp.config.from_object(config['development'])
    paitApp.run(port=3000, debug=True)