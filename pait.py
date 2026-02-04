from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect
from config import config

# Modelos
from models.ModelUser import ModelUser

paitApp = Flask(__name__)
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

if __name__ == '__main__':
    paitApp.config.from_object(config['development'])
    paitApp.run(port=3000, debug=True)