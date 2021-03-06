def test_config(app):
    assert isinstance(app.config['SECRET_KEY'], str)
    assert isinstance(app.config['DATABASE'], str)
    assert isinstance(app.config['LOG_FILE'], str)
    assert isinstance(app.config['ADMINS'], (list, tuple))
    assert isinstance(app.config['MAIL_SERVER'], str)
    assert isinstance(app.config['MAIL_PORT'], int)
    assert isinstance(app.config['MAIL_USE_TLS'], bool)
    assert isinstance(app.config['MAIL_USE_SSL'], bool)
    assert isinstance(app.config['MAIL_USERNAME'], str)
    assert isinstance(app.config['MAIL_PASSWORD'], str)
    assert isinstance(app.config['MAIL_ERROR_SUBJECT'], str)
    assert isinstance(app.config['MAIL_FROM_ADDRESS'], str)
