import pytest
from peewee import SqliteDatabase
from peewee import Model
from peewee import CharField
from werkzeug.exceptions import NotFound

from flaskapi.utils.resource import Resource

memory_database = SqliteDatabase(':memory:')


class FakeUser(Model):
    name = CharField(max_length=10)
    ssn = CharField(max_length=10)

    class Meta:
        db_table = 'fakeusers'
        database = memory_database

    def to_dict(self, private=False):
        data = {'name': self.name}
        if private:
            data['ssn'] = self.ssn
        return data

FakeUser.create_table(fail_silently=True)
user1 = FakeUser.create(name='tim', ssn='timssn')
user2 = FakeUser.create(name='bob', ssn='bobssn')


class MissingModelResource(Resource):
    pass


class UserResource(Resource):
    model = FakeUser


def test_missing_model():
    resource = MissingModelResource()
    with pytest.raises(NotImplementedError):
        resource.all()
    with pytest.raises(NotImplementedError):
        resource.create()


def test_create():
    resource = UserResource()
    obj = resource.create(name='tim')

    assert isinstance(obj, FakeUser)
    assert obj.name == 'tim'


def test_all():
    resource = UserResource()
    objs = resource.all()

    assert user1 in objs
    assert user2 in objs


def test_get():
    resource = UserResource()
    obj = resource.get(1)

    assert obj == user1


def test_get_fail():
    resource = UserResource()
    with pytest.raises(NotFound):
        resource.get(99)


def test_serialize():
    resource = UserResource()
    result = resource.serialize(user1)
    assert result['name'] == user1.name
    assert 'ssn' not in result


def test_serialize_private():
    resource = UserResource(private=True)
    result = resource.serialize(user1)
    assert result['name'] == user1.name
    assert result['ssn'] == user1.ssn


def test_serialize_many():
    resource = UserResource()
    result = resource.serialize_many((user1, user2))

    assert result[0]['name'] == user1.name
    assert 'ssn' not in result[0]


def test_serialize_many_private():
    resource = UserResource(private=True)
    result = resource.serialize_many((user1, user2))
    assert result[0]['name'] == user1.name
    assert result[0]['ssn'] == user1.ssn
