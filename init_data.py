#!/usr/bin/env python3
"""
Скрипт для заполнения базы данных тестовыми данными.
Запустите: cd vosvod_backend && conda run -n vosvod_env python init_data.py
"""
import asyncio
from datetime import time as dt_time
from uuid import uuid4

# Импортируем все модели для правильной инициализации SQLAlchemy
from app.models.users import User
from app.models.cities import City
from app.models.posts import Post
from app.models.shifts import Shift
from app.models.shift_assignments import ShiftAssignment
from app.models.journal_entries import JournalEntry

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash


async def init_data():
    async with AsyncSessionLocal() as session:
        # 1. Создание городов
        cities_data = [
            {"name": "Красноярск"},
            {"name": "Абан"},
        ]
        
        for city_data in cities_data:
            # Проверяем, существует ли город
            result = await session.execute(
                select(City).where(City.name == city_data["name"])
            )
            existing_city = result.scalar_one_or_none()
            if not existing_city:
                city = City(**city_data)
                session.add(city)
                print(f"Добавлен город: {city_data['name']}")
            else:
                print(f"Город уже существует: {city_data['name']}")
        
        await session.commit()
        
        # Получаем ID городов
        result = await session.execute(select(City))
        cities = {c.name: c.id for c in result.scalars().all()}
        print(f"Города в БД: {cities}")
        
        # 2. Создание постов для Красноярска
        posts_data = [
            {"name": "Стрелка", "description": "Пост на стрелке реки Енисей", "city_id": cities.get("Красноярск"), 
             "default_start_time": dt_time(9, 0), "default_end_time": dt_time(17, 0), "price_per_shift": 1500.00, "max_workers": 5},
            {"name": "Абаканская протока", "description": "Пост на Абаканской протоке", "city_id": cities.get("Красноярск"),
             "default_start_time": dt_time(9, 0), "default_end_time": dt_time(17, 0), "price_per_shift": 1500.00, "max_workers": 4},
            {"name": "Мясокомбинат", "description": "Пост в районе Мясокомбината", "city_id": cities.get("Красноярск"),
             "default_start_time": dt_time(10, 0), "default_end_time": dt_time(18, 0), "price_per_shift": 1400.00, "max_workers": 3},
            # Посты для Абана
            {"name": "Лагерь", "description": "Пост в детском лагере", "city_id": cities.get("Абан"),
             "default_start_time": dt_time(8, 0), "default_end_time": dt_time(16, 0), "price_per_shift": 1200.00, "max_workers": 3},
            {"name": "Озеро Становое", "description": "Пост на озере Становое", "city_id": cities.get("Абан"),
             "default_start_time": dt_time(9, 0), "default_end_time": dt_time(17, 0), "price_per_shift": 1300.00, "max_workers": 4},
        ]
        
        for post_data in posts_data:
            result = await session.execute(
                select(Post).where(Post.name == post_data["name"])
            )
            existing_post = result.scalar_one_or_none()
            if not existing_post:
                post = Post(**post_data)
                session.add(post)
                print(f"Добавлен пост: {post_data['name']}")
            else:
                print(f"Пост уже существует: {post_data['name']}")
        
        await session.commit()
        
        # 3. Создание администратора
        admin_login = "VodalchukMNK"  # Будет проверен при создании
        password_hash = get_password_hash("Vodalchuk123")
        
        result = await session.execute(
            select(User).where(User.login == admin_login)
        )
        existing_admin = result.scalar_one_or_none()
        
        if not existing_admin:
            admin = User(
                id=uuid4(),
                email="vodalchuk@vosvod.ru",
                login=admin_login,
                password_hash=password_hash,
                full_name="Водальчук Михаил Николаевич",
                phone="89041272169",
                role="admin",
                city_id=cities.get("Красноярск"),
                rank="младший сержант",
                password_changed=False
            )
            session.add(admin)
            print(f"Добавлен администратор: Водальчук Михаил Николаевич (логин: {admin_login}, пароль: Vodalchuk123)")
        else:
            print(f"Администратор уже существует: {admin_login}")
        
        # 4. Создание сотрудника (worker)
        worker_login = "MorozovMNK"
        worker_password_hash = get_password_hash("Morozov123")
        
        result = await session.execute(
            select(User).where(User.login == worker_login)
        )
        existing_worker = result.scalar_one_or_none()
        
        if not existing_worker:
            worker = User(
                id=uuid4(),
                email="morozov@vosvod.ru",
                login=worker_login,
                password_hash=worker_password_hash,
                full_name="Морозов Михаил Викторович",
                phone="89999999999",
                role="worker",
                city_id=cities.get("Красноярск"),
                rank="младший сержант",
                password_changed=False
            )
            session.add(worker)
            print(f"Добавлен сотрудник: Морозов Михаил Викторович (логин: {worker_login}, пароль: Morozov123)")
        else:
            print(f"Сотрудник уже существует: {worker_login}")
        
        await session.commit()
        print("\nДанные успешно загружены!")


if __name__ == "__main__":
    asyncio.run(init_data())