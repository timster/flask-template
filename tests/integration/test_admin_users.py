import pytest
from flask import url_for

from flaskapi.models import User

ADMIN_DATA = {
    'username': 'admin',
    'email': 'admin@example.com',
    'password': 'welcome',
}


@pytest.fixture(scope='module')
def user():
    return User().create(is_admin=True, **ADMIN_DATA)


def test_not_logged_in(client):
    resp = client.json_get(url_for('admin.users'))
    assert resp.status_code == 401


def test_not_admin(client):
    user = User.create(username='tim', email='tim@example.com', password='welcome', is_admin=False)

    auth = (user.username, user.api_key)

    resp = client.json_get(url_for('admin.users'), auth=auth)
    assert resp.status_code == 401


def test_list(client, user):
    auth = (user.username, user.api_key)
    resp = client.json_get(url_for('admin.users'), auth=auth)
    assert 'objects' in resp.json


def test_create_success(client, user):
    user_data = {
        'username': 'asdfasdf',
        'email': 'asdfasdf@example.com',
        'password': 'welcome'
    }
    auth = (user.username, user.api_key)
    resp = client.json_post(url_for('admin.users'), data=user_data, auth=auth)

    assert resp.status_code == 200
    assert resp.json['object']['email'] == user_data['email']
    assert resp.json['object']['username'] == user_data['username']
    assert 'password' not in resp.json
    assert 'password_hash' not in resp.json


def test_create_invalid(client, user):
    auth = (user.username, user.api_key)
    resp = client.json_post(url_for('admin.users'), data={}, auth=auth)

    assert resp.status_code == 422
    assert 'email' in resp.json['errors']
    assert 'username' in resp.json['errors']


def test_detail(client, user):
    auth = (user.username, user.api_key)
    resp = client.json_get(url_for('admin.user', pk=user.id), auth=auth)
    assert 'object' in resp.json


def test_update_success(client, user):
    newuser = User.create(username='newuser', email='newuser@example.com', password='welcome', is_admin=False)

    data = {
        'username': 'updateduser'
    }
    auth = (user.username, user.api_key)
    resp = client.json_post(url_for('admin.user', pk=newuser.id), data=data, auth=auth)
    assert 'object' in resp.json
    assert resp.json['object']['username'] == data['username']


def test_update_invalid(client, user):
    user1 = User.create(username='olduser1', email='olduser1@example.com', password='welcome', is_admin=False)
    user2 = User.create(username='olduser2', email='olduser2@example.com', password='welcome', is_admin=False)

    data = {
        'username': user2.username
    }
    auth = (user.username, user.api_key)
    resp = client.json_post(url_for('admin.user', pk=user1.id), data=data, auth=auth)
    assert 'errors' in resp.json
    assert 'username' in resp.json['errors']


def test_delete(client, user):
    newuser = User.create(username='byebye', email='byebye@example.com', password='welcome', is_admin=False)

    auth = (user.username, user.api_key)
    resp = client.json_delete(url_for('admin.user', pk=newuser.id), auth=auth)
    assert 'object' in resp.json
    assert resp.json['object']['username'] == newuser.username
