import json
import logging

import tornado.web

from models import Jobs
from models import Profits
from util.executor import run_async

LOGGER = logging.getLogger(__name__)


class ProfitsHandler(tornado.web.RequestHandler):
    """
    Subclass of ``tornado.web.RequestHandler`` which handles HTTP requests to
    ``/profits`` API endpoint.
    """

    @property
    def database_client(self):
        return self.application.database_client

    @property
    def rabbitmq_client(self):
        return self.application.rabbitmq_client

    def prepare(self):
        self.set_header('Content-Type', 'application/json')

    async def get(self):
        LOGGER.info('*** GET %s (%s)', self.request.uri, self.request.remote_ip)
        with self.database_client.session_factory.auto_session() as session:
            profits = await run_async(session.query(Profits).all)
            response = [profit.dict for profit in profits]
            response_json = json.dumps(response, sort_keys=True)
            self.write(response_json)

    async def post(self, *args, **kwargs):
        LOGGER.info('*** POST %s (%s)', self.request.uri, self.request.remote_ip)
        with self.database_client.session_factory.auto_session() as session:
            jobs = await run_async(session.query(Jobs).all)
            jobs = [job.dict for job in jobs]
            profits = await self.rabbitmq_client.call('count_profits', jobs)
            session.bulk_insert_mappings(Profits, profits)
