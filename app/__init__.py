# app/__init__.py
from flask import Flask, g, redirect, url_for
from .config import Config
from .models.database import init_db
from .models.fornecedor import Fornecedor
from .blueprints.fornecedores.routes import fornecedores_bp
from .blueprints.veiculos.routes import veiculos_bp
from .utils.logger import setup_logger
import os

logger = setup_logger()

def create_app():
    """Fábrica da aplicação Flask."""
    app = Flask(__name__)
    app.config.from_object(Config)
    # Configuração do diretório de uploads
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads/veiculos')

    # Criar diretório de uploads, se não existir
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Inicializar banco de dados
    with app.app_context():
        init_db(app)

    # Registrar blueprints
    app.register_blueprint(fornecedores_bp, url_prefix='/fornecedores')
    app.register_blueprint(veiculos_bp, url_prefix='/veiculos')

    # Before request para carregar fornecedores
    @app.before_request
    def load_fornecedores():
        g.fornecedores = Fornecedor.listar_todos()

    # Rota inicial
    @app.route('/')
    def index():
        return redirect(url_for('fornecedores.listar_fornecedores'))

    logger.info("Aplicação Flask inicializada com sucesso.")
    return app