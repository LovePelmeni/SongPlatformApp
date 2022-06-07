
import unittest


class RabbitmqIntegrationTestCase(unittest.TestCase):

    def test_connection_established(self):
        try:
            channel = pika.BlockingConnection(parameters=pika.ConnectionParameters(
            credentials=(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD),
            host=settings.RABBITMQ_HOST, port=settings.RABBITMQ_PORT, virtual_host=settings.RABBITMQ_VHOST)).channel()
            channel.close()
        except(pika.exceptions.ChannelError, pika.exceptions.AMQPChannelError,):
            raise NotImplementedError

class PostgresSQLIntegrationTestCase(unittest.TestCase):

    def test_connection_established(self):
        import socket
        try:
            channel = socket.create_connection(address=(settings.POSTGRES_HOST, settings.POSTGRES_PORT))
            channel.close()
        except(socket.timeout):
            raise NotImplementedError
