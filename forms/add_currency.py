from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class AddCurrencyForm(FlaskForm):
    name = StringField('Код валюты (USD, EUR, CNY и др.)', validators=[DataRequired()])
    amount = StringField('Кол-во', validators=[DataRequired()])
    submit = SubmitField('Добавить')
