from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class AddCryptocurrencyForm(FlaskForm):
    name = StringField("'ID криптовалюты (например, 'bitcoin', 'ethereum' и др.)'", validators=[DataRequired()])
    amount = StringField('Кол-во', validators=[DataRequired()])
    submit = SubmitField('Добавить')
