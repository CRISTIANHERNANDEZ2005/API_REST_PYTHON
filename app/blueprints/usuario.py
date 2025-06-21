"""
Propósito: Contiene las rutas y lógica para las operaciones CRUD de la tabla usuario.
Funcionalidad: Define un Blueprint (usuario_bp) que agrupa las rutas relacionadas con 
usuarios (/usuarios, /usuarios/<id>). Incluye funciones para obtener todos los usuarios, 
obtener un usuario específico, crear, actualizar y eliminar usuarios, con validaciones 
y manejo de errores. Todas las rutas excepto GET están protegidas por JWT.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
import pymysql.cursors
import bcrypt
import re

# Crea un Blueprint llamado 'usuario'
usuario_bp = Blueprint('usuario', __name__)

def get_db_connection():
    """Establece una conexión a la base de datos MySQL usando PyMySQL"""
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

def validate_numero(numero):
    """Valida el formato del número de usuario"""
    # Implementa validaciones específicas según tus requisitos
    return bool(numero)  # Por ahora solo verifica que no esté vacío

@usuario_bp.route('/', methods=['GET'])
@jwt_required()
def get_usuarios():
    """Obtiene todos los usuarios (sin información sensible)"""
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, numero, nombre, apellido FROM usuario")
            usuarios = cursor.fetchall()
            return jsonify(usuarios)
    except pymysql.Error as err:
        current_app.logger.error(f"Error al obtener usuarios: {str(err)}")
        return jsonify({"error": "Error al obtener los usuarios"}), 500
    finally:
        connection.close()

@usuario_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_usuario(id):
    """Obtiene un usuario específico por ID (sin información sensible)"""
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, numero, nombre, apellido FROM usuario WHERE id = %s", 
                (id,)
            )
            usuario = cursor.fetchone()
            
            if usuario:
                return jsonify(usuario)
            return jsonify({"error": "Usuario no encontrado"}), 404
    except pymysql.Error as err:
        current_app.logger.error(f"Error al obtener usuario {id}: {str(err)}")
        return jsonify({"error": "Error al obtener el usuario"}), 500
    finally:
        connection.close()

@usuario_bp.route('/', methods=['POST'])
@jwt_required()
def create_usuario():
    """Crea un nuevo usuario"""
    data = request.get_json()
    numero = data.get('numero')
    nombre = data.get('nombre')
    apellido = data.get('apellido')
    contrasena = data.get('contrasena')

    # Validación de campos
    if not all([numero, nombre, apellido, contrasena]):
        return jsonify({"error": "Número, nombre, apellido y contraseña son requeridos"}), 400
    
    if not validate_numero(numero):
        return jsonify({"error": "Número de usuario inválido"}), 400
    
    if not validate_password(contrasena):
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Verifica si el número ya está registrado
            cursor.execute("SELECT id FROM usuario WHERE numero = %s", (numero,))
            if cursor.fetchone():
                return jsonify({"error": "El número ya está registrado"}), 409

            # Hashea la contraseña
            hashed_password = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())

            # Inserta el nuevo usuario
            cursor.execute(
                """INSERT INTO usuario 
                (numero, nombre, apellido, contrasena) 
                VALUES (%s, %s, %s, %s)""",
                (numero, nombre, apellido, hashed_password)
            )
            connection.commit()
            usuario_id = cursor.lastrowid
            
            return jsonify({
                "message": "Usuario creado exitosamente",
                "usuario": {
                    "id": usuario_id,
                    "numero": numero,
                    "nombre": nombre,
                    "apellido": apellido
                }
            }), 201
    except pymysql.Error as err:
        current_app.logger.error(f"Error al crear usuario: {str(err)}")
        return jsonify({"error": "Error al crear el usuario"}), 500
    finally:
        connection.close()

@usuario_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_usuario(id):
    """Actualiza un usuario existente"""
    data = request.get_json()
    numero = data.get('numero')
    nombre = data.get('nombre')
    apellido = data.get('apellido')
    contrasena = data.get('contrasena')

    # Validación de campos mínimos
    if not all([numero, nombre, apellido]):
        return jsonify({"error": "Número, nombre y apellido son requeridos"}), 400
    
    if not validate_numero(numero):
        return jsonify({"error": "Número de usuario inválido"}), 400

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Verifica si el usuario existe
            cursor.execute("SELECT id FROM usuario WHERE id = %s", (id,))
            if not cursor.fetchone():
                return jsonify({"error": "Usuario no encontrado"}), 404

            # Verifica si el nuevo número ya está en uso por otro usuario
            cursor.execute(
                "SELECT id FROM usuario WHERE numero = %s AND id != %s", 
                (numero, id)
            )
            if cursor.fetchone():
                return jsonify({"error": "El número ya está en uso por otro usuario"}), 409

            # Prepara la consulta de actualización
            update_fields = []
            update_values = []
            
            update_fields.append("numero = %s")
            update_values.append(numero)
            
            update_fields.append("nombre = %s")
            update_values.append(nombre)
            
            update_fields.append("apellido = %s")
            update_values.append(apellido)
            
            # Si se proporcionó una nueva contraseña
            if contrasena:
                if not validate_password(contrasena):
                    return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400
                hashed_password = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())
                update_fields.append("contrasena = %s")
                update_values.append(hashed_password)
            
            # Construye y ejecuta la consulta
            update_values.append(id)
            update_query = f"UPDATE usuario SET {', '.join(update_fields)} WHERE id = %s"
            
            cursor.execute(update_query, update_values)
            connection.commit()
            
            if cursor.rowcount == 0:
                return jsonify({"error": "No se realizaron cambios en el usuario"}), 400
                
            return jsonify({
                "message": "Usuario actualizado exitosamente",
                "usuario": {
                    "id": id,
                    "numero": numero,
                    "nombre": nombre,
                    "apellido": apellido
                }
            })
    except pymysql.Error as err:
        current_app.logger.error(f"Error al actualizar usuario {id}: {str(err)}")
        return jsonify({"error": "Error al actualizar el usuario"}), 500
    finally:
        connection.close()

@usuario_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_usuario(id):
    """Elimina un usuario"""
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Verifica si el usuario existe
            cursor.execute("SELECT id FROM usuario WHERE id = %s", (id,))
            if not cursor.fetchone():
                return jsonify({"error": "Usuario no encontrado"}), 404

            # Elimina el usuario
            cursor.execute("DELETE FROM usuario WHERE id = %s", (id,))
            connection.commit()
            
            if cursor.rowcount == 0:
                return jsonify({"error": "No se pudo eliminar el usuario"}), 400
                
            return jsonify({"message": "Usuario eliminado exitosamente"})
    except pymysql.Error as err:
        current_app.logger.error(f"Error al eliminar usuario {id}: {str(err)}")
        return jsonify({"error": "Error al eliminar el usuario"}), 500
    finally:
        connection.close()