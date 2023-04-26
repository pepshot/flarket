import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Category(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'categories'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name_category = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    posts = orm.relationship('Posts', back_populates='categories')

