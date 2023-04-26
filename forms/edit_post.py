from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField
from wtforms import SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired


class EditPostForm(FlaskForm):
    name_post = StringField('Название объявления', validators=[DataRequired()])
    content_post = TextAreaField('Описание')
    price = IntegerField("Цена, ₽", validators=[DataRequired()])
    category = SelectField('Категория')
    is_hidden = BooleanField('Скрыть объявление')
    submit = SubmitField('Сохранить')
