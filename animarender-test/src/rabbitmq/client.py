import json
import logging
import uuid

import pika
import tornado.concurrent

from rabbitmq.data import build_request

LOGGER = logging.getLogger(__name__)


class RabbitMQClient:
    """
    Implements asynchronous RPC producer on top of RabbitMQ. It sends requests
    to ``CLIENT_QUEUE`` message queue and waits asynchronously for responses
    to ``SERVER_QUEUE`` message queue.
    """

    CLIENT_QUEUE = 'client_queue'  # From the core to the service.
    SERVER_QUEUE = 'server_queue'  # From the service to the core.

    def __init__(self, host='localhost', port=5672, username='guest', password='guest'):
        """
        Creates a new instance of ``RabbitMQClient`` with specified connection
        parameters and user credentials.

        :param str host: RabbitMQ server host name or IP address.
        :param int port: RabbitMQ server port.
        :param str username: RabbitMQ username.
        :param str password: RabbitMQ password.
        """
        self._host = host
        self._port = port
        self._username = username
        self._password = password

        self._connection = pika.TornadoConnection(
            pika.ConnectionParameters(
                host=self._host,
                port=self._port,
                credentials=pika.PlainCredentials(
                    username=self._username,
                    password=self._password,
                ),
            ),
            on_open_callback=self._on_connection_open,
            on_open_error_callback=self._on_connection_open_error,
        )
        self._channel = None
        self._client_queue = None
        self._server_queue = None
        self._pending_requests = dict()

    def call(self, method, *args, **kwargs):
        """
        Sends and RPC request to ``SERVER_QUEUE`` message queue and returns
        ``tornado.concurrent.Future`` with the result of this request.

        :param str method: Method to call.
        :param args: Method arguments.
        :param kwargs: Method keyword arguments.
        :return tornado.concurrent.Future: Future with response object.
        """
        request = build_request(method, *args, **kwargs)
        request_id = str(uuid.uuid4())
        request_json = json.dumps(request)
        request_future = tornado.concurrent.Future()
        self._pending_requests[request_id] = request_future

        LOGGER.info('Sending a request "%s" to RabbitMQ (ID: %s)', method, request_id)
        self._channel.basic_publish(
            exchange='',
            routing_key=self._client_queue,
            body=request_json,
            properties=pika.BasicProperties(
                content_type='application/json',
                correlation_id=request_id,
            )
        )

        return request_future

    def _on_connection_open(self, connection):
        """
        This method is called when connection to RabbitMQ server is
        successfully opened.

        :param pika.Connection connection: Connection instance.
        """
        LOGGER.info('Connection to %s:%s opened', self._host, self._port)
        LOGGER.info('Opening a new channel')
        connection.channel(on_open_callback=self._on_channel_open)

    def _on_connection_open_error(self, connection, reason):
        """
        This method is called when connection to RabbitMQ server failed
        to open for some ``reason``.

        :param pika.Connection connection: Connection instance.
        :param str reason: The reason why connection failed to open.
        """
        LOGGER.info(reason)

    def _on_channel_open(self, channel):
        """
        This method is called when a new channel is successfully opened.
        Declares ``CLIENT_QUEUE`` and ``SERVER_QUEUE`` message queues.

        :param pika.Channel channel: Channel instance.
        """
        LOGGER.info('Channel opened')
        self._channel = channel

        LOGGER.info('Declaring "%s" queue', self.CLIENT_QUEUE)
        self._channel.queue_declare(
            callback=self._on_client_queue_declared,
            queue=self.CLIENT_QUEUE,
        )

        LOGGER.info('Declaring "%s" queue', self.SERVER_QUEUE)
        self._channel.queue_declare(
            callback=self._on_server_queue_declared,
            queue=self.SERVER_QUEUE,
        )

    def _on_client_queue_declared(self, frame):
        """
        This method is called when ``CLIENT_QUEUE`` is declared successfully.
        It exists mostly for consistency with ``_on_server_queue_declared``.

        :param pika.frame.Method frame: Frame for ``Queue.DeclareOk`` method.
        """
        self._client_queue = frame.method.queue
        LOGGER.info('Successfully declared "%s" queue', self._client_queue)

    def _on_server_queue_declared(self, frame):
        """
        This method is called when ``SERVER_QUEUE`` is declared successfully.
        Subscribes for responses from RPC server.

        :param pika.frame.Method frame: Frame for ``Queue.DeclareOk`` method.
        """
        self._server_queue = frame.method.queue
        LOGGER.info('Successfully declared "%s" queue', self._server_queue)

        self._channel.basic_consume(
            consumer_callback=self._consumer_callback,
            queue=self._server_queue,
            no_ack=True,
        )
        LOGGER.info('Listening to "%s" queue', self._server_queue)

    def _consumer_callback(self, channel, method, properties, body):
        """
        This method is called when a new message is received on ``CLIENT_QUEUE``
        message queue. It resolves a future instance corresponding
        to the original request ID.

        :param pika.Channel channel: Receiving channel.
        :param pika.spec.Basic.Deliver method: Message deliver.
        :param pika.spec.BasicProperties properties: Message properties.
        :param bytes body: Message body.
        """
        response_json = body.decode()
        response = json.loads(response_json)
        response_id = properties.correlation_id
        LOGGER.info('Received a response (ID: %s)', response_id)
        request = self._pending_requests.get(response_id)
        if request is not None:
            request.set_result(response)
            self._pending_requests.pop(response_id)
