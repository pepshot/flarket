from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, FileField
from wtforms import SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired


class EditUserForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия')
    city = StringField('Город проживания', validators=[DataRequired()])
    address = StringField('Адрес')
    number_phone = StringField('Номер телефона')
    is_hidden_contact_info = BooleanField('Скрыть контактную информацию')
    submit = SubmitField('Сохранить')
