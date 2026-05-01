-- Скрипт для заполнения базы данных тестовыми данными
-- Выполните этот скрипт в вашей базе данных PostgreSQL

-- 1. Создание городов
INSERT INTO cities (name, created_at) VALUES 
    ('Красноярск', NOW()),
    ('Абан', NOW())
ON CONFLICT DO NOTHING;

-- Получаем ID городов
-- Красноярск = 1, Абан = 2 (предполагаем, что городов еще нет)

-- 2. Создание постов для Красноярска
INSERT INTO posts (name, description, city_id, default_start_time, default_end_time, price_per_shift, max_workers, photo_url, created_at)
VALUES 
    ('Стрелка', 'Пост на стрелке реки Енисей', 1, '09:00', '17:00', 1500.00, 5, NULL, NOW()),
    ('Абаканская протока', 'Пост на Абаканской протоке', 1, '09:00', '17:00', 1500.00, 4, NULL, NOW()),
    ('Мясокомбинат', 'Пост в районе Мясокомбината', 1, '10:00', '18:00', 1400.00, 3, NULL, NOW())
ON CONFLICT DO NOTHING;

-- 3. Создание постов для Абана
INSERT INTO posts (name, description, city_id, default_start_time, default_end_time, price_per_shift, max_workers, photo_url, created_at)
VALUES 
    ('Лагерь', 'Пост в детском лагере', 2, '08:00', '16:00', 1200.00, 3, NULL, NOW()),
    ('Озеро Становое', 'Пост на озере Становое', 2, '09:00', '17:00', 1300.00, 4, NULL, NOW())
ON CONFLICT DO NOTHING;

-- 4. Создание администратора
-- Логин будет сгенерирован автоматически по ФИО "Водальчук Михаил Николаевич" и городу
-- Примерный логин: VodaichukMN (если без города) или VodaichukMNK (с городом Красноярск)
INSERT INTO users (id, email, login, password_hash, full_name, phone, role, city_id, post, must_change_password, created_at)
VALUES 
    (gen_random_uuid(), 'vodalchuk@vosvod.ru', 'VodaichukMNK', 
     '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfQ3Z9xOyu', 
     'Водальчук Михаил Николаевич', '89041272169', 'admin', 1, 'младший сержант', true, NOW())
ON CONFLICT DO NOTHING;

-- Примечание: пароль для администратора нужно установить через API или хешировать вручную
-- Временный пароль для тестирования: "Admin123"

-- 5. Создание сотрудника (worker)
INSERT INTO users (id, email, login, password_hash, full_name, phone, role, city_id, post, must_change_password, created_at)
VALUES 
    (gen_random_uuid(), 'morozov@vosvod.ru', 'MorozovMNK', 
     '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfQ3Z9xOyu', 
     'Морозов Михаил Викторович', '89999999999', 'worker', 1, 'младший сержант', true, NOW())
ON CONFLICT DO NOTHING;

-- Примечание: пароль для сотрудника: "Worker123"