from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None

class UserOut(UserCreate):
    id: int
    joined_at: datetime
    class Config:
        orm_mode = True

class WordCreate(BaseModel):
    word: str

class WordOut(WordCreate):
    id: int
    stem: str
    correct_letter: str
    class Config:
        orm_mode = True

class TestResultCreate(BaseModel):
    user_id: int
    total_questions: int
    correct_answers: int
    percentage: int

class TestResultOut(TestResultCreate):
    id: int
    completed_at: datetime
    class Config:
        orm_mode = True
