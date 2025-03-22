"""
Модуль для работы с базой данных SQLite
"""
import os
import logging
from datetime import datetime, timedelta
import json
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from config import DATABASE_URL, BASE_DIR

# Создаем базовый класс для моделей
Base = declarative_base()

# Модель пользователя
class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    language_code = Column(String)
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Отношения
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    request_counter = relationship("RequestCounter", back_populates="user", uselist=False, cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")

# Модель настроек пользователя
class UserSettings(Base):
    __tablename__ = 'user_settings'
    
    user_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)
    tts_engine = Column(String, default='gtts')
    voice_type = Column(String, default='female')
    language = Column(String, default='ru')
    audio_format = Column(String, default='mp3')
    
    # Отношения
    user = relationship("User", back_populates="settings")

# Модель счетчика запросов
class RequestCounter(Base):
    __tablename__ = 'request_counters'
    
    user_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)
    hourly_count = Column(Integer, default=0)
    daily_count = Column(Integer, default=0)
    last_hourly_reset = Column(DateTime, default=datetime.utcnow)
    last_daily_reset = Column(DateTime, default=datetime.utcnow)
    
    # Отношения
    user = relationship("User", back_populates="request_counter")

# Модель задачи
class Task(Base):
    __tablename__ = 'tasks'
    
    task_id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    status = Column(String, default='pending')
    text_length = Column(Integer)
    file_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    estimated_time = Column(Integer)
    
    # Отношения
    user = relationship("User", back_populates="tasks")

# Создаем движок базы данных
engine = create_engine(DATABASE_URL)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Инициализация базы данных"""
    # Создаем директорию для базы данных, если она не существует
    db_dir = os.path.join(BASE_DIR, "db")
    os.makedirs(db_dir, exist_ok=True)
    
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    logging.info("База данных инициализирована")

def get_db():
    """Получение сессии базы данных"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def get_or_create_user(db, user_id, username=None, first_name=None, last_name=None, language_code=None, is_premium=False):
    """Получение или создание пользователя"""
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        user = User(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
            is_premium=is_premium
        )
        db.add(user)
        
        # Создаем настройки пользователя
        settings = UserSettings(user_id=user_id)
        db.add(settings)
        
        # Создаем счетчик запросов
        counter = RequestCounter(user_id=user_id)
        db.add(counter)
        
        db.commit()
        db.refresh(user)
    
    return user

def get_user_settings(db, user_id):
    """Получение настроек пользователя"""
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    
    if not settings:
        # Создаем пользователя и настройки, если они не существуют
        get_or_create_user(db, user_id)
        settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    
    return settings

def update_user_settings(db, user_id, **kwargs):
    """Обновление настроек пользователя"""
    settings = get_user_settings(db, user_id)
    
    for key, value in kwargs.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
    
    db.commit()
    db.refresh(settings)
    return settings

def create_task(db, user_id, task_id, text_length, file_name=None, estimated_time=None):
    """Создание новой задачи"""
    task = Task(
        task_id=task_id,
        user_id=user_id,
        text_length=text_length,
        file_name=file_name,
        estimated_time=estimated_time
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def update_task_status(db, task_id, status):
    """Обновление статуса задачи"""
    task = db.query(Task).filter(Task.task_id == task_id).first()
    
    if task:
        task.status = status
        task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(task)
    
    return task

def get_active_tasks(db, user_id):
    """Получение активных задач пользователя"""
    return db.query(Task).filter(
        Task.user_id == user_id,
        Task.status.in_(['pending', 'processing'])
    ).all()

def get_user_tasks(db, user_id, status=None):
    """Получение задач пользователя с указанным статусом"""
    query = db.query(Task).filter(Task.user_id == user_id)
    if status:
        query = query.filter(Task.status == status)
    return query.all()

def reset_user_settings(db, user_id):
    """Сброс настроек пользователя до значений по умолчанию"""
    settings = get_user_settings(db, user_id)
    
    settings.tts_engine = 'gtts'
    settings.voice_type = 'female'
    settings.language = 'ru'
    settings.audio_format = 'mp3'
    
    db.commit()
    db.refresh(settings)
    return settings