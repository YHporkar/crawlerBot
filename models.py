from sqlalchemy import Column, Integer, String, Text, create_engine, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

from config import SQLALCHEMY_DATABASE_URI


Base = declarative_base()
engine = create_engine(SQLALCHEMY_DATABASE_URI)

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()


class Admin(Base):
    __tablename__ = 'admin'
    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True)

    def get_by_username(username):
        admin = session.query(Admin).filter_by(username=username).first()
        return admin

    def get_all():
        return session.query(Admin).all()

    def initialize():
        Admin(id=215797529, username='Yasin_Porkar').add()
        Admin(id=183674933, username='khorshidiAmirhosein').add()

    def add(self):
        session.add(self)
        session.commit()

    def delete(admin):
        session.delete(admin)
        session.commit()
