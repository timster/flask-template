from flask import url_for


def test_invalid(client):
    resp = client.json_post(url_for('api.users'), data={})

    assert resp.status_code == 422
    assert 'email' in resp.json['errors']
    assert 'password' in resp.json['errors']
    assert 'username' in resp.json['errors']


def test_invalid_email(client):
    user_data = {
        'username': 'someuser',
        'email': 'invalid-email',
        'password': 'welcome'
    }

    resp = client.json_post(url_for('api.users'), data=user_data)

    assert resp.status_code == 422
    assert 'email' in resp.json['errors']
    assert 'password' not in resp.json['errors']
    assert 'username' not in resp.json['errors']


def test_success(client):
    user_data = {
        'username': 'uniqueuser',
        'email': 'uniqueuser@example.com',
        'password': 'welcome'
    }
    resp = client.json_post(url_for('api.users'), data=user_data)

    assert resp.status_code == 200
    assert resp.json['object']['email'] == user_data['email']
    assert resp.json['object']['username'] == user_data['username']
    assert 'password' not in resp.json
    assert 'password_hash' not in resp.json


def test_duplicate(client):
    user_data = {
        'username': 'uniqueuser2',
        'email': 'uniqueuser2@example.com',
        'password': 'welcome'
    }

    resp = client.json_post(url_for('api.users'), data=user_data)
    assert resp.status_code == 200

    resp = client.json_post(url_for('api.users'), data=user_data)
    assert resp.status_code == 422
    assert 'username' in resp.json['errors']
