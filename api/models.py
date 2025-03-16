from sqlalchemy import Column, Integer, String, true
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Exercise(Base):
  __tablename__ = 'exercises'
  name = Column(String)
  target_muscles = Column(String)
  type = Column(String)
  equipment = Column(String)
  mechanics = Column(String)
  force = Column(String)
  experience_level = Column(String)
  secondary_muscles = Column(String)
  popularity = Column(Integer)
  primary_key = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
