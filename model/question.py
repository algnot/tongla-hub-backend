import datetime
from sqlalchemy import Column, Integer, TIMESTAMP, TEXT, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from model.base import Base


class Question(Base):
    __tablename__ = "question"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(TEXT, nullable=False)
    description = Column(TEXT, nullable=False)
    start_code = Column(TEXT, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User")
    test_cases = relationship("TestCase", back_populates="question", cascade="all, delete-orphan")
    rate = Column(Integer, nullable=True, default=1)
    is_system_question = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    submitted = Column(Integer, nullable=True, default=0)
    commented = Column(Integer, nullable=True, default=0)
    created_at = Column(TIMESTAMP, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(TIMESTAMP, default=datetime.datetime.now(datetime.timezone.utc),
                                   onupdate=datetime.datetime.now(datetime.timezone.utc))
