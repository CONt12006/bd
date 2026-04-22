from sqlalchemy.orm import Session
from models import User, Word, TestResult

def get_user(db: Session, telegram_id: int):
    return db.query(User).filter(User.telegram_id == telegram_id).first()

def get_or_create_user(db: Session, telegram_id: int, username: str = None, first_name: str = None):
    db_user = get_user(db, telegram_id)
    if not db_user:
        db_user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    return db_user

def get_all_words(db: Session):
    return db.query(Word).filter(Word.active == True).all()

def create_word_if_not_exists(db: Session, word: str):
    if db.query(Word).filter(Word.word == word).first():
        return
    correct_letter = ''.join([c for c in word if c.isupper()])
    stem = ''.join(['..' if c.isupper() else c.lower() for c in word])
    db_word = Word(word=word, stem=stem, correct_letter=correct_letter)
    db.add(db_word)
    db.commit()

def create_test_result(db: Session, user_id: int, total: int, correct: int):
    percentage = (correct * 100) // total if total > 0 else 0
    result = TestResult(
        user_id=user_id,
        total_questions=total,
        correct_answers=correct,
        percentage=percentage
    )
    db.add(result)
    db.commit()
