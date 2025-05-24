# app/services/image_generator.py
from PIL import Image, ImageDraw, ImageFont
import os
from flask import current_app
from ..utils.logger import setup_logger
from ..models.fornecedor import Fornecedor

logger = setup_logger()

def generate_vehicle_image(vehicle):
    """
    Gera uma imagem PNG (9:16) com informações do veículo, ajustada para máxima legibilidade.

    Args:
        vehicle: Instância de Veiculo com id, id_fornecedor, placa, ativo, status, sequencial, foto1, foto2.

    Returns:
        str: Caminho relativo do arquivo da imagem gerada (ex.: 'output/veiculos/veiculo_<id>.png').

    Raises:
        ValueError: Se as configurações ou arquivos necessários estiverem ausentes.
        Exception: Para outros erros durante a geração da imagem.
    """
    try:
        # Validar configurações
        if not current_app.config.get('VEICULO_IMAGE_DIR'):
            raise ValueError("VEICULO_IMAGE_DIR não configurado")
        if not current_app.config.get('UPLOAD_FOLDER'):
            raise ValueError("UPLOAD_FOLDER não configurado")
        if not current_app.config.get('SAFRA'):
            raise ValueError("SAFRA não configurado")

        # Configurações da imagem (9:16, 1080x1920)
        width, height = 1080, 1920
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)

        # Carregar fonte (usar fonte padrão se arial não disponível)
        try:
            font = ImageFont.truetype('arial.ttf', 60)  # Tamanho base ajustado
        except IOError:
            font = ImageFont.load_default()
            logger.warning("Fonte arial.ttf não encontrada; usando fonte padrão")

        # Posições iniciais
        y_position = 50
        x_margin = 40  # Margem de 40px nas laterais
        text_width = width - (2 * x_margin)  # Largura disponível para texto (1000px)

        # Informações a serem exibidas
        safra = current_app.config['SAFRA']
        fornecedor = Fornecedor.buscar_por_id(vehicle.id_fornecedor)
        fornecedor_nome = fornecedor.nome if fornecedor else 'Desconhecido'

        # Ajustar tamanho da fonte dinamicamente com base no comprimento do fornecedor
        max_font_size = 60
        while True:
            left, top, right, bottom = draw.textbbox((0, 0), fornecedor_nome, font=font)
            text_height = bottom - top
            if right - left <= text_width and y_position + text_height <= height:
                break
            max_font_size -= 5
            if max_font_size < 20:  # Limite mínimo legível
                logger.warning("Tamanho da fonte reduzido ao limite mínimo devido ao comprimento do fornecedor")
                break
            font = ImageFont.truetype('arial.ttf', max_font_size) if 'arial.ttf' in locals() else ImageFont.load_default()

        # Desenhar Safra
        draw.text((x_margin, y_position), f"Safra: {safra}", fill='black', font=font)
        y_position += 80  # Espaçamento após safra

        # Desenhar Status com cor condicional usando o mesmo font ajustado
        status_text = "LIBERADO" if vehicle.status == "ok" else vehicle.status.upper()
        status_color = 'green' if vehicle.status == "ok" else 'red'
        draw.text((x_margin, y_position), status_text, fill=status_color, font=font)
        y_position += 100  # Espaçamento maior para destacar status

        # Desenhar demais informações
        infos = [
            f"Placa: {vehicle.placa}",
            f"Ativo: {vehicle.ativo}",
            f"Fornecedor: {fornecedor_nome}",
            f"Sequencial: {vehicle.sequencial}"
        ]
        for info in infos:
            draw.text((x_margin, y_position), info, fill='black', font=font)
            y_position += 80  # Espaçamento uniforme

        # Adicionar fotos (redimensionar para 1080x720 cada)
        photo_width, photo_height = 1080, 720
        total_photo_height = photo_height * 2 + 50  # 50px de espaçamento entre fotos
        if y_position + total_photo_height > height:
            logger.warning(f"Espaço insuficiente para ambas as fotos em {vehicle.id}; ajustando layout")
            photo_height = (height - y_position - 50) // 2  # Dividir espaço restante
            photo_width = int((photo_height / 720) * 1080)  # Manter proporção 3:2

        for idx, photo in enumerate([vehicle.foto1, vehicle.foto2], 1):
            if photo:
                photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo)
                if os.path.exists(photo_path):
                    try:
                        img = Image.open(photo_path).convert('RGB')
                        # Manter proporção 3:2, ajustando para largura máxima
                        img_ratio = img.width / img.height
                        if img_ratio > 1.5:  # Ajustar se a imagem for mais larga
                            img = img.resize((photo_width, int(photo_width / img_ratio)), Image.Resampling.LANCZOS)
                        else:
                            img = img.resize((int(photo_height * img_ratio), photo_height), Image.Resampling.LANCZOS)
                        # Centralizar horizontalmente
                        paste_x = (width - img.width) // 2
                        image.paste(img, (paste_x, y_position))
                        y_position += img.height + 50  # Espaçamento de 50px
                    except Exception as e:
                        logger.error(f"Erro ao processar foto {idx} do veículo {vehicle.id}: {str(e)}")
                        draw.text((x_margin, y_position), f"Erro na Foto {idx}", fill='red', font=font)
                        y_position += 80
                else:
                    logger.warning(f"Foto {photo_path} não encontrada para veículo {vehicle.id}")
                    draw.text((x_margin, y_position), f"Foto {idx} Não Encontrada", fill='black', font=font)
                    y_position += 80
            else:
                draw.text((x_margin, y_position), f"Sem Foto {idx}", fill='black', font=font)
                y_position += 80

        # Criar diretório de saída, se não existir
        output_dir = current_app.config['VEICULO_IMAGE_DIR']
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Diretório de saída criado: {output_dir}")

        # Salvar imagem
        filename = f"veiculo_{vehicle.id}.png"
        output_path = os.path.join(output_dir, filename)
        image.save(output_path, 'PNG')
        logger.info(f"Imagem gerada para veículo {vehicle.id} em {output_path}")

        # Retornar caminho relativo para uso em templates ou mensagens
        relative_path = os.path.join('output/veiculos', filename).replace('\\', '/')
        return relative_path

    except ValueError as ve:
        logger.error(f"Configuração inválida ao gerar imagem para veículo {vehicle.id}: {str(ve)}")
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar imagem para veículo {vehicle.id}: {str(e)}")
        raise