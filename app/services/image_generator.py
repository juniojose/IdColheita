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

        # Carregar fontes (regular e negrito)
        try:
            font_regular = ImageFont.truetype('arial.ttf', 60)
            font_bold = ImageFont.truetype('arialbd.ttf', 60)
            font_bold_header = ImageFont.truetype('arialbd.ttf', 40)  # Tamanho reduzido para 40 (30% de 60)
        except IOError:
            font_regular = ImageFont.load_default()
            font_bold = ImageFont.load_default()
            font_bold_header = ImageFont.load_default()
            logger.warning("Fontes arial.ttf ou arialbd.ttf não encontradas; usando fonte padrão")

        # Margens e posições iniciais
        x_margin = 40  # Margem lateral
        y_position = 20  # Início do topo
        line_spacing = 20  # Espaçamento entre linhas de texto

        # 1. Cabeçalho: "IDENTIFICADOR DE VEÍCULOS DA COLHEITA"
        header_text = "IDENTIFICADOR DE VEÍCULOS DA COLHEITA"
        header_height = 100  # Altura do fundo do cabeçalho
        draw.rectangle((0, 0, width, header_height), fill=(0, 113, 70))  # Fundo verde
        draw.text((width // 2, header_height // 2), header_text, fill='white', font=font_bold_header, anchor="mm")  # Texto centralizado com fonte reduzida
        y_position = header_height + line_spacing

        # 2. Status com fundo colorido
        status_text = "LIBERADO" if vehicle.status == "ok" else vehicle.status.upper()
        status_color = (0, 113, 70) if vehicle.status == "ok" else (255, 0, 0)  # Verde ou vermelho
        status_height = 80  # Altura do fundo do status
        draw.rectangle((0, y_position, width, y_position + status_height), fill=status_color)
        draw.text((width // 2, y_position + status_height // 2), status_text, fill='white', font=font_bold, anchor="mm")
        y_position += status_height + line_spacing

        # 3. Placa: "Placa: RPX1F19"
        placa_text = f"Placa: {vehicle.placa.upper()}"
        draw.text((x_margin, y_position), "Placa: ", fill='black', font=font_regular)
        placa_x = x_margin + draw.textlength("Placa: ", font=font_regular)
        draw.text((placa_x, y_position), vehicle.placa.upper(), fill='black', font=font_bold)
        y_position += 80 + line_spacing

        # 4. Ativo: "Ativo: 2630"
        ativo_text = f"Ativo: {vehicle.ativo}"
        draw.text((x_margin, y_position), "Ativo: ", fill='black', font=font_regular)
        ativo_x = x_margin + draw.textlength("Ativo: ", font=font_regular)
        draw.text((ativo_x, y_position), str(vehicle.ativo), fill='black', font=font_bold)
        y_position += 80 + line_spacing

        # 5. Fornecedor: "CONFIANÇA CHUPINHA"
        fornecedor = Fornecedor.buscar_por_id(vehicle.id_fornecedor)
        fornecedor_nome = fornecedor.nome.upper() if fornecedor else 'DESCONHECIDO'
        draw.text((x_margin, y_position), fornecedor_nome, fill='black', font=font_bold)
        y_position += 80 + line_spacing

        # 6. Sequencial: "Nº 001"
        sequencial_text = f"Nº {vehicle.sequencial:03d}"
        draw.text((x_margin, y_position), sequencial_text, fill='black', font=font_bold)
        y_position += 80 + line_spacing

        # 7. Adicionar fotos (alinhadas à esquerda, 3px de espaço)
        photo_width, photo_height = 1080, 720
        total_photo_height = photo_height * 2 + 3  # 3px de espaço entre fotos
        if y_position + total_photo_height > height:
            logger.warning(f"Espaço insuficiente para ambas as fotos em {vehicle.id}; ajustando layout")
            photo_height = (height - y_position - 3) // 2  # Dividir espaço restante
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
                        # Alinhar à esquerda
                        paste_x = x_margin
                        image.paste(img, (paste_x, y_position))
                        y_position += img.height + 3  # Espaçamento de 3px
                    except Exception as e:
                        logger.error(f"Erro ao processar foto {idx} do veículo {vehicle.id}: {str(e)}")
                        draw.text((x_margin, y_position), f"Erro na Foto {idx}", fill='red', font=font_regular)
                        y_position += 80
                else:
                    logger.warning(f"Foto {photo_path} não encontrada para veículo {vehicle.id}")
                    draw.text((x_margin, y_position), f"Foto {idx} Não Encontrada", fill='black', font=font_regular)
                    y_position += 80
            else:
                draw.text((x_margin, y_position), f"Sem Foto {idx}", fill='black', font=font_regular)
                y_position += 80

        # 8. Adicionar borda preta de 3px ao redor da imagem
        draw.rectangle((0, 0, width - 1, height - 1), outline='black', width=3)

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