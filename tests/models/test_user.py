from flaskapi.models import User


def test_user_api_key(app):
    u = User(username='tim', email='tim@me.com', password='pass', api_key='1234')

    assert not u.check_api_key('')
    assert u.check_api_key(u.api_key)

    u.api_key = 'asdf1234'
    assert u.check_api_key('asdf1234')

    u.generate_api_key()
    assert u.check_api_key(u.api_key)


def test_user_password():
    u = User(username='tim', email='tim@me.com', password='pass')

    assert not u.check_password('')
    assert u.check_password('pass')
    assert u.password == u.password_hash

    u.password = 'derp'
    assert u.check_password('derp')
    assert u.password == u.password_hash

    u.password = None
    assert u.check_password('derp')
    assert u.password == u.password_hash
