import tempfile
import os
import base64
import json

from flask.testing import FlaskClient
from flask.wrappers import Response
from peewee_moves import DatabaseManager
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
def app(request):
    temp_database = os.path.join(tempfile.mkdtemp(), 'test.sqlite')
    os.environ['FLASK_DATABASE_URL'] = 'sqlite:///' + temp_database

    app = create_app()
    app.test_client_class = TestClient
    app.response_class = TestResponse

    with app.test_request_context():
        migrations = os.path.join(app.root_path, 'migrations')
        manager = DatabaseManager(app.config['DATABASE'], directory=migrations)
        manager.upgrade()

        yield app


@pytest.fixture()
def client(app):
    with app.test_client() as client:
        yield client
