from database.meta import DeclarativeBase
from database.session import SessionFactory


class DatabaseClient:
    def __init__(self, host, port, username, password, database):
        self._session_factory = SessionFactory(
            'mysql+mysqlconnector://{}:{}@{}:{}/{}'
            .format(username, password, host, port, database))
        self._create_tables()

    @property
    def session_factory(self):
        return self._session_factory

    def _create_tables(self):
        DeclarativeBase.metadata.create_all(self._session_factory.engine)

    @staticmethod
    def load_models():
        """
        Loads application models.
        Every model class should be imported here to be available for
        SQLAlchemy Declarative Mapper and Alembic automatic revisions.
        Note: this import may look like unused, but it is intentional.
        DO NOT delete this import or this entire method.
        """
        from models.jobs import Jobs
        from models.profits import Profits