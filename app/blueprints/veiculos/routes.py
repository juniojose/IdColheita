# app/blueprints/veiculos/routes.py
from flask import render_template, request, redirect, url_for, flash, current_app
from . import veiculos_bp
from ...models.veiculo import Veiculo
from ...models.fornecedor import Fornecedor
from .forms import VeiculoForm
from ...services.id_generator import generate_id
from ...utils.logger import setup_logger
import mysql.connector
import os
from werkzeug.utils import secure_filename

logger = setup_logger()

@veiculos_bp.route('/veiculos', methods=['GET', 'POST'])
def listar_veiculos():
    form = VeiculoForm()
    veiculos = Veiculo.listar_todos()
    if form.validate_on_submit():
        try:
            id_veiculo = generate_id('veiculos')
            sequencial = Veiculo.gerar_sequencial()

            # Processar upload das fotos
            foto1_filename = None
            foto2_filename = None
            if form.foto1.data:
                foto = form.foto1.data
                extensao = os.path.splitext(foto.filename)[1].lower()
                foto1_filename = secure_filename(f"{form.placa.data}_{form.ativo.data}_1{extensao}")
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], foto1_filename)
                foto.save(upload_path)
                logger.info(f"Foto 1 salva em {upload_path}")
            if form.foto2.data:
                foto = form.foto2.data
                extensao = os.path.splitext(foto.filename)[1].lower()
                foto2_filename = secure_filename(f"{form.placa.data}_{form.ativo.data}_2{extensao}")
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], foto2_filename)
                foto.save(upload_path)
                logger.info(f"Foto 2 salva em {upload_path}")

            veiculo = Veiculo(
                id=id_veiculo,
                id_fornecedor=form.id_fornecedor.data,
                placa=form.placa.data,
                ativo=form.ativo.data,
                status=form.status.data,
                sequencial=sequencial,
                foto1=foto1_filename,
                foto2=foto2_filename
            )
            veiculo.salvar()
            flash('Veículo cadastrado com sucesso!', 'success')
            return redirect(url_for('veiculos.listar_veiculos'))
        except Exception as e:
            flash(f'Erro ao cadastrar veículo: {str(e)}', 'danger')
            logger.error(f"Erro ao cadastrar veículo: {str(e)}")
    return render_template('veiculos/index.html', form=form, veiculos=veiculos)

@veiculos_bp.route('/veiculos/editar/<string:id>', methods=['GET', 'POST'])
def editar_veiculo(id):
    veiculo = Veiculo.buscar_por_id(id)
    if not veiculo:
        flash('Veículo não encontrado!', 'danger')
        return redirect(url_for('veiculos.listar_veiculos'))
    form = VeiculoForm(obj=veiculo, id_fornecedor=veiculo.id_fornecedor, status=veiculo.status, ativo=veiculo.ativo)
    if form.validate_on_submit():
        try:
            foto1_filename = veiculo.foto1
            foto2_filename = veiculo.foto2
            if form.foto1.data:
                foto = form.foto1.data
                extensao = os.path.splitext(foto.filename)[1].lower()
                foto1_filename = secure_filename(f"{form.placa.data}_{form.ativo.data}_1{extensao}")
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], foto1_filename)
                foto.save(upload_path)
                logger.info(f"Nova foto 1 salva em {upload_path}")
            if form.foto2.data:
                foto = form.foto2.data
                extensao = os.path.splitext(foto.filename)[1].lower()
                foto2_filename = secure_filename(f"{form.placa.data}_{form.ativo.data}_2{extensao}")
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], foto2_filename)
                foto.save(upload_path)
                logger.info(f"Nova foto 2 salva em {upload_path}")

            veiculo.id_fornecedor = form.id_fornecedor.data
            veiculo.placa = form.placa.data
            veiculo.ativo = form.ativo.data
            veiculo.status = form.status.data
            veiculo.foto1 = foto1_filename
            veiculo.foto2 = foto2_filename
            veiculo.atualizar()
            flash('Veículo atualizado com sucesso!', 'success')
            return redirect(url_for('veiculos.listar_veiculos'))
        except Exception as e:
            flash(f'Erro ao atualizar veículo: {str(e)}', 'danger')
            logger.error(f"Erro ao atualizar veículo: {str(e)}")
    return render_template('veiculos/edit.html', form=form, veiculo=veiculo)

@veiculos_bp.route('/veiculos/deletar/<string:id>', methods=['POST'])
def deletar_veiculo(id):
    try:
        veiculo = Veiculo.buscar_por_id(id)
        if veiculo:
            for foto in [veiculo.foto1, veiculo.foto2]:
                if foto:
                    foto_path = os.path.join(current_app.config['UPLOAD_FOLDER'], foto)
                    if os.path.exists(foto_path):
                        os.remove(foto_path)
                        logger.info(f"Foto {foto_path} removida")
            veiculo.deletar()
            flash('Veículo deletado com sucesso!', 'success')
        else:
            flash('Veículo não encontrado!', 'danger')
    except Exception as e:
        flash(f'Erro ao deletar veículo: {str(e)}', 'danger')
        logger.error(f"Erro ao deletar veículo: {str(e)}")
    return redirect(url_for('veiculos.listar_veiculos'))