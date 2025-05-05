import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Shares(SqlAlchemyBase):
    __tablename__ = 'shares'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    company = sqlalchemy.Column(sqlalchemy.String)
    amount = sqlalchemy.Column(sqlalchemy.Integer)
    original_price = sqlalchemy.Column(sqlalchemy.Float)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')
