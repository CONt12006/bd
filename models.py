from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    joined_at = Column(DateTime, default=datetime.utcnow)

    results = relationship("TestResult", back_populates="user")


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(50), unique=True, index=True)
    stem = Column(String(50))
    correct_letter = Column(String(1))
    active = Column(Boolean, default=True)


class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.telegram_id"))
    total_questions = Column(Integer)
    correct_answers = Column(Integer)
    percentage = Column(Integer)
    completed_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="results")
