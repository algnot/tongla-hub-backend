from sqlalchemy import Column, TEXT, VARCHAR
from model.base import Base

class Bank(Base):
    __tablename__ = "banks"

    id = Column(VARCHAR(3), primary_key=True, nullable=False)
    name = Column(TEXT, nullable=False)
    full_name = Column(TEXT, nullable=False)
