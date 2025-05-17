from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField, Field
from wtforms.validators import DataRequired, InputRequired


class AddShareForm(FlaskForm):
    company = StringField('Тикер акции (например, AAPL для Apple)', validators=[InputRequired()])
    amount = StringField('Кол-во', validators=[DataRequired()])
    submit = SubmitField('Добавить')
