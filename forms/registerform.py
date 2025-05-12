from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import PasswordField, StringField, SubmitField, EmailField, FileField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    image = FileField('Фотография (желательно квадратная)', validators=[FileRequired(), FileAllowed(["png", "jpg", "jpeg"], "Файлы должны быть png, jpg или jpeg")])
    submit = SubmitField('Войти')
