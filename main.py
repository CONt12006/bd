from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import telebot
from telebot import types
import random
import threading

from database import SessionLocal, engine
from models import Base, Word, User, TestResult
from crud import get_or_create_user, get_all_words, create_word_if_not_exists, create_test_result

Base.metadata.create_all(bind=engine)

app = FastAPI(title="DuckBot API")

BOT_TOKEN = "5808738937:AAF6f0r9GfRLHMDxUqCtvnkgawLmfYdhF3A"
bot = telebot.TeleBot(BOT_TOKEN)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DEFAULT_WORDS = [
    "кОмпьютер", "кОнкурент", "кОрзина", "кОролевство", "лАбиринт", "лИнгвистический", "мЕтафора",
    "нОвелла", "обАяние", "орАнжерея", "ориЕнтир", "ошЕломлённый", "панОрама", "парашЮт",
    "подрАжание", "порАзительный", "правИльный", "примИтивный", "рЕализм", "рЕжиссёрский",
    "рестАврация", "рОвесники", "сИреневый", "сокрОвенные (мечты)", "стадИон", "стрЕмиться",
    "тАлант", "трАдиционный", "трОллейбусный (парк)", "фестИваль", "кОмфортный", "кОнференция",
    "кОричневый", "крОмешная (тьма)", "лЕлеять (мечту)", "насЕкомое", "обАняние", "оптИмистичный",
    "орИгинальный", "офИцерский", "пАлисадник", "панОрамный", "пЕйзаж", "пессИмистический",
    "покОление", "посЕщать", "разбОгатеть", "рЕалистичный", "резИденция", "рЕцензент", "сИмптомы",
    "(в) смЯтении", "спАртакиада", "стИпендия", "сувЕренитет", "тОржественный", "трЕвожиться", "унИчтожать"
]

user_test_data = {}

@app.on_event("startup")
def on_startup():
    """Инициализация: добавление слов в БД"""
    db = SessionLocal()
    try:
        for word in DEFAULT_WORDS:
            create_word_if_not_exists(db, word)
    finally:
        db.close()
    threading.Thread(target=bot.polling, kwargs={"none_stop": True}, daemon=True).start()

@app.get("/")
def root():
    return {"message": "DuckBot API is running!"}


@bot.message_handler(commands=['start'])
def welcome(message):
    db = SessionLocal()
    try:
        get_or_create_user(
            db,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )
    finally:
        db.close()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton('/commands')
    markup.add(btn)
    bot.send_message(message.chat.id, "Привет! Я DuckBot — твой помощник по русскому языку.", reply_markup=markup)

@bot.message_handler(commands=['commands'])
def commands(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton('/test_Russia_language')
    markup.add(btn)
    bot.send_message(message.chat.id, "Команды:\n/test_Russia_language — начать тест", reply_markup=markup)

@bot.message_handler(commands=['test_Russia_language'])
def start_test(message):
    db = SessionLocal()
    try:
        words = get_all_words(db)
        if not words:
            bot.send_message(message.chat.id, "Нет доступных слов.")
            return
    finally:
        db.close()

    shuffled = random.sample(words, len(words))

    user_test_data[message.chat.id] = {
        "words": shuffled,
        "current": None,
        "correct": 0,
        "total": 0
    }

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("СТАРТ"))
    bot.send_message(message.chat.id, "Нажмите СТАРТ", reply_markup=markup)
    bot.register_next_step_handler(message, process_test_step)

def process_test_step(message):
    data = user_test_data.get(message.chat.id)
    if not data:
        return

    if message.text == "СТОП":
        finish_test(message)
        return

    if message.text != "СТАРТ":
        current_word = data["current"]
        if message.text == current_word.correct_letter:
            bot.send_message(message.chat.id, "Правильно!")
            data["correct"] += 1
        else:
            bot.send_message(message.chat.id, f"Неправильно! Правильно: {current_word.correct_letter}")

        data["total"] += 1

    if not data["words"]:
        finish_test(message)
        return

    next_word = data["words"].pop()
    data["current"] = next_word

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['О', 'А', 'Е', 'И', 'Ю', 'У', 'Ё', 'Я', 'СТОП']
    for i in range(0, len(buttons), 4):
        markup.row(*buttons[i:i+4])

    bot.send_message(message.chat.id, next_word.stem, reply_markup=markup)
    bot.register_next_step_handler(message, process_test_step)

def finish_test(message):
    data = user_test_data.pop(message.chat.id, None)
    if not data:
        return

    total = data["total"]
    correct = data["correct"]
    percent = (correct * 100) // total if total > 0 else 0

    db = SessionLocal()
    try:
        create_test_result(db, user_id=message.from_user.id, total=total, correct=correct)
    finally:
        db.close()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('/commands'))
    bot.send_message(message.chat.id, "Тест завершён!")
    bot.send_message(message.chat.id, f"Результат: {correct} из {total} ({percent}%)", reply_markup=markup)
