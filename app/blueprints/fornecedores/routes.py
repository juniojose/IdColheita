# app/blueprints/fornecedores/routes.py
from flask import render_template, request, redirect, url_for, flash
from . import fornecedores_bp
from ...models.fornecedor import Fornecedor
from .forms import FornecedorForm
from ...services.id_generator import generate_id
from ...utils.logger import setup_logger

logger = setup_logger()

@fornecedores_bp.route('/')
def index():
    """Rota inicial da aplicação."""
    return redirect(url_for('fornecedores.listar_fornecedores'))

@fornecedores_bp.route('/fornecedores', methods=['GET', 'POST'])
def listar_fornecedores():
    form = FornecedorForm()
    fornecedores = Fornecedor.listar_todos()
    if form.validate_on_submit():
        try:
            # Gerar ID automaticamente
            id_fornecedor = generate_id('fornecedores')
            fornecedor = Fornecedor(
                id=id_fornecedor,
                nome=form.nome.data,
                pessoa_de_contato=form.pessoa_de_contato.data,
                whatsapp=form.whatsapp.data
            )
            fornecedor.salvar()
            flash('Fornecedor cadastrado com sucesso!', 'success')
            return redirect(url_for('fornecedores.listar_fornecedores'))
        except Exception as e:
            flash(f'Erro ao cadastrar fornecedor: {str(e)}', 'danger')
            logger.error(f"Erro ao cadastrar fornecedor: {str(e)}")
    return render_template('index.html', form=form, fornecedores=fornecedores)

@fornecedores_bp.route('/fornecedores/editar/<string:id>', methods=['GET', 'POST'])
def editar_fornecedor(id):
    fornecedor = Fornecedor.buscar_por_id(id)
    if not fornecedor:
        flash('Fornecedor não encontrado!', 'danger')
        return redirect(url_for('fornecedores.listar_fornecedores'))
    form = FornecedorForm(obj=fornecedor)
    if form.validate_on_submit():
        try:
            fornecedor.nome = form.nome.data
            fornecedor.pessoa_de_contato = form.pessoa_de_contato.data
            fornecedor.whatsapp = form.whatsapp.data
            fornecedor.atualizar()
            flash('Fornecedor atualizado com sucesso!', 'success')
            return redirect(url_for('fornecedores.listar_fornecedores'))
        except Exception as e:
            flash(f'Erro ao atualizar fornecedor: {str(e)}', 'danger')
            logger.error(f"Erro ao atualizar fornecedor: {str(e)}")
    return render_template('edit.html', form=form, fornecedor=fornecedor)

@fornecedores_bp.route('/fornecedores/deletar/<string:id>', methods=['POST'])
def deletar_fornecedor(id):
    try:
        fornecedor = Fornecedor.buscar_por_id(id)
        if fornecedor:
            fornecedor.deletar()
            flash('Fornecedor deletado com sucesso!', 'success')
        else:
            flash('Fornecedor não encontrado!', 'danger')
    except Exception as e:
        if "FOREIGN KEY constraint failed" in str(e):
            flash('Não é possível excluir o fornecedor porque ele está associado a veículos. Remova os veículos associados primeiro.', 'danger')
        else:
            flash(f'Erro ao deletar fornecedor: {str(e)}', 'danger')
        logger.error(f"Erro ao deletar fornecedor: {str(e)}")
    except Exception as e:
        flash(f'Erro ao deletar fornecedor: {str(e)}', 'danger')
        logger.error(f"Erro ao deletar fornecedor: {str(e)}")
    return redirect(url_for('fornecedores.listar_fornecedores'))