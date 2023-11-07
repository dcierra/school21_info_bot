import connect_db
from sqlalchemy import Column, Boolean, String, BigInteger


class User(connect_db.Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    login = Column(String)
    password = Column(String)
    school_id = Column(String)
    token_id = Column(String)
    admin = Column(Boolean, default=False)
