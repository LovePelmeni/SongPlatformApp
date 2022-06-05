from __future__ import annotations
import typing

import psycopg2
from django.conf import settings
from django.db import transaction

import django.http, logging
from django.middleware import csrf


logger = logging.getLogger(__name__)
import psycopg2._psycopg.connection



class EventTrigger(object):

    """
    /* Class represents trigger, that executes everytime
    new transaction is being inserted in the "failed events" database
    Using PostgresSQL...
    """

    def __init__(self, database_connection: psycopg2._psycopg.connection, trigger: callable):
        self.database_connection = database_connection
        self.trigger = trigger


    def __call__(self, *args, **kwargs):
        self.add_trigger(trigger=kwargs.get('trigger'))


    @staticmethod
    def start_trigger(trigger):
        import celery
        pass


    def add_trigger(self, trigger: callable) -> TriggerException:
        """
        / * Creates new Postgresql Trigger.
        """
        pass

    @staticmethod
    def get_trigger_sql(handler) -> TriggerException:
        """
        / * Returns trigger SQL Command for specific table
        """
        return "CREATE CONSTRAINT TRIGGER %s AFTER INSERT ON %s START PROCEDURE "

    def create_database_trigger(self, database_credentials):
        """
        / * Creates new Postgresql Trigger. by executing sql command.
        """


class EventDatabase(object):

    def __init__(self,
        database_name: str ,
        database_user: str,
        database_password: str,
        database_host: str,
        database_port: int | str
    ):
        self.database_name = database_name
        self.database_user = database_user
        self.database_password = database_password
        self.database_host = database_host
        self.database_port = database_port


    def connect(self) -> typing.Generator:
        import psycopg2
        self.__setattr__('connection', connection)
        yield connection


    def disconnect(self) -> None:
        if not hasattr(self, 'connection'):
            raise AttributeError()
        return


class FailedTransactionHandler(object):

    """
    / * Class Represents the Handler That handles failed transaction.
    / * When Transaction fails to execute. Rabbitmq appends it to the "failed message database",
    then this handler is used to handle this transaction with retries.
    """

    def __init__(self, database_credentials, handlers):
        try:
            self.database_credentials = database_credentials
            self.handlers = handlers
            assert all([callable(handler) for handler in handlers])
        except(AssertionError,):
            logger.debug('not all handlers is callable functions.')


    def __call__(self, **kwargs):
        database = EventDatabase(**kwargs)
        with database.connect() as connection:
            self.add_transaction_handlers(connection)

    def add_transaction_handlers(self, connection):
        try:
            for handler in self.handlers:
                EventTrigger(database_connection=connection, trigger=handler)
            return True
        except() as exception:
            logger.error('[HANDLERS EXCEPTION] %s' % exception)
            raise NotImplementedError


