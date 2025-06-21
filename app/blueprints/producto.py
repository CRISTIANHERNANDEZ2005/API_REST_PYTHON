"""
Propósito: Contiene las rutas y lógica para las operaciones CRUD de la tabla productos.
Funcionalidad: Define un Blueprint (producto_bp) que agrupa las rutas relacionadas 
con productos (/productos, /productos/<id>). Incluye funciones para obtener todos los productos, 
obtener un producto específico, crear, actualizar y eliminar productos.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
import pymysql.cursors

# Crea un Blueprint llamado 'producto'
producto_bp = Blueprint('producto', __name__)

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

@producto_bp.route('/', methods=['GET'])
@jwt_required()
def get_productos():
    """Obtiene todos los productos"""
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM productos")
            productos = cursor.fetchall()
            return jsonify(productos)
    except pymysql.Error as err:
        current_app.logger.error(f"Error al obtener productos: {str(err)}")
        return jsonify({"error": "Error al obtener los productos"}), 500
    finally:
        connection.close()

@producto_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_producto(id):
    """Obtiene un producto específico por ID"""
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM productos WHERE id = %s", (id,))
            producto = cursor.fetchone()
            
            if producto:
                return jsonify(producto)
            return jsonify({"error": "Producto no encontrado"}), 404
    except pymysql.Error as err:
        current_app.logger.error(f"Error al obtener producto {id}: {str(err)}")
        return jsonify({"error": "Error al obtener el producto"}), 500
    finally:
        connection.close()

@producto_bp.route('/', methods=['POST'])
@jwt_required()
def create_producto():
    """Crea un nuevo producto"""
    data = request.get_json()
    nombre = data.get('nombre')
    precio = data.get('precio')
    descripcion = data.get('descripcion', '')  # Opcional, con valor por defecto
    nombre_categoria = data.get('nombre_categoria', '')  # Opcional, con valor por defecto
    
    # Validación de campos requeridos
    if not all([nombre, precio is not None]):
        return jsonify({"error": "Nombre y precio son requeridos"}), 400
    
    try:
        # Validar que el precio sea numérico
        precio = float(precio)
    except (ValueError, TypeError):
        return jsonify({"error": "El precio debe ser un número válido"}), 400

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO productos 
                (nombre, precio, descripcion, nombre_categoria) 
                VALUES (%s, %s, %s, %s)""",
                (nombre, precio, descripcion, nombre_categoria)
            )
            connection.commit()
            producto_id = cursor.lastrowid
            
            return jsonify({
                "message": "Producto creado exitosamente",
                "producto": {
                    "id": producto_id,
                    "nombre": nombre,
                    "precio": precio,
                    "descripcion": descripcion,
                    "nombre_categoria": nombre_categoria
                }
            }), 201
    except pymysql.Error as err:
        current_app.logger.error(f"Error al crear producto: {str(err)}")
        return jsonify({"error": "Error al crear el producto"}), 500
    finally:
        connection.close()

@producto_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_producto(id):
    """Actualiza un producto existente"""
    data = request.get_json()
    nombre = data.get('nombre')
    precio = data.get('precio')
    descripcion = data.get('descripcion', '')
    nombre_categoria = data.get('nombre_categoria', '')
    
    # Validación de campos requeridos
    if not all([nombre, precio is not None]):
        return jsonify({"error": "Nombre y precio son requeridos"}), 400
    
    try:
        # Validar que el precio sea numérico
        precio = float(precio)
    except (ValueError, TypeError):
        return jsonify({"error": "El precio debe ser un número válido"}), 400

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE productos SET 
                nombre = %s, 
                precio = %s, 
                descripcion = %s, 
                nombre_categoria = %s 
                WHERE id = %s""",
                (nombre, precio, descripcion, nombre_categoria, id)
            )
            connection.commit()
            
            if cursor.rowcount == 0:
                return jsonify({"error": "Producto no encontrado"}), 404
                
            return jsonify({
                "message": "Producto actualizado exitosamente",
                "producto": {
                    "id": id,
                    "nombre": nombre,
                    "precio": precio,
                    "descripcion": descripcion,
                    "nombre_categoria": nombre_categoria
                }
            })
    except pymysql.Error as err:
        current_app.logger.error(f"Error al actualizar producto {id}: {str(err)}")
        return jsonify({"error": "Error al actualizar el producto"}), 500
    finally:
        connection.close()

@producto_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_producto(id):
    """Elimina un producto"""
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
            connection.commit()
            
            if cursor.rowcount == 0:
                return jsonify({"error": "Producto no encontrado"}), 404
                
            return jsonify({"message": "Producto eliminado exitosamente"})
    except pymysql.Error as err:
        current_app.logger.error(f"Error al eliminar producto {id}: {str(err)}")
        return jsonify({"error": "Error al eliminar el producto"}), 500
    finally:
        connection.close()