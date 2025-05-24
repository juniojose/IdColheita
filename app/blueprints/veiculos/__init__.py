# app/blueprints/veiculos/__init__.py
from flask import Blueprint

veiculos_bp = Blueprint('veiculos', __name__, template_folder='../../templates/veiculos')

from . import routes