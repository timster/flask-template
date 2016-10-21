import json

import flask

from flaskapi.utils.views import View


def test_view_dispatch():
    app = flask.Flask(__name__)
    client = app.test_client()

    class CustomView(View):
        def dispatch(self):
            return 'result'

    CustomView.register(app, '/view', 'view')

    assert client.get('/view').data == b'result'


def test_get_post_data():
    app = flask.Flask(__name__)
    client = app.test_client()

    class CustomView(View):
        def post(self):
            data = self.get_post_data()
            return 'hello {}'.format(data['name'])

    CustomView.register(app, '/view', 'view')

    # normal post
    kwargs = {
        'data': {'name': 'tim'},
    }
    assert client.post('/view', **kwargs).data == b'hello tim'

    # json post
    kwargs = {
        'data': json.dumps({'name': 'world'}),
        'content_type': 'application/json'
    }
    assert client.post('/view', **kwargs).data == b'hello world'


def test_custom_response():
    app = flask.Flask(__name__)
    client = app.test_client()

    class CustomView(View):
        def get(self):
            return self.response({'name': 'tim'})

    CustomView.register(app, '/view', 'view')

    resp = client.get('/view')
    data = json.loads(resp.data.decode('utf-8'))
    assert data['name'] == 'tim'


def test_custom_object():
    app = flask.Flask(__name__)
    client = app.test_client()

    class CustomView(View):
        def get(self):
            return self.object({'name': 'tim'})

    CustomView.register(app, '/view', 'view')

    resp = client.get('/view')
    data = json.loads(resp.data.decode('utf-8'))
    assert data['object']['name'] == 'tim'


def test_custom_objects():
    app = flask.Flask(__name__)
    client = app.test_client()

    class CustomView(View):
        def get(self):
            return self.objects({'name': 'tim'})

    CustomView.register(app, '/view', 'view')

    resp = client.get('/view')
    data = json.loads(resp.data.decode('utf-8'))
    assert data['objects']['name'] == 'tim'


def test_custom_errors():
    app = flask.Flask(__name__)
    client = app.test_client()

    class CustomView(View):
        def get(self):
            return self.errors({'name': 'tim'})

    CustomView.register(app, '/view', 'view')

    resp = client.get('/view')
    data = json.loads(resp.data.decode('utf-8'))
    assert data['errors']['name'] == 'tim'
