# app/blueprints/veiculos/forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp, URL
from ...models.fornecedor import Fornecedor

class VeiculoForm(FlaskForm):
    id_fornecedor = SelectField('Fornecedor', validators=[DataRequired()], coerce=str)
    placa = StringField('Placa', validators=[DataRequired(), Length(max=7), Regexp(r'^[A-Z]{3}\d{4}$|^[A-Z]{3}\d[A-Z]\d{2}$', message="Placa deve seguir o formato brasileiro (ex.: ABC1234 ou ABC1D23).")])
    ativo = StringField('Ativo', validators=[DataRequired(), Length(min=1, max=6), Regexp(r'^\d{1,6}$', message="Ativo deve ser um número com até 6 dígitos.")])
    status = SelectField('Status', validators=[DataRequired()], choices=[('ok', 'Ok'), ('bloqueado', 'Bloqueado'), ('desligado', 'Desligado')])
    foto1 = FileField('Foto 1 do Veículo', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], 'Apenas imagens JPG, JPEG ou PNG são permitidas.')])
    foto2 = FileField('Foto 2 do Veículo', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], 'Apenas imagens JPG, JPEG ou PNG são permitidas.')])
    submit = SubmitField('Salvar')

    def __init__(self, *args, **kwargs):
        super(VeiculoForm, self).__init__(*args, **kwargs)
        fornecedores = Fornecedor.listar_todos()
        self.id_fornecedor.choices = [(f.id, f.nome) for f in fornecedores]

class LinkForm(FlaskForm):
    link = StringField('Link', validators=[DataRequired(), URL(message="Por favor, insira um URL válido (ex.: https://exemplo.com).")])
    submit = SubmitField('Seguir para Impressão')