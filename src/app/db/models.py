import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime, Table, inspect
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from app.db.database import db

Base = declarative_base()


class User(db.Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, unique=True, nullable=False)
    email_verified = Column(Boolean, default=True, nullable=False)
    username = Column(String, index=True, nullable=False, unique=True)
    password = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.now())

    def __init__(self, **kw):
        super().__init__(**kw)
        self._boards = set()

    @property
    def boards(self):
        return self._boards

    def add_board(self, board):
        self._boards.add(board)


class Card(db.Model):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.now())
    last_change_at = Column(DateTime, nullable=False, default=datetime.datetime.now())

    list_id = Column(Integer, ForeignKey("lists.id"))
    list = relationship("List", backref="cards")

    last_change_by_id = Column(Integer, ForeignKey("users.id"))
    last_change_by = relationship("User", backref="cards", foreign_keys=[last_change_by_id])

    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_by = relationship("User", backref="card", foreign_keys=[created_by_id])


class List(db.Model):
    __tablename__ = "lists"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)

    # TODO: null value in fk
    board_id = Column(Integer, ForeignKey("boards.id"))
    board = relationship("Board", backref="lists")

    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_by = relationship("User", backref="lists")


# TODO: add indexes
class BoardUsers(db.Model):
    __tablename__ = 'board_users'

    board_id = Column(Integer, ForeignKey('boards.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)


class Board(db.Model):
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    public = Column(Boolean, nullable=False, default=False)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", backref="boards")

    created_at = Column(DateTime, nullable=False, default=datetime.datetime.now())

    def __init__(self, **kw):
        super().__init__(**kw)
        self._users = set()

    @property
    def users(self):
        return self._users

    def add_user(self, user):
        self._users.add(user)
        user._boards.add(self)

    # users = relationship("User", secondary=board_users)



