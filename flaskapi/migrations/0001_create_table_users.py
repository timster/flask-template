"""
create table users
date created: 2016-10-13 20:36:37.549690
"""


def upgrade(migrator):
    with migrator.create_table('users') as table:
        table.primary_key('id')
        table.datetime('date_created')
        table.datetime('date_updated')
        table.char('username', max_length=30, unique=True)
        table.char('email', max_length=250, unique=True)
        table.char('password_hash', max_length=250)
        table.char('api_key', max_length=250, unique=True)
        table.bool('is_admin')


def downgrade(migrator):
    migrator.drop_table('users')
