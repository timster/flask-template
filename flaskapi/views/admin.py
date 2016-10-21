from flask import Blueprint
from peewee_validates import Field
from peewee_validates import ModelValidator
from peewee_validates import validate_email

from flaskapi.ext import auth
from flaskapi.resources import UserResource
from flaskapi.utils.views import View

api = Blueprint('admin', __name__)

user_resource = UserResource(private=True)


class UserValidator(ModelValidator):
    password = Field(str, min_length=6)

    class Meta:
        exclude = ('password_hash', )

    def __init__(self, *args, **kwargs):
        """Overwrite to add email validator."""
        super().__init__(*args, **kwargs)
        self._meta.fields['email'].validators.append(validate_email())


class AdminView(View):
    decorators = [auth.admin_required, auth.login_required]


class UsersView(AdminView):
    def get(self):
        return self.objects(user_resource.serialize_many(user_resource.all()))

    def post(self):
        obj = user_resource.create()
        validator = UserValidator(obj)
        if not validator.validate(self.get_post_data()):
            return self.errors(validator.errors)
        validator.save()
        return self.object(user_resource.serialize(obj))


class UserView(AdminView):
    def get(self, pk):
        return self.object(user_resource.serialize(user_resource.get(pk)))

    def post(self, pk):
        obj = user_resource.get(pk)
        validator = UserValidator(obj)
        if not validator.validate(self.get_post_data()):
            return self.errors(validator.errors)
        validator.save()
        return self.object(user_resource.serialize(obj))

    def delete(self, pk):
        obj = user_resource.get(pk)
        obj.delete_instance()
        return self.object(user_resource.serialize(obj))


UsersView.register(api, '/users', 'users')
UserView.register(api, '/users/<pk>', 'user')
