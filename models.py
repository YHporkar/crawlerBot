from sqlalchemy import Column, Integer, String, Date, Text, create_engine, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError

from config import SQLALCHEMY_DATABASE_URI

from whooshalchemy import IndexService

Base = declarative_base()
engine = create_engine(SQLALCHEMY_DATABASE_URI)

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

config = {"WHOOSH_BASE": "whoosh"}
index_service = IndexService(config=config, session=session)


class Admin(Base):
    __tablename__ = 'admin'
    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True)
    is_super = Column(Boolean, default=False)

    def get_by_username(username):
        admin = session.query(Admin).filter_by(username=username).first()
        return admin

    @staticmethod
    def get_all():
        return session.query(Admin).all()

    def initialize():
        Admin(id=215797529, username='Yasin_Porkar', is_super=True).add()
        Admin(id=183674933, username='khorshidiAmirhosein', is_super=True).add()

    def add(self):
        if not session.query(Admin).filter_by(username=self.username).first():
            session.add(self)
            session.commit()

    def delete(admin):
        session.delete(admin)
        session.commit()


class Channel(Base):
    __tablename__ = 'channel'
    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True)
    name = Column(Text)
    start = Column(Integer)

    @staticmethod
    def get_all():
        return session.query(Channel).all()

    def add(self):
        if not session.query(Channel).filter_by(username=self.username).first():
            session.add(self)
            session.commit()

    def update_start(channel, new_start):
        channel.start = new_start
        session.commit()
        return new_start

    def delete(channel):
        session.delete(channel)
        session.commit()


class Post(Base):
    __tablename__ = 'post'
    __searchable__ = ['raw_caption']

    id = Column(Integer, primary_key=True)
    caption = Column(Text)
    raw_caption = Column(Text)
    url = Column(String(50), nullable=False, unique=True)
    views = Column(Integer, nullable=False)
    channel_name = Column(String(50), nullable=False)
    date = Column(Date, nullable=False)

    def get_by_query(query, date):
        return Post.search_query(query).filter(Post.date >= date).all()

    def get_old_posts(date):
        return session.query(Post).filter(Post.date < date).all()

    def get_urls_by_channel(channel_url):
        urls = []
        for post in session.query(Post).filter(Post.url.like('%' + channel_url + '%')).all():
            urls.append(post.url)
        return urls

    def add(self):
        if not session.query(Post).filter_by(url=self.url).first():
            session.add(self)
            session.commit()

    def delete(post):
        session.delete(post)
        session.commit()


index_service.register_class(Post)
