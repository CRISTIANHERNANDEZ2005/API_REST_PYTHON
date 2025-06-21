"""
Propósito: Contiene las rutas y lógica para las operaciones CRUD de la tabla categoria.
Funcionalidad: Define un Blueprint (categoria_bp) que agrupa las rutas relacionadas con 
categorías (/categorias, /categorias/<id>). Incluye funciones para obtener todas las categorías, 
obtener una categoría específica, crear, actualizar y eliminar categorías, con manejo de errores
y conexión a la base de datos usando PyMySQL.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
import pymysql.cursors

# Crea un Blueprint llamado 'categoria'
categoria_bp = Blueprint('categoria', __name__)

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

@categoria_bp.route('/', methods=['GET'])
@jwt_required()
def get_categorias():
    """Obtiene todas las categorías"""
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM categoria")
            categorias = cursor.fetchall()
            return jsonify(categorias)
    except pymysql.Error as err:
        current_app.logger.error(f"Error al obtener categorías: {str(err)}")
        return jsonify({"error": "Error al obtener categorías"}), 500
    finally:
        connection.close()

@categoria_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_categoria(id):
    """Obtiene una categoría específica por ID"""
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM categoria WHERE id = %s", (id,))
            categoria = cursor.fetchone()
            
            if categoria:
                return jsonify(categoria)
            return jsonify({"error": "Categoría no encontrada"}), 404
    except pymysql.Error as err:
        current_app.logger.error(f"Error al obtener categoría {id}: {str(err)}")
        return jsonify({"error": "Error al obtener la categoría"}), 500
    finally:
        connection.close()

@categoria_bp.route('/', methods=['POST'])
@jwt_required()
def create_categoria():
    """Crea una nueva categoría"""
    data = request.get_json()
    nombre = data.get('nombre')
    
    if not nombre:
        return jsonify({"error": "El nombre es requerido"}), 400
    
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO categoria (nombre) VALUES (%s)", 
                (nombre,)
            )
            connection.commit()
            categoria_id = cursor.lastrowid
            
            return jsonify({
                "message": "Categoría creada exitosamente",
                "categoria": {
                    "id": categoria_id,
                    "nombre": nombre
                }
            }), 201
    except pymysql.Error as err:
        current_app.logger.error(f"Error al crear categoría: {str(err)}")
        return jsonify({"error": "Error al crear la categoría"}), 500
    finally:
        connection.close()

@categoria_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_categoria(id):
    """Actualiza una categoría existente"""
    data = request.get_json()
    nombre = data.get('nombre')
    
    if not nombre:
        return jsonify({"error": "El nombre es requerido"}), 400
    
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE categoria SET nombre = %s WHERE id = %s",
                (nombre, id)
            )
            connection.commit()
            
            if cursor.rowcount == 0:
                return jsonify({"error": "Categoría no encontrada"}), 404
                
            return jsonify({
                "message": "Categoría actualizada exitosamente",
                "categoria": {
                    "id": id,
                    "nombre": nombre
                }
            })
    except pymysql.Error as err:
        current_app.logger.error(f"Error al actualizar categoría {id}: {str(err)}")
        return jsonify({"error": "Error al actualizar la categoría"}), 500
    finally:
        connection.close()

@categoria_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_categoria(id):
    """Elimina una categoría"""
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM categoria WHERE id = %s", (id,))
            connection.commit()
            
            if cursor.rowcount == 0:
                return jsonify({"error": "Categoría no encontrada"}), 404
                
            return jsonify({"message": "Categoría eliminada exitosamente"})
    except pymysql.Error as err:
        current_app.logger.error(f"Error al eliminar categoría {id}: {str(err)}")
        return jsonify({"error": "Error al eliminar la categoría"}), 500
    finally:
        connection.close()