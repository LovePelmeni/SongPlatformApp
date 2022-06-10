import pika

RABBITMQ_HOST = 'localhost'
RABBITMQ_USER = 'rabbitmq_user'
RABBITMQ_PASSWORD = 'rabbitmq_password'
RABBITMQ_PORT = '5671'
RABBITMQ_VHOST = 'rabbitmq_vhost'

def response_handler(queue, method, properties, body):
    print('responded with success.')


data = {}

connection = pika.BlockingConnection(parameters=pika.ConnectionParameters(
credentials=(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD),
host=settings.RABBITMQ_HOST, port=settings.RABBITMQ_PORT, virtual_host=settings.RABBITMQ_VHOST)).channel()

connection.basic_publish(exchange='exchange',
routing_key='customer_create', body=json.dumps({'data': data}).encode('utf-8'))



