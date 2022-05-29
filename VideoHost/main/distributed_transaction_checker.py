class RabbitmqContainerNotFound(BaseException):
    pass


class DistributedTransactionHandler(object):

    channel = pika.BlockingConnection(parameters=
    pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        virtual_host=settings.RABBITMQ_VHOST,
        credentials=pika.PlainCredentials(username=settings.RABBITMQ_USER, password=settings.RABBITMQ_PASSWORD)
    )).channel()
    ack_codes = ()

    def __new__(cls, **kwargs):
        cls.consume()
        return super().__new__(**kwargs)

    def get_rabbitmq_container(self, client):
        try:
            for container in client.container.list():
                if client.containers.get(container_id=container.id
                ).name.decode('latin1').decode('utf-8') == self.rabbitmq_container_name:
                    return container
            raise RabbitmqContainerNotFound()
        except(RabbitmqContainerNotFound,):
            raise NotImplementedError

    def get_queues_list(self):
        try:
            import docker
            client = docker.from_env(version='1.4.1')
            rabbitmq_container = self.get_rabbitmq_container(client)
            queues = rabbitmq_container.exec_run(command='rabbitmqctl list_queues')[1]
            return queues
        except(NotImplementedError,):
            logger.error('Rabbitmq Is Not Running.')


    def handle_exception(self, ):
        pass


    def __init__(self):
        self.rabbitmq_container_name = 'rabbitmqserver'
        self.queues = self.get_queues_list()


    @classmethod
    def publish(cls, url_path, method: typing.Literal["user_creation", "user_deletion", "group_deletion", "group_creation"]):
        import requests
        session = qrequests.Session()
        request = session.request(method=method, url_path=url_path, params=params, data=data,
        headers={'Access-Control-Allow-Origin': '*', 'CSRF-Token': ''})
        cls.handle_confirmation(request=request)


    @classmethod
    def handle_confirmation(cls, request):
        response = grequests.map(request)
        if not response.status_code in cls.ack_codes:
            pass

    @classmethod
    def consume(cls):
        import pika
        cls.channel.basic_consume(
        queue='', auto_ack=False, exclusive=False,
        on_message_callback=cls.handle_confirmation
        )
