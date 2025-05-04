from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class AddPropertyForm(FlaskForm):
    type = StringField('Тип', validators=[DataRequired()])
    amount = StringField('Кол-во метров квадратных', validators=[DataRequired()])
    city = StringField('Город', validators=[DataRequired()])
    submit = SubmitField('Купить')
