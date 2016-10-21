import os

SECRET_KEY = os.getenv('FLASK_SECRET_KEY', str(os.urandom(64)))

sqlite_database = os.path.join(os.getcwd(), 'development.sqlite')

DATABASE = os.getenv('FLASK_DATABASE_URL', 'sqlite:///{}'.format(sqlite_database))

LOG_FILE = os.getenv('FLASK_LOG_FILE', os.path.join(os.getcwd(), 'logs', 'app.log'))

ADMINS = os.getenv('FLASK_ADMINS', 'admin@example.com').split(';')

MAIL_SERVER = os.getenv('FLASK_MAIL_SERVER', 'localhost')
MAIL_PORT = int(os.getenv('FLASK_MAIL_PORT', 1025))
MAIL_USE_TLS = os.getenv('FLASK_MAIL_USE_TLS', 'false').lower() in ('1', 'true', 'on')
MAIL_USE_SSL = os.getenv('FLASK_MAIL_USE_SSL', 'false').lower() in ('1', 'true', 'on')
MAIL_USERNAME = os.getenv('FLASK_MAIL_USERNAME', '')
MAIL_PASSWORD = os.getenv('FLASK_MAIL_PASSWORD', '')
MAIL_ERROR_SUBJECT = os.getenv('FLASK_MAIL_ERROR_SUBJECT', 'Application Error')
MAIL_FROM_ADDRESS = os.getenv('FLASK_MAIL_FROM_ADDRESS', 'admin@example.com')
