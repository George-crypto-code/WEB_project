from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class AddShareForm(FlaskForm):
    company = StringField('Тикер акции (например, AAPL для Apple)', validators=[DataRequired()])
    amount = StringField('Кол-во', validators=[DataRequired()])
    submit = SubmitField('Добавить')
