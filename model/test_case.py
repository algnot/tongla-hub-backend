import datetime
from sqlalchemy import Column, Integer, TIMESTAMP, TEXT, ForeignKey
from sqlalchemy.orm import relationship
from model.base import Base


class TestCase(Base):
    __tablename__ = "test_case"

    id = Column(Integer, primary_key=True, autoincrement=True)
    input = Column(TEXT, nullable=False)
    expected = Column(TEXT, nullable=False)
    expected_run_time_ms = Column(Integer, default=5000)
    question_id = Column(Integer, ForeignKey("question.id"), nullable=False)
    question = relationship("Question", back_populates="test_cases")
    created_at = Column(TIMESTAMP, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(TIMESTAMP, default=datetime.datetime.now(datetime.timezone.utc),
                                   onupdate=datetime.datetime.now(datetime.timezone.utc))
