# app/blueprints/fornecedores/__init__.py
from flask import Blueprint

fornecedores_bp = Blueprint('fornecedores', __name__, template_folder='../../templates/fornecedores')

from . import routes