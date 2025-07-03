"""
Propósito: Gestiona la configuración de la aplicación Flask.
Funcionalidad: Define clases de configuración para diferentes entornos (desarrollo, 
producción) que extraen variables de entorno desde .env. Proporciona una estructura 
centralizada para acceder a configuraciones como credenciales de MySQL y la clave secreta.
"""

import os

class Config:
    # Configuración de MySQL
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'maglev.proxy.rlwy.net')  # Valor por defecto explícito
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'YGdRCcTLeuiGqiMEBMVDlZondeuiGAAP')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'railway')
    MYSQL_PORT = os.getenv('MYSQL_PORT', '26298')  # Como string
    
    def __repr__(self):
        return f"<Config: {self.MYSQL_HOST}:{self.MYSQL_PORT} DB:{self.MYSQL_DATABASE} USER:{self.MYSQL_USER}>"


# /lib
# |    |
# |--- /model
# |    |    usuario.dart
# |    |    categoria.dart
# |    |    producto.dart
# |    |
# |--- /services
# |    |    auth_service.dart
# |    |    usuario_service.dart
# |    |    categoria_service.dart
# |    |    producto_service.dart
# |    |
# |--- /screens
# |   |-- /auth
# |   |   |-- login_screen.dart
# |   |   |-- register_screen.dart
# |   |-- /categorias
# |   |-- dashboard_screen.dart
# |   |   |-- categoria_editar_screen.dart
# |   |   |-- categoria_lista_screen.dart
# |   |   |-- categoria_agregar_screen.dart
# |   |-- /productos
# |   |   |-- producto_editar_screen.dart
# |   |   |-- producto_lista_screen.dart
# |   |   |-- producto_agregar_screen.dart
# |   |   /usuarios
# |   |   |-- usuario_editar_screen.dart
# |   |   |-- usuario_lista_screen.dart
# |   |   |-- usuario_agregar_screen.dart
# |    
# |--- /utils
# |    |    ruta.dart
# |    |    token_storage.dart
# |    |    validators.dart
# |    | 
# |    |
# |--- main.dart

# /PythonApi-main
# |    |
# |    |
# |--- /app
# |   |-- /blueprints
# |   |   |-- auth.py
# |   |   |-- categoria.py
# |   |   |-- documentacion.py
# |   |   |-- producto.py
# |   |   |-- usuario.py
# |   |-- /static
# |   |   |-- /swagger-ui
# |   |-- .env
# |   |-- __init__.py
# |   |-- config.py
# |    
# |--- Procfile
# |--- requirements.txt
# |--- run.py
# |--- swagger.json