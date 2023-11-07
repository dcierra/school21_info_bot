from connect_db import session
from db_utils.models.user import User


def get_user(user_id):
    user = session.query(User).filter(User.id == user_id).first()
    return user
