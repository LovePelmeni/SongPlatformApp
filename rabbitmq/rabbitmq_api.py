from __future__ import annotations

import typing

import pika, json
channel = pika.BlockingConnection(parameters=pika.ConnectionParameters(
host='localhost', port=5671, virtual_host='rabbitmq_vhost',
credentials=pika.PlainCredentials(username='rabbitmq_user', password='rabbitmq_password'))).channel()

xmpp_user_queue = channel.queue_declare(queue='user', exclusive=False)
xmpp_group_queue = channel.queue_declare(queue='user', exclusive=False)

# import logging
# logger = logging.getLogger(__name__)
#
#
# asgiref.sync.sync_to_async(listen_for_incoming_events)
#
# def delivery_callback():
#
# def send_to_queue(queue: typing.Literal["group", "user"], exchange: typing.Literal["group_exchange", "user_exchange"], data: dict | str):
#     data = json.dumps(data).encode('utf-8')
#     channel.basic_publish(routing_key=queue, body=data, exchange=exchange)
#     logger.debug('')
#
#