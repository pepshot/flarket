from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms import SubmitField, EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    surname = StringField('Фамилия')
    name = StringField('Имя', validators=[DataRequired()])
    city = StringField('Город проживания', validators=[DataRequired()])
    address = StringField('Адрес',)
    email = EmailField('Email', validators=[DataRequired()])
    number_phone = EmailField('Номер телефона')
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')
