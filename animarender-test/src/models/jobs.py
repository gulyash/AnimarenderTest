import json

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer

from database.meta import DeclarativeBase


class Jobs(DeclarativeBase):
    __tablename__ = 'jobs'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    id = Column(BigInteger, primary_key=True)
    start_time = Column(DateTime)
    completion_time = Column(DateTime)
    nodes_used = Column(Integer)
    passmark = Column(Integer)

    @property
    def dict(self):
        return {
            'id': self.id,
            'start_time': self.start_time.isoformat(),
            'completion_time': self.completion_time.isoformat(),
            'nodes_used': self.nodes_used,
            'passmark': self.passmark,
        }

    @property
    def json(self):
        return json.dumps(self.dict, sort_keys=True)
