import environs
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, declarative_base, sessionmaker

env = environs.Env()
env.read_env()

host = env("host")
password = env("password")
database = env("database")

engine = create_engine(f"postgresql+psycopg2://postgres:{password}@{host}:5432/{database}")

session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = session.query_property()
