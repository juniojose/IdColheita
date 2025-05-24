# app/__init__.py
from flask import Flask
from .config import Config
from .models.database import init_db
from .utils.logger import setup_logger
from .blueprints.fornecedores import fornecedores_bp  # Import do blueprint

logger = setup_logger()

def create_app():
    """Fábrica da aplicação Flask."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar banco de dados
    with app.app_context():
        init_db(app)

    # Registrar blueprints
    app.register_blueprint(fornecedores_bp)

    logger.info("Aplicação Flask inicializada com sucesso.")

    return app