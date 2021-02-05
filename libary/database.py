import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


BASE = declarative_base()
ENGINE = sqlalchemy.create_engine('sqlite:///database.db')

DBSESSION = sessionmaker()
DBSESSION.configure(bind=ENGINE)
