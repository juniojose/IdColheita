# app/__init__.py
from flask import Flask
from .config import Config
from .models.database import init_db
from .utils.logger import setup_logger

logger = setup_logger()

def create_app():
    """Fábrica da aplicação Flask."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar banco de dados
    with app.app_context():
        init_db(app)

    # Registrar blueprints (a serem adicionados nas etapas 8 e 9)
    # Exemplo: from .routes.fornecedores import fornecedores_bp
    # app.register_blueprint(fornecedores_bp)

    logger.info("Aplicação Flask inicializada com sucesso.")

    return app