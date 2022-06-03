from __future__ import annotations
import typing

from django.conf import settings
from django.db import transaction

import django.http, logging
from django.middleware import csrf


logger = logging.getLogger(__name__)


class DistributedTransactionFailed(BaseException):

    def __init__(self, exception_name, reason):
        self.reason = reason
        self.exception_name = exception_name
        logger.debug('[DISTRIBUTED EXCEPTION]: %s: %s' % (self.exception_name, self.reason))


class DistributedTransactionHandler(object):

    def __init__(self,

    data: typing.Optional[dict],
    query_params: typing.Optional[dict],
    method: typing.Literal["delete", "post"],
    url: str):

        self.data = data
        self.transaction_entry_url = url
        self.query_params = query_params
        self.method = method
        self.session = requests.Session()

    def execute_request(self):
        response = self.session.request(
            url='http://' + settings.PAYMENT_SERVICE_HOST + '8081/' + self.transaction_entry_url,
            timeout=50, headers={'CSRF-Token': csrf._get_new_csrf_string()}, method=self.method,
            params=self.query_params)
        response.raise_for_status()

    @transaction.atomic
    def execute_delete(self):
        try:
            self.execute_request()
        except(requests.exceptions.Timeout):
            logger.error('Payment Service Did not responded. On Delete.')
            transaction.rollback()
            raise DistributedTransactionFailed(exception_name=exception.__class__.__name__,
            reason=exception.args)

    @transaction.atomic
    def execute_update(self):
        pass

    @transaction.atomic
    def execute_create(self):
        import requests
        try:
            self.execute_request()
        except(requests.exceptions.Timeout,):
            logger.error('Payment Service Did not responded. On Create.')

        except() as exception:
            logger.debug('[DISTRIBUTED EXCEPTION]')
            transaction.rollback()
            raise DistributedTransactionFailed(exception_name=exception.__class__.__name__,
            reason=exception.args)








