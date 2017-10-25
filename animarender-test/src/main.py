#!/usr/bin/python3
import logging

import tornado.ioloop
import tornado.web

import config
from database import DatabaseClient
from handlers import JobsHandler
from rabbitmq import RabbitMQClient

LOGGER = logging.getLogger(__name__)


class Application(tornado.web.Application):
    """
    Main application class. It is responsible for connecting to RabbitMQ server
    and for performing RPC requests to the Deadline service.
    Provides main application entry point (see: ``launch``).
    """

    def __init__(self):
        """
        Creates a new instance of ``Application``, assigns handlers to API
        endpoints and connects to database and RabbitMQ server.
        """
        self._database_client = DatabaseClient(**config.DATABASE_CONFIG)
        self._database_client.load_models()
        self._rabbitmq_client = RabbitMQClient(**config.RABBITMQ_CONFIG)

        handlers = [
            (r'/api/v1/jobs', JobsHandler),
        ]

        super().__init__(handlers, debug=True)
        self.listen(8888)

    @property
    def database_client(self):
        return self._database_client

    @property
    def rabbitmq_client(self):
        return self._rabbitmq_client

    @staticmethod
    def launch():
        """
        Main application entry point. Starts application I/O loop and waits
        forever or until termination.
        """
        io_loop = tornado.ioloop.IOLoop.current()
        try:
            LOGGER.info('Started I/O loop')
            io_loop.start()
        except KeyboardInterrupt:
            io_loop.stop()
            LOGGER.info('Stopped I/O loop')


if __name__ == '__main__':
    logging_format = '%(levelname) -10s %(asctime)s %(name) -30s %(funcName) -35s %(lineno) -5d: %(message)s'
    logging.basicConfig(level=logging.INFO, format=logging_format)
    application = Application()
    application.launch()
