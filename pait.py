from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect
from config import config
from flask_mail import Mail, Message

# Modelos
from models.ModelUser import ModelUser

paitApp = Flask(__name__)
# Configuración Flask,para decirle quien es el proveedor de correos
paitApp.config['MAIL_SERVER'] = 'smtp.gmail.com'
paitApp.config['MAIL_PORT'] = 587
paitApp.config['MAIL_USE_TLS'] = True
paitApp.config['MAIL_USERNAME'] = 'proyectospaitoficial@gmail.com' #bspz lvwj cltp uces
paitApp.config['MAIL_PASSWORD'] = 'yqyoovwtnxbapocf' # Clave especial de Google

mail = Mail(paitApp) # Inicializamos el motor



csrf = CSRFProtect(paitApp) # Protección CSRF Global
db = MySQL(paitApp)







@paitApp.route('/')
def index():
    return render_template('registro.html')

@paitApp.route('/login', methods=['POST'])
def login():
    codigo = request.form.get('codigo')
    password = request.form.get('password')
    celular = request.form.get('celular')
    correo = request.form.get('correo')

    # Validación de campos obligatorios (Flash)
    if not codigo or not password or not celular or not correo:
        flash("Por favor, completa todos los campos para continuar.", "warning")
        return redirect(url_for('index'))

    try:
        # Intentar login a través del modelo
        user_logged = ModelUser.login(db, codigo, password)
        
        if user_logged:
            # Actualizar datos de contacto en cada login
            ModelUser.update_data(db, user_logged.id, celular, correo)
            
            # Guardar sesión
            session['user_id'] = user_logged.codigo
            session['rol'] = user_logged.rol
            session['nombre'] = user_logged.nombre

            if user_logged.rol == 'M':
                return redirect(url_for('dashboard_mentor'))
            return redirect(url_for('dashboard_alumno'))
        else:
            flash("Código o contraseña incorrectos.", "danger")
            return redirect(url_for('index'))
            
    except Exception as e:
        flash(f"Error en el servidor: {str(e)}", "danger")
        return redirect(url_for('index'))

@paitApp.route('/dashboard_alumno')
def dashboard_alumno():
    return render_template('dashboardAl.html')

@paitApp.route('/dashboard_mentor')
def dashboard_mentor():
    return render_template('dashboardMe.html')

# Ruta para la página de recuperación de contraseña
@paitApp.route('/enviar_recuperacion', methods=['POST', 'GET'])
def enviar_recuperacion():
    # 1. Atrapamos el dato del formulario
    correo_usuario = request.form['email_usuario'] # El name que pusiste en el input
    
    # 2. Creamos el objeto del mensaje
    # subject = Asunto, sender = Quien envía, recipients = Quien recibe (en lista [])
    msg = Message(subject="Recuperar Contraseña",
                  sender=paitApp.config['MAIL_USERNAME'],
                  recipients=[correo_usuario])
    
    # 3. Escribimos el cuerpo del mensaje
    msg.body = "Hola! Para cambiar tu clave entra a este link: (Aquí irá tu link)"
    
    # 4. El acto de magia: enviar
    try:
        mail.send(msg)
        return "¡Correo enviado con éxito!"
    except Exception as e:
        return f"Error al enviar: {str(e)}"
    
# Ruta para abrir el formulario de recuperación de contraseña
@paitApp.route('/Recuperar')
def recuperar():
    return render_template('recuperar.html')



if __name__ == '__main__':
    paitApp.config.from_object(config['development'])
    paitApp.run(port=3000, debug=True)