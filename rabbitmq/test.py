import pika

connection = pika.BlockingConnection(parameters=pika.ConnectionParameters(
port=5672, host='localhost', virtual_host='test_vhost',
credentials=pika.PlainCredentials(username='test_user', password='test_password')))

channel = connection.channel()
queue = channel.queue_declare(queue='some-queue', exclusive=False)
def callback_method(request, method, queue, data):
    print(request, method, queue, data)

channel.basic_consume(queue=queue.method.queue, on_message_callback=callback_method)
channel.start_consuming()