import datetime
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase, create_session
from sqlalchemy import orm


class Posts(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    author = sqlalchemy.Column(sqlalchemy.Integer,
                               sqlalchemy.ForeignKey("users.id"))
    category = sqlalchemy.Column(sqlalchemy.Integer,
                                 sqlalchemy.ForeignKey("categories.id"), default=0)
    name_post = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content_post = sqlalchemy.Column(sqlalchemy.String)
    publication_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                         default=datetime.datetime.now)
    price = sqlalchemy.Column(sqlalchemy.Integer, default=None)
    is_hidden = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    count_views = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    url_photo = sqlalchemy.Column(sqlalchemy.String)
    user = orm.relationship('User')
    categories = orm.relationship('Category')
