import pika, logging
from . import rabbimq_handlers
import asgiref.sync, docker
from django.conf import settings
# when deploy change host to name of the service.

USER_CREATE_QUEUE_NAME = 'user_created'
USER_DELETE_QUEUE_NAME = 'user_deleted'

logger = logging.getLogger(__name__)

try:
    connection = pika.BlockingConnection(parameters=pika.ConnectionParameters(host=settings.RABBITMQ_HOST, port=settings.RABBITMQ_PORT,
    credentials=pika.PlainCredentials(username=settings.RABBITMQ_USER, password=settings.RABBITMQ_PASSWORD),
    virtual_host=settings.RABBITMQ_VHOST))

    channel = connection.channel()

    channel.basic_consume(queue=USER_CREATE_QUEUE_NAME, exclusive=False,
    on_message_callback=rabbimq_handlers.handle_user_creation)

    channel.basic_consume(queue=USER_DELETE_QUEUE_NAME, exclusive=False,
    on_message_callback=rabbimq_handlers.handle_user_deletion)
    asgiref.sync.sync_to_async(channel.start_consuming)

except(pika.exceptions.AMQPConnectionError,) as exception:
    logger.error('CONNECTION EXCEPTION HAS OCCURRED. %s' % exception)
    logger.debug('%s' % exception)






