from uuid import uuid4
from datetime import datetime

from peewee import BooleanField
from peewee import CharField
from peewee import DateTimeField
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from flaskapi.ext import db


def generate_api_key():
    """Generate a unique API key."""
    return uuid4().hex


class Model(db.Model):
    def __str__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.id)

    def __repr__(self):
        return str(self)

    def to_dict(self, private=False):
        """
        Convert this model to a dictionary representation.
        The private attribute controls whether private fields should be included in the output.
        """
        data = {'id': self.id}
        data.update({key: getattr(self, key) for key in self._meta.serialize})
        if private:
            data.update({key: getattr(self, key) for key in self._meta.serialize_private})
        return data

    class Meta:
        serialize = ()
        serialize_private = ()


class TimestampedModel(Model):
    date_created = DateTimeField(default=datetime.utcnow)
    date_updated = DateTimeField(default=datetime.utcnow)

    def save(self, *args, **kwargs):
        """Save this model with a date_update column."""
        self.date_updated = datetime.utcnow()
        super().save(*args, **kwargs)

    def to_dict(self, private=False):
        """
        Convert this model to a dictionary representation.
        Overwrites parent to add date_created and date_updated fields.
        """
        data = super().to_dict(private=private)
        if private:
            data['date_created'] = self.date_created
            data['date_updated'] = self.date_updated
        return data


class User(TimestampedModel):
    username = CharField(max_length=30, unique=True)
    email = CharField(max_length=250, unique=True)
    password_hash = CharField(max_length=250)
    api_key = CharField(max_length=250, unique=True, default=generate_api_key)
    is_admin = BooleanField(default=False)

    class Meta:
        db_table = 'users'
        serialize = ('username', 'email', 'api_key', 'is_admin')
        serialize_private = ()

    @property
    def password(self):
        """Return the hashed password value."""
        return self.password_hash

    @password.setter
    def password(self, value):
        """Set the password to the hashed value."""
        if not value:
            return
        self.password_hash = generate_password_hash(value)

    def check_password(self, value):
        """Check if the given password is valid for this user."""
        if not value:
            return False
        return check_password_hash(self.password_hash, value)

    def generate_api_key(self):
        """Generate an API key and save it to the api_key field."""
        self.api_key = generate_api_key()

    def check_api_key(self, value):
        """Check if the given API key is valid for this user."""
        if not value:
            return False
        return value == self.api_key
