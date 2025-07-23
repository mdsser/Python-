from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Script(Base):
    __tablename__ = 'scripts'
    id = Column(Integer, Sequence('script_id_seq'), primary_key=True)
    name = Column(String(50))
    path = Column(String(100))

def init_db():
    engine = create_engine('sqlite:///ops.db')
    Base.metadata.create_all(engine)
