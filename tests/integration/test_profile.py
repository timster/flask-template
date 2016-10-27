import pytest
from flask import url_for

from flaskapi.models import User

USER_DATA = {
    'username': 'mockuser',
    'email': 'mockuser@example.com',
    'password': 'welcome',
}


@pytest.fixture(scope='function')
def user():
    user, created = User().get_or_create(**USER_DATA)
    return user


def test_not_logged_in(client):
    resp = client.json_get(url_for('api.profile'))
    assert resp.status_code == 401


def test_invalid(client, user):
    auth = (user.username, 'invalid-key')
    resp = client.json_get(url_for('api.profile'), auth=auth)
    assert resp.status_code == 401


def test_profile(client, user):
    auth = (user.username, user.api_key)
    resp = client.json_get(url_for('api.profile'), auth=auth)
    assert resp.status_code == 200
    assert resp.json['object']['email'] == USER_DATA['email']
    assert resp.json['object']['username'] == USER_DATA['username']
    assert 'password' not in resp.json
    assert 'password_hash' not in resp.json


def test_update_invalid(client, user):
    new_data = {
        'email': '32f4sdv@example.com',
        'password': 'newpassword',
        'current_password': 'bad',
    }
    auth = (user.username, user.api_key)
    resp = client.json_post(url_for('api.profile'), data=new_data, auth=auth)
    assert resp.status_code == 422
    assert 'current_password' in resp.json['errors']


def test_update(client, user):
    new_data = {
        'email': 'dfbdfgb@example.com',
        'password': 'newpassword',
        'current_password': USER_DATA['password'],
    }
    auth = (user.username, user.api_key)
    resp = client.json_post(url_for('api.profile'), data=new_data, auth=auth)
    assert resp.status_code == 200
    assert 'errors' not in resp.json
    assert resp.json['object']['email'] == new_data['email']

    # authentication with old password fails
    auth = (user.username, 'welcome')
    resp = client.json_get(url_for('api.profile'), auth=auth)
    assert resp.status_code == 401

    # authentication with new password is great success
    auth = (user.username, 'newpassword')
    resp = client.json_get(url_for('api.profile'), auth=auth)
    assert resp.status_code == 200


def test_delete_invalid(client, user):
    new_data = {
        'current_password': 'bad',
    }
    auth = (user.username, user.api_key)
    resp = client.json_delete(url_for('api.profile'), data=new_data, auth=auth)
    assert resp.status_code == 422
    assert 'current_password' in resp.json['errors']


def test_delete(client, user):
    new_data = {
        'current_password': 'welcome',
    }
    auth = (user.username, user.api_key)
    resp = client.json_delete(url_for('api.profile'), data=new_data, auth=auth)
    assert resp.status_code == 200

    # check to make sure trying to authenticate fails after delete
    auth = (user.username, user.api_key)
    resp = client.json_get(url_for('api.profile'), auth=auth)
    assert resp.status_code == 401
