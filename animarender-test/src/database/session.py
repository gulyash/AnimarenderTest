import sqlalchemy
import sqlalchemy.orm

from contextlib import contextmanager


class SessionFactory:
    """
    SessionFactory is a wrapper around the functions that SQLAlchemy provides.
    The intention here is to let the user work at the session level instead of
    engines and connections.
    """

    def __init__(self, database_url, *args, **kwargs):
        """
        Creates a new instance of ``SessionFactory`` with specified database
        URL to use. Additional positional and keyword arguments are passed
        to ``sqlalchemy.create_engine``.

        :param str database_url: Database URL.
        :param args: Additional arguments.
        :param kwargs: Additional keyword arguments.
        """
        self._engine = sqlalchemy.create_engine(database_url, *args, **kwargs)
        self._session_factory = sqlalchemy.orm.sessionmaker()
        self._session_factory.configure(bind=self._engine)

    @property
    def engine(self):
        """
        Returns an instance of ``sqlalchemy.engine.Engine`` used to connect to
        the database.

        :return sqlalchemy.engine.Engine: The engine.
        """
        return self._engine

    def make_session(self):
        """
        Creates a new SQLAlchemy session.

        :return sqlalchemy.orm.session.Session: The session.
        """
        return self._session_factory()

    @contextmanager
    def auto_session(self):
        """
        Wraps SQLAlchemy session into context manager to use it in Python
        ``with`` statement.

        :return sqlalchemy.orm.session.Session: The session.
        """
        session = None
        try:
            session = self.make_session()
            yield session
        except:
            session.rollback()
            raise
        else:
            session.commit()
        finally:
            session.close()
