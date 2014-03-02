from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.orm import sessionmaker, relationship, backref

import config

from model_base import Base


class Client(Base):
    __tablename__ = config.db_prefix+'_clients'

    id = Column(Integer, primary_key=True)
    picture = Column(String)
    code = Column(String)

    def __init__(self, code, picture):
        self.code = code
        self.picture = picture

    def __repr__(self):
        return "<Client('%s, %s')>" % (self.code, self.picture)

