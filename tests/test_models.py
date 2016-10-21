from peewee import CharField

from flaskapi.models import Model
from flaskapi.models import TimestampedModel


class FakeUser(TimestampedModel):
    name = CharField(max_length=20)
    ssn = CharField(max_length=10)

    class Meta:
        serialize = ('name',)
        serialize_private = ('ssn',)


def test_model_str():
    obj = Model(id=1)

    assert str(obj) == '<Model 1>'
    assert repr(obj) == '<Model 1>'


def test_model_to_dict():
    obj = Model(id=1)
    data = obj.to_dict()

    assert data['id'] == obj.id


def test_model_to_dict_private():
    obj = TimestampedModel(id=1)
    data = obj.to_dict()

    assert data['id'] == obj.id
    assert 'date_created' not in data
    assert 'date_updated' not in data

    obj = TimestampedModel(id=1)
    data = obj.to_dict(private=True)

    assert data['id'] == obj.id
    assert data['date_created'] == obj.date_created
    assert data['date_updated'] == obj.date_updated


def test_model_to_dict_custom():
    obj = FakeUser(name='timster', ssn='1234567890')
    data = obj.to_dict()

    assert data['name'] == obj.name
    assert 'ssn' not in data
    assert 'date_created' not in data
    assert 'date_updated' not in data

    obj = FakeUser(name='timster', ssn='1234567890')
    data = obj.to_dict(private=True)

    assert data['name'] == obj.name
    assert data['ssn'] == obj.ssn
    assert data['date_created'] == obj.date_created
    assert data['date_updated'] == obj.date_updated
