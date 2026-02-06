from flask import Flask, render_template, request, redirect, url_for, flash, session
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
paitApp.config['SECRET_KEY'] = 'Cl4v3Sup3rm3g4S3gur4PAIT2026!'
generador = URLSafeTimedSerializer(paitApp.config['SECRET_KEY'])
csrf = CSRFProtect(paitApp) # Protección CSRF Global
db = MySQL(paitApp)


@paitApp.route('/')
def index():
    return render_template('registro.html')

# login
@paitApp.route('/login', methods=['POST'])
def login():
    codigo = request.form.get('codigo')
    password = request.form.get('password')

    if not codigo or not password:
        flash("Código y contraseña son requeridos", "warning")
        return redirect(url_for('index'))

    user_logged = ModelUser.login(db, codigo, password)
    if user_logged:
        session['user_id'] = user_logged.id # Guardamos el ID real de la DB
        session['codigo'] = user_logged.codigo
        session['rol'] = user_logged.rol
        session['nombre'] = user_logged.nombre
        
        # Guardamos si tiene datos completos para el modal
        session['datos_completos'] = bool(user_logged.correo and user_logged.celular)

        if user_logged.rol == 'M':
            return redirect(url_for('dashboard_mentor'))
        return redirect(url_for('dashboard_alumno'))
    
    flash("Código o contraseña incorrectos.", "danger")
    return redirect(url_for('index'))

@paitApp.route('/actualizar_perfil', methods=['POST'])
def actualizar_perfil():
    if 'user_id' not in session: return redirect(url_for('index'))
    
    id_user = session['user_id']
    celular = request.form.get('celular')
    correo = request.form.get('correo')
    presentacion = request.form.get('presentacion', '')

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

@paitApp.route('/dashboard_alumno')
def dashboard_alumno():
    if 'user_id' not in session: return redirect(url_for('index'))
    id_u = session['user_id']
    # Verificamos si el usuario ya tiene equipo
    equipo_usuario = ModelEquipo.obtener_equipo_usuario(db, id_u)
    # Verificamos si el usuario tiene invitaciones
    invitaciones = ModelEquipo.obtener_invitaciones_usuario(db, id_u)
    
    return render_template('dashboardAl.html', 
                           equipo_usuario=equipo_usuario, 
                           invitaciones=invitaciones)

@paitApp.route('/dashboard_mentor')
def dashboard_mentor():
    if 'user_id' not in session or session.get('rol') != 'M':
        return redirect(url_for('index'))
    
    # Verificamos si tiene equipos asignados
    equipos = ModelEquipo.obtener_equipos_mentor(db, session['user_id'])
    return render_template('dashboardMe.html', tiene_equipos=len(equipos) > 0)

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
        return "¡Correo enviado con éxito!"
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

# SingOut
@paitApp.route('/signout', methods=['GET'])
def signout():
    session.clear()
    return redirect(url_for('index'))

@paitApp.route('/equipos')
def lista_equipos():
    if 'user_id' not in session: return redirect(url_for('index'))
    equipos = ModelEquipo.obtener_todos(db)
    return render_template('equipos.html', equipos=equipos)

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

@paitApp.route('/mi_equipo')
def mi_equipo():
    if 'user_id' not in session: return redirect(url_for('index'))
    
    id_usuario = session['user_id']
    # Obtenemos el equipo al que pertenece el usuario
    equipo = ModelEquipo.obtener_equipo_usuario(db, id_usuario)
    
    if not equipo:
        flash("Aún no perteneces a ningún equipo.", "info")
        return redirect(url_for('dashboard_alumno'))
    
    # Obtenemos los integrantes reales
    integrantes = ModelEquipo.obtener_miembros(db, equipo.id)
    # Obtenemos el conteo para la validación de cupo
    total_miembros = len(integrantes)
    
    return render_template('miequipo.html', 
                           equipo=equipo, 
                           integrantes=integrantes, 
                           total_miembros=total_miembros)

@paitApp.route('/mis_equipos_mentor')
def mis_equipos_mentor():
    if 'user_id' not in session or session.get('rol') != 'M':
        return redirect(url_for('index'))
        
    equipos = ModelEquipo.obtener_equipos_mentor(db, session['user_id'])
    return render_template('equiposMe.html', equipos=equipos)

@paitApp.route('/buscar_alumnos')
def buscar_alumnos():
    if 'user_id' not in session: return redirect(url_for('index'))
    
    # Solo Jefe (U + tiene equipo) o Mentor (M) pueden invitar
    # (El decorador de seguridad que hicimos antes sería ideal aquí)
    
    carrera = request.args.get('carrera')
    grado = request.args.get('grado')

    # Obtenemos los candidatos filtrados
    alumnos = ModelUser.obtener_disponibles(db, carrera, grado, id_excluir=session['user_id'])
    
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

@paitApp.route('/procesar_invitacion/<int:id_inv>/<string:accion>', methods=['POST'])
def procesar_invitacion(id_inv, accion):
    if 'user_id' not in session: return redirect(url_for('index'))
    
    exito, mensaje = ModelEquipo.responder_invitacion(db, id_inv, accion, session['user_id'])
    flash(mensaje, "success" if exito else "danger")
    
    return redirect(url_for('dashboard_alumno'))


if __name__ == '__main__':
    paitApp.config.from_object(config['development'])
    paitApp.run(port=3000, debug=True)