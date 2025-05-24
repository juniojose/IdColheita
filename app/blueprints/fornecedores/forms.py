# app/blueprints/fornecedores/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class FornecedorForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(max=255)])
    pessoa_de_contato = StringField('Pessoa de Contato', validators=[Optional(), Length(max=255)])
    whatsapp = StringField('WhatsApp', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Salvar')