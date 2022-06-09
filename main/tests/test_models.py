from django.test import TestCase, override_settings
import pytest
from django import test
try:
    from VideoHost.main import models
except(ImportError,):
    import models

@pytest.fixture(scope='module')
def client():
    yield test.Client(enforce_csrf_checks=True)

pytest_plugins = "pytester" # it let pytest know that this plugin
# is being used and includes it to the module plugins.


class AutomatedModelTestCase(TestCase):

    """
    / * Automates model testing. Does Not depends on models quantity
    """

    def setUp(self) -> None:
        from django.apps import apps
        self.models = [model.__class__.__name__ for model
        in apps.get_models(include_auto_created=True)]

    def test_model_creation(self, testdir):
        for model in self.models:
            testdir.makepyfile("""
                import pytest 
                from VideoHost.main import models 
                
                creation_data = {}
                @parameterized.expand([creation_data])
                def test_create_%s(creation_data):
                    models.%s.objects.create(**creation_data)
                    assert len(models.%s.objects.all()) == 1
            """ % (model, model, model))
            result_output = testdir.runytest('-vv')
            assert result_output.stdout.files[-4:-2] == [
                u'test_model_creation.py::test_create_%s PASSED' % model
            ]

    def test_model_update(self, testdir):
        for model in self.models:
            testdir.makepyfile("""
                import pytest
                from VideoHost.main import models 
                data = {}
                model_obj = models.%s.objects.create(**data)
                updated_data = {}
                
                @parameterized.expand([updated_data])
                def test_update_%s(updated_data):
                    for element, value in updated_data.items():
                        model_obj.__setattr__(element, value)
                    model_obj.save()
                    assert model_obj
                    
            """ % (model, model))
            result_output = testdir.runytest('-vv')
            assert result_output.stdout.files[-4:-2] == [
                u'test_model_update.py::test_update_%s PASSED' % model
            ]

    def test_model_delete(self, testdir):
        for model in self.models:
            testdir.makepyfile("""
            
                import pytest, django.core.exceptions 
                from VideoHost.main import models 
                
                data = {}
                model_obj = models.%s.objects.create(**data)

                @parameterized.expand([model_obj.id])
                def test_delete_%s(model_obj_id):
                    try:
                        models.%s.objects.delete(id=1)
                        assert not len(models.%s.objects.all())
                    except(django.core.exceptions.ObjectDoesNotExist):
                        raise NotImplementedError()

            """ % (model, model, model, model))
            result_output = testdir.runytest('-vv')
            assert result_output.stdout.files[-4:-2] == [
                u'test_model_delete.py::test_delete_%s PASSED' % model
            ]


# class TestUserModel(TestCase):
#
#     def setUp(self):
#         self.data = {'username': 'some-username', 'password': 'some-password',
#         'phone_number': 'some_phone_number'}
#         self.user = models.CustomUser.objects.create(**self.data)
#
#     @parameterized.expand([])
#     def test_create_user(self, user_data):
#         models.CustomUser.objects.create(**user_data)
#         self.assertEquals(len(models.CustomUser.objects.all()), 2)
#
#     @parameterized.expand([])
#     def test_update_user(self, updated_data: dict):
#         for element, value in updated_data.items():
#             self.user.__setattr__(element, value)
#         self.user.save()
#         self.assertAlmostEqual(first=self.user.username, second=updated_data.get('username'))
#
#     @parameterized.expand([])
#     def test_delete_user(self, user_id):
#         models.CustomUser.objects.delete(id=user_id)
#         self.assertEqual(len(models.CustomUser.objects.all()), 1)
#
#
#
# class TestSongModel(TestCase):
#
#     def setUp(self):
#         self.data = {'username': 'some-username', 'password': 'some-password',
#                      'phone_number': 'some-phone_number'}
#
#     @parameterized.expand([])
#     def test_create_user(self, user_data):
#         models.CustomUser.objects.create(**user_data)
#         self.assertEquals(len(models.CustomUser.objects.all()), 2)
#
#     @parameterized.expand([])
#     def test_update_user(self, updated_data: dict):
#         for element, value in updated_data.items():
#             self.user.__setattr__(element, value)
#         self.user.save()
#         self.assertAlmostEqual(first=self.user.username, second=updated_data.get('username'))
#
#     @parameterized.expand([])
#     def test_delete_user(self, user_id):
#         models.CustomUser.objects.delete(id=user_id)
#         self.assertEqual(len(models.CustomUser.objects.all()), 1)
#
#
# class TestSubscriptionModel(TestCase):
#
#     def setUp(self):
#         self.data = {'username': 'some-username', 'password': 'some-password',
#                      'phone_number': 'some-phone_number'}
#
#     @parameterized.expand([])
#     def test_create_user(self, user_data):
#         models.CustomUser.objects.create(**user_data)
#         self.assertEquals(len(models.CustomUser.objects.all()), 2)
#
#     @parameterized.expand([])
#     def test_update_user(self, updated_data: dict):
#         for element, value in updated_data.items():
#             self.user.__setattr__(element, value)
#         self.user.save()
#         self.assertAlmostEqual(first=self.user.username, second=updated_data.get('username'))
#
#     @parameterized.expand([])
#     def test_delete_user(self, user_id):
#         models.CustomUser.objects.delete(id=user_id)
#         self.assertEqual(len(models.CustomUser.objects.all()), 1)
#
#
# class TestAlbumModel(TestCase):
#
#     def setUp(self):
#         self.data = {'username': 'some-username', 'password': 'some-password',
#                      'phone_number': 'some-phone_number'}
#
#     @parameterized.expand([])
#     def test_create_subscription(self, user_data):
#         models.CustomUser.objects.create(**user_data)
#         self.assertEquals(len(models.CustomUser.objects.all()), 2)
#
#     @parameterized.expand([])
#     def test_update_subscription(self, updated_data: dict):
#         for element, value in updated_data.items():
#             self.user.__setattr__(element, value)
#         self.user.save()
#         self.assertAlmostEqual(first=self.user.username, second=updated_data.get('username'))
#
#     @parameterized.expand([])
#     def test_delete_subscription(self, user_id):
#         models.CustomUser.objects.delete(id=user_id)
#         self.assertEqual(len(models.CustomUser.objects.all()), 1)
#
#
#
#
#
