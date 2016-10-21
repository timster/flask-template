from flask_httpauth import HTTPBasicAuth
from flask_mail import Mail
from playhouse.flask_utils import FlaskDB

auth = HTTPBasicAuth()
db = FlaskDB()
mail = Mail()
