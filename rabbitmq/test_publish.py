from .test import channel

channel.basic_publish(exchange='', routing_key='some-queue',
body=json.dumps({'Hi': 'There'}))
print('message has been sended...')