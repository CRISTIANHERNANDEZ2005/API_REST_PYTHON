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
    
    # Añade esto temporalmente para debug
    def __repr__(self):
        return f"<Config: {self.MYSQL_HOST}:{self.MYSQL_PORT} DB:{self.MYSQL_DATABASE} USER:{self.MYSQL_USER}>"