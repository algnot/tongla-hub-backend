import datetime
import enum

from sqlalchemy import Column, Integer, TIMESTAMP, VARBINARY, Enum, TEXT
from sqlalchemy.orm import relationship

from model.base import Base
from model.user_tokens import UserTokens
from util.encryptor import hash_password


class RoleType(enum.Enum):
    USER = 1
    ADMIN = 2

class User(Base):
    __tablename__ = "users"
    __encrypted_field__ = ["username", "email"]

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(VARBINARY(200), nullable=False)
    email = Column(VARBINARY(200), nullable=False, unique=True)
    hashed_password = Column(VARBINARY(200), nullable=False)
    tokens = relationship("UserTokens", back_populates="user", cascade="all, delete-orphan")
    created_at = Column(TIMESTAMP, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(TIMESTAMP, default=datetime.datetime.now(datetime.timezone.utc),
                                   onupdate=datetime.datetime.now(datetime.timezone.utc))
    role = Column(Enum(RoleType), default=RoleType.USER, nullable=False)
    image_url = Column(TEXT, nullable=True)

    def sign_up(self, password):
        return self.create({
            "hashed_password": hash_password(password)
        })

    def generate_token(self):
        user_token = UserTokens()
        user_token.user_id = self.id
        return user_token.generate_token()
