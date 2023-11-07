from sqlalchemy.exc import IntegrityError

from db_utils.models.user import User
from connect_db import session
from SchoolParser.Credentials import GetCredentials


async def registration(data, message):
    login = data['login']
    password = data['password']

    gc = GetCredentials(auth_login=login, auth_password=password)

    try:
        school_id = gc.get_school_id()
        token_id = gc.get_token_id()
    except:
        return False

    user = User(id=int(message.from_user.id), login=login, password=password, school_id=school_id, token_id=token_id)

    session.add(user)

    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False
