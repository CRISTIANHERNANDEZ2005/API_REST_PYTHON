"""
Propósito: Define rutas para autenticación de usuarios (inicio de sesión, registro y verificación).
Funcionalidad: Proporciona endpoints /login, /register y /me para autenticar, registrar y 
obtener información del usuario autenticado usando JWT. Valida campos, hashea contraseñas con bcrypt 
y genera/verifica tokens JWT.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import pymysql.cursors
import bcrypt
import re

# Crea el Blueprint para autenticación
auth_bp = Blueprint('auth', __name__)

def get_db_connection():
    """
    Establece una conexión a la base de datos MySQL usando configuraciones de la app.
    """
    return pymysql.connect(
        host=current_app.config['MYSQL_HOST'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD'],
        database=current_app.config['MYSQL_DATABASE'],
        port=int(current_app.config['MYSQL_PORT']),
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5
    )

def validate_password(password):
    """Valida que la contraseña cumpla con los requisitos mínimos"""
    if len(password) < 6:
        return False
    return True

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Inicia sesión de un usuario verificando número y contraseña, generando un token JWT.
    """
    data = request.get_json()
    numero = data.get('numero')
    contrasena = data.get('contrasena')

    # Validación de campos
    if not numero or not contrasena:
        return jsonify({"error": "Número y contraseña son requeridos"}), 400

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Busca el usuario por número
            cursor.execute("SELECT * FROM usuarios WHERE numero = %s", (numero,))
            usuario = cursor.fetchone()
            
            if not usuario:
                return jsonify({"error": "Usuario no encontrado"}), 404
            
            # Verifica la contraseña
            if bcrypt.checkpw(contrasena.encode('utf-8'), usuario['contrasena'].encode('utf-8')):
                access_token = create_access_token(identity=str(usuario['id']))
                return jsonify({
                    "message": "Inicio de sesión exitoso",
                    "access_token": access_token,
                    "usuario": {
                        "id": usuario['id'],
                        "numero": usuario['numero'],
                        "nombre": usuario['nombre'],
                        "apellido": usuario['apellido']
                    }
                }), 200
            else:
                return jsonify({"error": "Credenciales inválidas"}), 401
    except pymysql.Error as err:
        current_app.logger.error(f"Error en login: {str(err)}")
        return jsonify({"error": "Error al procesar el inicio de sesión"}), 500
    finally:
        connection.close()

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Registra un nuevo usuario en la base de datos.
    """
    data = request.get_json()
    numero = data.get('numero')
    nombre = data.get('nombre')
    apellido = data.get('apellido')
    contrasena = data.get('contrasena')

    # Validación de campos
    if not all([numero, nombre, apellido, contrasena]):
        return jsonify({"error": "Todos los campos son requeridos"}), 400
    
    if not validate_password(contrasena):
        return jsonify({
            "error": "La contraseña debe tener al menos 6 caracteres"
        }), 400

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Verifica si el número ya está registrado
            cursor.execute("SELECT id FROM usuarios WHERE numero = %s", (numero,))
            if cursor.fetchone():
                return jsonify({"error": "El número ya está registrado"}), 409

            # Hashea la contraseña
            hashed_password = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())

            # Inserta el nuevo usuario
            cursor.execute(
                """INSERT INTO usuarios
                (numero, nombre, apellido, contrasena) 
                VALUES (%s, %s, %s, %s)""",
                (numero, nombre, apellido, hashed_password)
            )
            connection.commit()
            user_id = cursor.lastrowid

            # Crea token de acceso
            access_token = create_access_token(identity=str(user_id))
            
            return jsonify({
                "message": "Usuario registrado exitosamente",
                "access_token": access_token,
                "usuario": {
                    "id": user_id,
                    "numero": numero,
                    "nombre": nombre,
                    "apellido": apellido
                }
            }), 201
    except pymysql.Error as err:
        current_app.logger.error(f"Error en registro: {str(err)}")
        return jsonify({"error": "Error al registrar el usuario"}), 500
    finally:
        connection.close()