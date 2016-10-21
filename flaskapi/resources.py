from flaskapi.utils.resource import Resource
from flaskapi.models import User


class UserResource(Resource):
    model = User
