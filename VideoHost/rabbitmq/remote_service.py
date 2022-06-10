from __future__ import annotations

import pika

RABBITMQ_HOST = 'localhost'
RABBITMQ_USER = 'rabbitmq_user'
RABBITMQ_PASSWORD = 'rabbitmq_password'
RABBITMQ_PORT = '5671'
RABBITMQ_VHOST = 'rabbitmq_vhost'

def send_response(data: bytes, method):
    connection.basic_publish(exchange='exchange', body=data, routing_key=method.reply)

def respond_with_status(quuee, method, prop, body):
    return send_response(data=json.dumps({'status': status, 'body': body}).encode('utf-8'), method=method)

connection = pika.BlockingConnection(parameters=pika.ConnectionParameters(
credentials=(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD),
host=settings.RABBITMQ_HOST, port=settings.RABBITMQ_PORT, virtual_host=settings.RABBITMQ_VHOST)).channel()

connection.basic_consume(on_message_callback=(
lambda queue, method, prop, body: respond_with_status(queue, method, prop, body)), queue='customer_create')


