import os
import uuid
from argon2 import PasswordHasher
from db import connect
from datetime import datetime, timedelta

class NotAuthenticated(Exception):
    def __init__(self, message):
        Exception.__init__(self)
        self.status_code = 401 # Unauthorized
        self.message = message

def is_protected():
    password_hash = os.environ.get('EXPLOSIG_PASSWORD_HASH')
    return (password_hash != None and len(password_hash) > 0)

def login(password):
    if is_protected():
        table, conn = connect('auth')
        # Try to verify the password
        try:
            ph = PasswordHasher()
            ph.verify(os.environ['EXPLOSIG_PASSWORD_HASH'], password)
            # Password is correct, generate token, insert into database
            token = str(uuid.uuid4())
            ins = table.insert().values(token=token, created=datetime.now())
            conn.execute(ins)
            # Success
            return { "token": token }
        except:
            # Failure
            raise NotAuthenticated('Authentication failed. Please try again.')


def check_token(req):
    if is_protected():
        try:
            token = req['token']
            table, conn = connect('auth')
            # Look up the token in the database
            sel = table.select().where(table.c.token == token)
            res = conn.execute(sel)
            row = res.fetchone()
            if row != None:
                # If a row for the token was found, check when it was created
                if (datetime.now() - row['created']) < timedelta(days=7):
                    # If less than 7 days ago, succeed
                    return True
                else:
                    # If more than 7 days ago, delete the token, allow to fail
                    sel = table.delete().where(table.c.token == token)
                    conn.execute(sel)
        except:
            pass
        raise NotAuthenticated('Authentication failed. Please try again.')

def logout(token):
    if is_protected():
        table, conn = connect('auth')
        # If a logout was requested, proceed to delete the token
        sel = table.delete().where(table.c.token == token)
        conn.execute(sel)