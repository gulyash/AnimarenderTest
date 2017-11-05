import json

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import Integer

from database.meta import DeclarativeBase


class Profits(DeclarativeBase):
    __tablename__ = 'profits'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    id = Column(BigInteger, primary_key=True)
    profit = Column(Integer)

    @property
    def dict(self):
        return {
            'id': self.id,
            'profit': self.profit,
        }

    @property
    def json(self):
        return json.dumps(self.dict, sort_keys=True)