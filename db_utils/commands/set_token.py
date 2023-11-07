from SchoolParser.Credentials import GetCredentials
from connect_db import session
from db_utils.models.user import User


def set_token(user: User):
    gc = GetCredentials(auth_login=user.login, auth_password=user.password)
    user.token_id = gc.get_token_id()
    session.commit()
    return user
