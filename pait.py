from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from config import config
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

paitApp = Flask(__name__)
db      = MySQL(paitApp)
signinManager = LoginManager(paitApp)

@paitApp.route('/registro', methods=['GET', 'POST'])
def registro():
    return render_template('registro.html')

if __name__ == '__main__':
    paitApp.config.from_object(config['development'])
    paitApp.run(port=3000, debug=True)