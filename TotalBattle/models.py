from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import json
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func, MetaData
from sqlalchemy.ext.hybrid import hybrid_method
from hashlib import sha1

import imagehash
from PIL import Image
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import REAL
from sqlalchemy.orm import relationship


SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1107@localhost:5433/totalbattle"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()


def init_db():
    Base.metadata.create_all(bind=engine)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    username = Column(String(128), index=True, unique=True)

    accounts = relationship(
        'Account', backref="author", cascade="all, delete", lazy=False)

    def __init__(self, email, password):
        self.email = email
        self.username = email
        self.password = generate_password_hash(password, method='sha256')

    @classmethod
    def authenticate(cls, **kwargs):
        email = kwargs.get('email')
        password = kwargs.get('password')

        if not email or not password:
            return None

        user = cls.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            return None

        return user

    def to_dict(self):
        return dict(id=self.id, email=self.email)


class Account(Base):
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True)
    login = Column(String(128), index=True, unique=True)
    password = Column(String(255), nullable=False)
    isTriumph = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String(128), unique=False)
    clan = Column(String(128), unique=False)
    avatar = Column(String(128), unique=False)
    accounts = relationship('Chest', backref="account", lazy=False)
    is_locked = Column(Boolean, default=False)

    selenium_url = Column(String(128), unique=False)
    selenium_session_id = Column(String(128), unique=False)

    vip = Column(Boolean, default=False)

    def __init__(self, login, password, owner, name, clan, avatar, isTriumph=False) -> None:

        self.login = login
        self.password = password
        self.user_id = owner.id
        self.name = name
        self.clan = clan
        self.avatar = avatar
        self.is_locked = False
        self.isTriumph = isTriumph

    def to_dict(self):
        return dict(
            name=self.name,
            clan=self.clan,
            avatar=self.avatar,
            id=self.id,
            is_locked=self.is_locked,
            isTriumph=self.isTriumph,
            user_id=self.user_id,
            vip=self.vip
        )

    def to_login(self):
        return dict(
            login=self.login,
            password=self.password,
            name=self.name,
            clan=self.clan,
            avatar=self.avatar,
            id=self.id,
            is_locked=self.is_locked,
            isTriumph=self.isTriumph,
            user_id=self.user_id,
            vip=self.vip
        )


class Chest(Base):
    __tablename__ = 'chest'
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('account.id'))

    # images
    chest_type = Column(String(128), index=True)
    chest_name = Column(String(128), index=True)
    player = Column(String(128), index=True)
    # ids
    chest_type_id = Column(Integer, ForeignKey('ideal_chest_type.id'))
    chest_name_id = Column(Integer, ForeignKey('ideal_chest_name.id'))
    player_id = Column(Integer, ForeignKey(
        'clan_player.id', ondelete='CASCADE'))

    opened_in = Column(DateTime)
    got_at = Column(DateTime)
    path = Column(String(128))
    check_needed = Column(String(128))

    def __init__(self, account_id, chest_type, player_name, chest_name, got_at, path, chest_type_id, chest_name_id, player_id, check_needed=''):
        self.account_id = account_id
        self.chest_type = chest_type
        self.player = player_name
        self.chest_name = chest_name
        self.got_at = got_at
        self.path = path
        self.check_needed = check_needed
        self.opened_in = datetime.now()-timedelta(hours=3)

        self.chest_type_id = chest_type_id
        self.chest_name_id = chest_name_id
        self.player_id = player_id

    def to_dict(self):
        return dict(
            id=self.id,
            chest_type=self.chest_type,
            player=self.player,
            got_at=self.got_at,
            chest_name=self.chest_name,
            opened_in=self.opened_in,
            path=self.path,
            check_needed=self.check_needed
        )


class Report(Base):
    __tablename__ = 'report'
    id = Column(Integer, primary_key=True)
    hash = Column(String(128))
    report_query = Column(String(128))
    account_id = Column(Integer, ForeignKey('account.id'))

    def __init__(self, report_query, account_id):
        self.hash = sha1(report_query.encode('utf-8')).hexdigest()
        self.report_query = report_query
        self.account_id = account_id

    def get_query(self):
        return json.loads(self.report_query)


class ChestRule(Base):
    __tablename__ = 'chest_rule'
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('account.id'))
    group = Column(Integer, default=99)
    ideal_chest_name = Column(String(128))
    ideal_chest_type = Column(String(128))
    scores = Column(REAL, default=1)

    ideal_chest_name_id = Column(
        Integer, ForeignKey('ideal_chest_name.id'))
    ideal_chest_type_id = Column(
        Integer, ForeignKey('ideal_chest_type.id'))

    def __init__(self, account_id, group, scores, ideal_chest_name, ideal_chest_type):
        self.account_id = account_id
        self.group = group
        self.scores = scores
        self.ideal_chest_name = ideal_chest_name
        self.ideal_chest_type = ideal_chest_type
        if (ideal_chest_name != 'all'):
            idealChestNameInstance = SessionLocal.query(IdealChestName).filter_by(
                text=ideal_chest_name).first()
            self.ideal_chest_name_id = idealChestNameInstance.id
        if (ideal_chest_type != 'all'):
            idealChestTypeInstance = SessionLocal.query(IdealChestType).filter_by(
                text=ideal_chest_type).first()
            self.ideal_chest_type_id = idealChestTypeInstance.id

    def to_dict(self):
        return dict(
            group=self.group,
            ideal_chest_name=self.ideal_chest_name,
            ideal_chest_type=self.ideal_chest_type,
            scores=self.scores
        )


class ClanPlayer(Base):
    __tablename__ = 'clan_player'
    id = Column(Integer, primary_key=True)
    hash = Column(String(128))
    account_id = Column(Integer, ForeignKey('account.id'))
    path = Column(String(128))
    name = Column(String(128))
    level = Column(Integer, default=1)

    chests = relationship('Chest', backref="Owner")

    def __init__(self, account_id, path, name):
        self.hash = str(imagehash.phash(Image.open(path), hash_size=16))
        self.path = path
        self.account_id = account_id
        self.name = name

    @hybrid_method
    def difference(self, path):
        return imagehash.phash(Image.open(path), hash_size=16) - imagehash.hex_to_hash(self.hash)

    @difference.expression
    def difference(cls, path):
        return imagehash.phash(Image.open(path), hash_size=16) - imagehash.hex_to_hash(cls.hash)


class IdealChestName(Base):
    __tablename__ = 'ideal_chest_name'
    id = Column(Integer, primary_key=True)
    hash = Column(String(128))
    path = Column(String(128))
    text = Column(String(128))

    def __init__(self, path, text):
        self.hash = str(imagehash.phash(Image.open(path), 16))
        self.path = path
        self.text = text

    @hybrid_method
    def difference(self, path):
        return imagehash.phash(Image.open(path), 16) - imagehash.hex_to_hash(self.hash)

    @difference.expression
    def difference(cls, path):
        return imagehash.phash(Image.open(path), 16) - imagehash.hex_to_hash(cls.hash)


class IdealChestType(Base):
    __tablename__ = 'ideal_chest_type'
    id = Column(Integer, primary_key=True)
    hash = Column(String(128))
    path = Column(String(128))
    text = Column(String(128))

    def __init__(self, path, text):
        self.hash = str(imagehash.phash(Image.open(path), 16))
        self.path = path
        self.text = text

    @hybrid_method
    def difference(self, path):
        return imagehash.phash(Image.open(path), 16) - imagehash.hex_to_hash(self.hash)

    @difference.expression
    def difference(cls, path):
        return imagehash.phash(Image.open(path), 16) - imagehash.hex_to_hash(cls.hash)


class Queue(Base):
    __tablename__ = 'queue'
    id = Column(Integer, primary_key=True)
    url = Column(String(128))
    account_id = Column(Integer, ForeignKey('account.id'))
    cookies = Column(String(256))
    active = Column(Boolean, default=False)
    timestamp = Column(DateTime)
    done = Column(Boolean, default=False)

    def __init__(self, url, account_id, cookies):
        self.url = url
        self.account_id = account_id
        self.cookies = cookies
        self.active = False
        self.timestamp = datetime.now()

    def to_dict(self):
        return dict(
            timestamp=self.timestamp,
            active=self.active,
            account_id=self.account_id
        )
