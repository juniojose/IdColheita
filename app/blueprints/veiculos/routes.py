# app/blueprints/veiculos/routes.py
from flask import render_template, request, redirect, url_for, flash, current_app
from . import veiculos_bp
from ...models.veiculo import Veiculo
from ...models.fornecedor import Fornecedor
from .forms import VeiculoForm, LinkForm
from ...services.id_generator import generate_id
from ...services.image_generator import generate_vehicle_image
from ...utils.logger import setup_logger
import mysql.connector
import os
from werkzeug.utils import secure_filename
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import black
from werkzeug.datastructures import FileStorage  # Importar FileStorage para verificação

logger = setup_logger()

@veiculos_bp.route('/', methods=['GET', 'POST'])
def listar_veiculos():
    form = VeiculoForm()
    veiculos = Veiculo.listar_todos()
    for veiculo in veiculos:
        fornecedor = Fornecedor.buscar_por_id(veiculo.id_fornecedor)
        veiculo.fornecedor_nome = fornecedor.nome if fornecedor else 'Desconhecido'
    if form.validate_on_submit():
        try:
            id_veiculo = generate_id('veiculos')
            sequencial = Veiculo.gerar_sequencial()

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

            try:
                image_path = generate_vehicle_image(veiculo)
                flash(f'Veículo cadastrado e imagem gerada com sucesso em static/{image_path}!', 'success')
            except Exception as e:
                flash(f'Veículo cadastrado, mas erro ao gerar imagem: {str(e)}', 'warning')
                logger.error(f"Erro ao gerar imagem para veículo {id_veiculo}: {str(e)}")

            return redirect(url_for('veiculos.gerar_qr_code', id_veiculo=id_veiculo))
        except Exception as e:
            flash(f'Erro ao cadastrar veículo: {str(e)}', 'danger')
            logger.error(f"Erro ao cadastrar veículo: {str(e)}")
    return render_template('veiculos/index.html', form=form, veiculos=veiculos)

@veiculos_bp.route('/gerar-qr-code/<string:id_veiculo>', methods=['GET', 'POST'])
def gerar_qr_code(id_veiculo):
    veiculo = Veiculo.buscar_por_id(id_veiculo)
    if not veiculo:
        flash('Veículo não encontrado!', 'danger')
        return redirect(url_for('veiculos.listar_veiculos'))

    form = LinkForm()
    if form.validate_on_submit():
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(form.link.data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            qr_dir = os.path.join(current_app.config['VEICULO_IMAGE_DIR'], 'qr_codes')
            os.makedirs(qr_dir, exist_ok=True)
            qr_filename = f"qr_{id_veiculo}.png"
            qr_path = os.path.join(qr_dir, qr_filename)
            img.save(qr_path)
            logger.info(f"QR-Code salvo em {qr_path}")

            pdf_dir = os.path.join(current_app.config['VEICULO_IMAGE_DIR'], 'pdfs')
            os.makedirs(pdf_dir, exist_ok=True)
            pdf_filename = f"id_colheita_{id_veiculo}.pdf"
            pdf_path = os.path.join(pdf_dir, pdf_filename)

            # Criar o PDF (140x80 mm)
            c = canvas.Canvas(pdf_path, pagesize=(140 * mm, 80 * mm))
            width, height = 140 * mm, 80 * mm

            # Definir px_per_mm para conversão
            px_per_mm = 3.7795  # Aproximadamente 300 DPI

            left_margin = 2 * mm  # Margem à esquerda para o texto
            qr_margin = 2 * px_per_mm/mm  # Margem de 5 px (~1.32 mm) à direita do QR-Code
            qr_size = height - 2 * qr_margin  # ~80 mm - 10 px (5 px topo e base)

            # Obter safra corrigida (sem duplicar "SAFRA")
            safra = current_app.config['SAFRA']
            safra_text = safra

            # Informações com tamanhos fixos
            lines = [
                {"text": safra_text, "size": 30, "bold": True},  # Tamanho fixo de 24 px
                {"text": veiculo.placa, "size": 30, "bold": True},
                {"text": veiculo.ativo, "size": 30, "bold": True},
                {"text": f"{veiculo.sequencial:03d}", "size": 42, "bold": True},  # Tamanho fixo de 42 px
            ]

            # Definir espaçamento fixo entre linhas
            #line_spacing = 2 * px_per_mm  # Aproximadamente 10 px de espaçamento
            line_spacing = -70

            # Posicionar o texto a partir de uma margem fixa do topo
            start_y = height - 15 * px_per_mm  # Iniciar a 15 px do topo para centralizar visualmente

            current_y = start_y
            for line in lines:
                font = "Helvetica-Bold" if line["bold"] else "Helvetica"
                c.setFont(font, line["size"])
                c.setFillColor(black)
                c.drawString(left_margin, current_y, line["text"])
                current_y -= line["size"] * px_per_mm + line_spacing

            # QR Code à direita
            qr_image = ImageReader(qr_path)
            qr_x = width - qr_size - qr_margin
            qr_y = qr_margin  # Início a 5 px do topo
            c.drawImage(qr_image, qr_x, qr_y, width=qr_size, height=qr_size)

            c.showPage()
            c.save()
            logger.info(f"PDF finalizado com layout corrigido: {pdf_path}")

            return redirect(url_for('veiculos.imprimir_id_colheita', id_veiculo=id_veiculo))
        except Exception as e:
            flash(f'Erro ao gerar QR-Code ou PDF: {str(e)}', 'danger')
            logger.error(f"Erro ao gerar QR-Code ou PDF: {str(e)}")
    return render_template('veiculos/gerar_qr_code.html', form=form, veiculo=veiculo)

@veiculos_bp.route('/imprimir/<string:id_veiculo>')
def imprimir_id_colheita(id_veiculo):
    veiculo = Veiculo.buscar_por_id(id_veiculo)
    if not veiculo:
        flash('Veículo não encontrado!', 'danger')
        return redirect(url_for('veiculos.listar_veiculos'))

    pdf_filename = f"id_colheita_{id_veiculo}.pdf"
    pdf_relative_path = os.path.join('output/veiculos/pdfs', pdf_filename).replace('\\', '/')
    return render_template('veiculos/imprimir.html', veiculo=veiculo, pdf_path=pdf_relative_path)

@veiculos_bp.route('/editar/<string:id>', methods=['GET', 'POST'])
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
            # Verificar se uma nova foto foi enviada para foto1
            if form.foto1.data and isinstance(form.foto1.data, FileStorage) and form.foto1.data.filename:
                foto = form.foto1.data
                extensao = os.path.splitext(foto.filename)[1].lower()
                foto1_filename = secure_filename(f"{form.placa.data}_{form.ativo.data}_1{extensao}")
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], foto1_filename)
                foto.save(upload_path)
                logger.info(f"Nova foto 1 salva em {upload_path}")
            # Verificar se uma nova foto foi enviada para foto2
            if form.foto2.data and isinstance(form.foto2.data, FileStorage) and form.foto2.data.filename:
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

            # Regenerar a imagem do veículo com os dados atualizados
            try:
                image_path = generate_vehicle_image(veiculo)
                flash(f'Veículo atualizado e imagem gerada com sucesso em static/{image_path}!', 'success')
            except Exception as e:
                flash(f'Veículo atualizado, mas erro ao gerar imagem: {str(e)}', 'warning')
                logger.error(f"Erro ao gerar imagem para veículo {id}: {str(e)}")

            return redirect(url_for('veiculos.listar_veiculos'))
        except Exception as e:
            flash(f'Erro ao atualizar veículo: {str(e)}', 'danger')
            logger.error(f"Erro ao atualizar veículo: {str(e)}")
    return render_template('veiculos/edit.html', form=form, veiculo=veiculo)

@veiculos_bp.route('/deletar/<string:id>', methods=['POST'])
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