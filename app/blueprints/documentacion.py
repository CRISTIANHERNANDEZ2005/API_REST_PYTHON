from flask import send_from_directory, render_template_string, Blueprint
import os

documentacion_bp = Blueprint('documentacion', __name__)

# http://127.0.0.1:5000/documentacion/docs

@documentacion_bp.route('/swagger.json')
def swagger_json():
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    print(f"Intentando servir swagger.json desde: {os.path.join(root_dir, 'swagger.json')}")  # Depuración
    if not os.path.exists(os.path.join(root_dir, 'swagger.json')):
        return {"error": "Archivo swagger.json no encontrado"}, 404
    return send_from_directory(root_dir, 'swagger.json')

@documentacion_bp.route("/docs")
def swagger_ui():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Swagger UI</title>
        <link rel="stylesheet" href="/static/swagger-ui/swagger-ui.css" />
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="/static/swagger-ui/swagger-ui-bundle.js"></script>
        <script src="/static/swagger-ui/swagger-ui-standalone-preset.js"></script>
        <script>
            window.onload = () => {
                window.ui = SwaggerUIBundle({
                    url: '/documentacion/swagger.json',
                    dom_id: '#swagger-ui',
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIStandalonePreset
                    ],
                    layout: "StandaloneLayout",
                });
            };
        </script>
    </body>
    </html>
    """)