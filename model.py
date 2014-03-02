# -*- encoding: utf-8 -*-

from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, relationship, backref

import config

from model_client import *

from model_base import Base

engine = create_engine(config.db, echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

session = Session()
