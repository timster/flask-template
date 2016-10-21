def test_wsgi(mocker):
    create_app = mocker.patch('flaskapi.create_app')
    create_app.return_value = 'fakeapp'

    from flaskapi.wsgi import app

    assert create_app.called
    assert app == 'fakeapp'
