import re
from uuid import uuid4
from datetime import datetime

from flask import current_app
from markdown import markdown
from markupsafe import escape
from peewee import BooleanField
from peewee import CharField
from peewee import DateTimeField
from peewee import ForeignKeyField
from peewee import TextField
from playhouse.fields import ManyToManyField
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from flaskapi.ext import db

PARAGRAPH_RE = re.compile(r'(?:\r\n|\r|\n){2,}')


def linebreaks(value):
    """
    Convert the given value to a value separated by HTML <br> and <p> tags.
    Also escapes anything that would be HTML.
    Two linebreaks = <p> tag
    One linebreak = <br> tag
    """
    value = str(escape(value))
    paragraphs = PARAGRAPH_RE.split(value)
    iter_paragraphs = ('<p>{}</p>'.format(x.replace('\n', '<br>')) for x in paragraphs)
    return '\n'.join(iter_paragraphs)


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
        self.date_updated = datetime.utcnow()
        super().save(*args, **kwargs)

    def to_dict(self, private=False):
        """
        Convert this model to a dictionary representation.
        Overwrites to add date_created and date_updated fields.
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

    def _get_hash_method(self):
        try:
            return current_app.config['PASSWORD_HASH_METHOD']
        except (RuntimeError, KeyError):
            return 'pbkdf2:sha256:50000'

    @property
    def password(self):
        """Return the hashed password value."""
        return self.password_hash

    @password.setter
    def password(self, value):
        """Set the password to the hashed value."""
        if not value:
            return
        self.password_hash = generate_password_hash(value, method=self._get_hash_method())

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


class Category(TimestampedModel):
    name = CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'categories'
        serialize = ('id', 'name')
        serialize_private = ()
        order_by = ('name',)


class TitleContent(TimestampedModel):
    title = CharField(max_length=250)
    date_published = DateTimeField(null=True)
    content = TextField(null=True)

    class Meta:
        serialize = ('title', 'date_published', 'html')
        serialize_private = ('content', )
        order_by = ('date_published', )

    @classmethod
    def published_filter(cls):
        """Filter to find all published instances."""
        return (cls.date_published) & (cls.date_published < datetime.utcnow())

    @property
    def html(self):
        """Return content as formatted (safe) HTML."""
        return markdown(self.content or '')


class Entry(TitleContent):
    categories = ManyToManyField(Category, related_name='entries')

    class Meta:
        db_table = 'entries'


EntryCategory = Entry.categories.get_through_model()


class Page(TitleContent):
    class Meta:
        db_table = 'pages'
        order_by = ('title', )


class Comment(TimestampedModel):
    author = CharField(max_length=100)
    date_published = DateTimeField(default=datetime.utcnow)
    content = TextField()

    entry = ForeignKeyField(Entry, related_name='comments')

    class Meta:
        db_table = 'comments'
        serialize = ('author', 'date_published', 'html')
        serialize_private = ('content', )
        order_by = ('date_published', )

    @property
    def html(self):
        """Return content as formatted (safe) HTML."""
        return linebreaks(self.content or '')
