from flask import Blueprint
from flask import g
from peewee_validates import Field
from peewee_validates import ModelValidator
from peewee_validates import validate_email
from peewee_validates import ValidationError

from flaskapi.ext import auth
from flaskapi.resources import UserResource
from flaskapi.utils.views import View

api = Blueprint('api', __name__)

user_resource = UserResource(private=False)


class UserValidator(ModelValidator):
    password = Field(str, required=True, min_length=6)

    class Meta:
        only = ('email', 'username', 'password')

    def __init__(self, *args, **kwargs):
        """Overwrite to add email validator."""
        super().__init__(*args, **kwargs)
        self._meta.fields['email'].validators.append(validate_email())


class ProfileValidator(ModelValidator):
    password = Field(str, min_length=6)
    current_password = Field(str, required=True)

    class Meta:
        only = ('email', 'username', 'password', 'current_password')
        messages = {
            'password': 'must be valid'
        }

    def __init__(self, *args, **kwargs):
        """Overwrite to add email validator."""
        super().__init__(*args, **kwargs)
        self._meta.fields['email'].validators.append(validate_email())

    def clean_current_password(self, value):
        if self.instance and not self.instance.check_password(value):
            raise ValidationError('password')
        return value


class UsersView(View):
    def post(self):
        obj = user_resource.create()
        validator = UserValidator(obj)
        if not validator.validate(self.get_post_data()):
            return self.errors(validator.errors)
        validator.save()
        return self.object(user_resource.serialize(obj))


class ProfileView(View):
    decorators = (auth.login_required, )

    def get(self):
        return self.object(user_resource.serialize(g.user))

    def post(self):
        obj = g.user
        validator = ProfileValidator(obj)
        if not validator.validate(self.get_post_data()):
            return self.errors(validator.errors)
        validator.save()
        return self.object(user_resource.serialize(obj))

    def delete(self):
        obj = g.user
        validator = ProfileValidator(obj)
        if not validator.validate(self.get_post_data(), only=['current_password']):
            return self.errors(validator.errors)
        obj.delete_instance()
        return self.object(user_resource.serialize(obj))


UsersView.register(api, '/users', 'users')
ProfileView.register(api, '/profile', 'profile')
