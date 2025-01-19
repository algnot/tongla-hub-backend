import datetime
import random
import string
from sqlalchemy import Column, Integer, TIMESTAMP, Boolean, VARCHAR, TEXT
from model.base import Base


def default_expiration_time():
    return datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)

class OneTimePassword(Base):
    __tablename__ = "one_time_password"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ref = Column(VARCHAR(6), nullable=False)
    mapper_key = Column(TEXT, nullable=False)
    mapper_value = Column(TEXT, nullable=False)
    code = Column(VARCHAR(6), nullable=False)
    used = Column(Boolean, default=False)
    expires_at = Column(TIMESTAMP, default=default_expiration_time, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(TIMESTAMP, default=datetime.datetime.now(datetime.timezone.utc),
                                   onupdate=datetime.datetime.now(datetime.timezone.utc))

    def create(self, value=None):
        if value is None:
            value = {}

        code  = ''.join(random.choices(string.digits, k=6))
        ref = ''.join(random.choices(string.ascii_letters, k=4))

        return super().create({
            "ref": ref,
            "code": code,
            **value
        })
