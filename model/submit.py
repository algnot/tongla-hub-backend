import datetime
import random
from sqlalchemy import Column, Integer, TIMESTAMP, TEXT, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from model.base import Base

def generate_random_id():
    return random.randint(10000000, 99999999)

class Submit(Base):
    __tablename__ = "submit"

    id = Column(Integer, primary_key=True, default=generate_random_id)
    question_id = Column(Integer, ForeignKey("question.id"), nullable=False)
    question = relationship("Question")
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User")
    code = Column(TEXT, nullable=True)
    score = Column(Integer, nullable=True)
    max_score = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(TIMESTAMP, default=datetime.datetime.now(datetime.timezone.utc),
                                   onupdate=datetime.datetime.now(datetime.timezone.utc))
