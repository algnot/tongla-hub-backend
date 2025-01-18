import datetime

from sqlalchemy import Column, Integer, TIMESTAMP, VARBINARY, TEXT, ForeignKey
from sqlalchemy.orm import relationship

from model.base import Base


class Account(Base):
    __tablename__ = "accounts"
    __encrypted_field__ = ["number", "prompt_pay_number"]

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(TEXT, nullable=False)
    number = Column(VARBINARY(200), nullable=False)
    prompt_pay_number = Column(VARBINARY(200), nullable=True)
    qr_code_url = Column(TEXT, nullable=True)
    bank_id = Column(Integer, ForeignKey("banks.id"), nullable=False)
    bank = relationship("Bank", foreign_keys=[bank_id])
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", foreign_keys=[owner_id])
    created_at = Column(TIMESTAMP, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(TIMESTAMP, default=datetime.datetime.now(datetime.timezone.utc),
                        onupdate=datetime.datetime.now(datetime.timezone.utc))
