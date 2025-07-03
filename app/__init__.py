"""
Propósito: Inicializa la aplicación Flask y configura sus componentes principales.
Funcionalidad: Define la función create_app() que crea la instancia de Flask, carga 
configuraciones desde .env a través de config.py, inicializa extensiones como CORS y JWT, 
configura la clave secreta y registra los Blueprints de categorías, productos, 
documentación y autenticación.
"""

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager  # Importa JWTManager
from dotenv import load_dotenv
import os
from pathlib import Path

from .config import Config
from .blueprints.categoria import categoria_bp
from .blueprints.producto import producto_bp
from .blueprints.documentacion import documentacion_bp
from .blueprints.auth import auth_bp
from .blueprints.usuario import usuario_bp

cors = CORS(resources={r"/*": {"origins": "*"}})  # Permite todos los orígenes
jwt = JWTManager()  # Instancia global de JWTManager

def create_app():
    
    env_path = Path('.') / '.env'
    print(f"Buscando .env en: {env_path.absolute()}")  # Debug
    load_dotenv(env_path)
    app = Flask(__name__)
    app.config.from_object(Config)
    
    print("!CONFIGURACIÓN CARGADA!")  # Debug
    print(f"DB_HOST: {os.getenv('MYSQL_HOST')}")  # Debug
    
    app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY', 'Yeicy')
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    # Configura la clave secreta de la aplicación
    app.secret_key = app.config['SECRET_KEY']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hora

    # Configura la clave secreta de la aplicación
    app.secret_key = app.config['JWT_SECRET_KEY']

    # Inicializa extensiones
    cors.init_app(app)
    jwt.init_app(app)  # Inicializa JWTManager

    # Registra Blueprints
    app.register_blueprint(categoria_bp, url_prefix='/categorias')
    app.register_blueprint(producto_bp, url_prefix='/productos')
    app.register_blueprint(documentacion_bp, url_prefix='/documentacion')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(usuario_bp, url_prefix='/usuarios')

    return app