from __future__ import annotations

import unittest, pytest
from django import test
from parameterized import parameterized
try:
    from VideoHost.main import models
except(ImportError, ModuleNotFoundError):
    import models

@pytest.fixture(scope='module')
def client():
    yield test.Client(enforce_csrf_checks=True)



