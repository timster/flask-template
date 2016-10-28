import base64
import json

from flask.testing import FlaskClient
from flask.wrappers import Response
from peewee_moves import get_database_manager
from werkzeug import cached_property
import pytest

from flaskapi import create_app


class TestResponse(Response):
    """Add a json property for easy access during testing."""

    @cached_property
    def json(self):
        return json.loads(self.data.decode('utf-8'))


class TestClient(FlaskClient):
    """Add json_<method> methods to the test client."""

    @staticmethod
    def build_auth_header(username, password):
        hashstring = '{}:{}'.format(username, password)
        return b'Basic %s' % base64.b64encode(hashstring.encode('ascii'))

    def _update_kwargs(self, **kwargs):
        kwargs['content_type'] = 'application/json'

        if 'data' in kwargs:
            kwargs['data'] = json.dumps(kwargs['data'])

        username, password = kwargs.pop('auth', (None, None))
        if username or password:
            headers = kwargs.setdefault('headers', {})
            headers['Authorization'] = self.build_auth_header(username, password)

        return kwargs

    def json_get(self, *args, **kwargs):
        kwargs = self._update_kwargs(**kwargs)
        return self.get(*args, **kwargs)

    def json_post(self, *args, **kwargs):
        kwargs = self._update_kwargs(**kwargs)
        return self.post(*args, **kwargs)

    def json_delete(self, *args, **kwargs):
        kwargs = self._update_kwargs(**kwargs)
        return self.delete(*args, **kwargs)


@pytest.fixture(scope='function')
def app(tmpdir):
    sqlite_file = str(tmpdir.join('test.sqlite'))
    config = {
        'TESTING': True,
        'DATABASE': 'sqlite:///' + sqlite_file,
        'PASSWORD_HASH_METHOD': 'plain',
    }
    app = create_app(config)
    app.test_client_class = TestClient
    app.response_class = TestResponse

    with app.test_request_context():
        get_database_manager(app).upgrade()

        yield app


@pytest.fixture(scope='function')
def client(app):
    with app.test_client() as client:
        yield client
