import datetime
from sqlalchemy import Column, Integer, TIMESTAMP, Boolean, VARCHAR
from model.base import Base


def default_expiration_time():
    return datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)

class User(Base):
    __tablename__ = "one_time_password"
    __encrypted_field__ = ["username", "email"]

    id = Column(Integer, primary_key=True, autoincrement=True)

    ref = Column(VARCHAR(6), nullable=False)
    code = Column(VARCHAR(6), nullable=False)
    used = Column(Boolean, default=False)
    expires_at = Column(TIMESTAMP, default=default_expiration_time, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(TIMESTAMP, default=datetime.datetime.now(datetime.timezone.utc),
                                   onupdate=datetime.datetime.now(datetime.timezone.utc))
