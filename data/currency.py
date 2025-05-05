import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Currency(SqlAlchemyBase):
    __tablename__ = 'currency'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    amount = sqlalchemy.Column(sqlalchemy.Integer)
    original_price = sqlalchemy.Column(sqlalchemy.Float)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')
