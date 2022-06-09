from django.test import TestCase, TransactionTestCase
from django import test

class BaseRequestEndpointTestCase(TestCase):

    def __new__(cls, **kwargs):
        if cls.setUp and not hasattr(cls, 'pytest_plugins'):
            setattr(cls, __name='pytest_plugins', __value='pytester')
        return super().__new__(**kwargs)

    @pytest.fixture(scope='module')
    def client(self):
        yield test.Client(enforce_csrf_checks=True)

    def test_endpoints(self, testdir, client):
        testdir.makepyfile(
        """
            from django import test 
            from parameterized import parameterized
        
            model_obj_payload = {}
            models.%s.objects.create(**model_obj_payload)
            
            @pytest.fixture(scope='module')
            def client(self):
                yield test.Client(enforce_csrf_checks=True)


            @parameterized.expand([created_data, client])
            def create_%s(created_data: dict, client):
                response = client.post('http://localhost:8000/%s/', timeout=10) 
                self.assertEquals(response.status_code, 200)
                self.assertGreater(len(models.%s.objects.all()), 1)
                
                
            @parameterized.expand([updated_data, obj, client])
            def test_update_endpoint(self, updated_data: dict, obj, client):
                response = client.put('http://localhost:8000/%s/', timeout=10) 
                self.assertEquals(response.status_code, 200)
        
        
            @parameterized.expand([obj_id, client])
            def test_delete_endpoint(self, client):
                response = client.delete('http://localhost:8000/%s/', timeout=10)  
                self.assertEquals(response.status_code, 200)
                self.assertLess(len(models.%s.objects.all()), 1)
                
        """ % (model, model.lower(), model, model, model, model, model)
        )





