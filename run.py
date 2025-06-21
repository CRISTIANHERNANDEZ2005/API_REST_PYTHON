# Propósito: Punto de entrada para ejecutar la aplicación Flask.
# Funcionalidad: Crea una instancia de la aplicación Flask llamando a la función create_app() 
# definida en app/__init__.py y la ejecuta como servidor en el host y puerto
# especificados (por ejemplo, 0.0.0.0:5000). Permite iniciar la aplicación en modo desarrollo con la opción de 
# depuración activada.

# Importa la función para crear la aplicación desde el módulo app
from app import create_app

app = create_app()

# if __name__ == '__main__':
#     app.run()
