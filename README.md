# Справочник API ВОСВОД для фронтенд-разработчиков

**Аутентификация:** JWT токен в заголовке `Authorization: Bearer <token>`

## Содержание
1. [Аутентификация](#аутентификация)
2. [Пользователи (общие)](#пользователи-общие)
3. [Администратор](#администратор)
4. [Работник (Worker)](#работник-worker)
5. [Модели данных](#модели-данных)

---

## Аутентификация

### Вход в систему
**Endpoint:** `POST /auth/login`

**Тело запроса:**
```json
{
  "login": "string",
  "password": "string"
}
```

**Ответ:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "require_password_change": boolean
}
```

**Описание:** Возвращает JWT токен для последующих запросов. Если `require_password_change: true`, необходимо сменить пароль.

### Смена пароля
**Endpoint:** `POST /auth/change-password`

**Требуемая роль:** Любой аутентифицированный пользователь

**Тело запроса:**
```json
{
  "current_password": "string",
  "new_password": "string"
}
```

**Ответ:** `200 OK` при успехе

---

## Пользователи (общие)

### Получить свой профиль
**Endpoint:** `GET /users/me`

**Требуемая роль:** Любой аутентифицированный пользователь

**Ответ:** [UserResponse](#userresponse)

### Получить коллег
**Endpoint:** `GET /users/colleagues`

**Требуемая роль:** Любой аутентифицированный пользователь

**Query параметры:**
- `city_id` (опционально) - фильтр по городу

**Ответ:** Массив [UserResponse](#userresponse)

**Примечание:** Для работников возвращаются только коллеги из того же города.

### Получить профиль пользователя по ID
**Endpoint:** `GET /users/{user_id}`

**Требуемая роль:** Любой аутентифицированный пользователь

**Path параметры:**
- `user_id` (UUID) - идентификатор пользователя

**Ответ:** [UserResponse](#userresponse)

### Получить количество отработанных смен
**Endpoint:** `GET /users/{user_id}/shifts-count`

**Требуемая роль:** Любой аутентифицированный пользователь

**Path параметры:**
- `user_id` (UUID) - идентификатор пользователя

**Ответ:**
```json
{
  "count": integer
}
```

---

## Администратор

*Все эндпоинты ниже требуют роли `admin`*

### Управление пользователями

#### Получить всех пользователей
**Endpoint:** `GET /admin/users`

**Ответ:** Массив [UserResponse](#userresponse)

#### Создать пользователя
**Endpoint:** `POST /admin/users`

**Тело запроса:** [UserCreate](#usercreate)

**Ответ:** [UserResponse](#userresponse) (201 Created)

#### Получить пользователя по ID
**Endpoint:** `GET /admin/users/{user_id}`

**Path параметры:**
- `user_id` (UUID) - идентификатор пользователя

**Ответ:** [UserResponse](#userresponse)

#### Обновить пользователя
**Endpoint:** `PUT /admin/users/{user_id}`

**Path параметры:**
- `user_id` (UUID) - идентификатор пользователя

**Тело запроса:** [UserUpdate](#userupdate)

**Ответ:** [UserResponse](#userresponse)

#### Удалить пользователя
**Endpoint:** `DELETE /admin/users/{user_id}`

**Path параметры:**
- `user_id` (UUID) - идентификатор пользователя

**Ответ:** `204 No Content`

### Управление городами

#### Получить все города
**Endpoint:** `GET /admin/cities`

**Ответ:** Массив [CityResponse](#cityresponse)

#### Создать город
**Endpoint:** `POST /admin/cities`

**Тело запроса:** [CityCreate](#citycreate)

**Ответ:** [CityResponse](#cityresponse) (201 Created)

#### Получить город по ID
**Endpoint:** `GET /admin/cities/{city_id}`

**Path параметры:**
- `city_id` (integer) - идентификатор города

**Ответ:** [CityResponse](#cityresponse)

#### Обновить город
**Endpoint:** `PUT /admin/cities/{city_id}`

**Path параметры:**
- `city_id` (integer) - идентификатор города

**Тело запроса:** [CityUpdate](#cityupdate)

**Ответ:** [CityResponse](#cityresponse)

#### Удалить город
**Endpoint:** `DELETE /admin/cities/{city_id}`

**Path параметры:**
- `city_id` (integer) - идентификатор города

**Ответ:** `204 No Content`

### Управление постами

#### Получить все посты
**Endpoint:** `GET /admin/posts`

**Query параметры:**
- `city_id` (опционально) - фильтр по городу

**Ответ:** Массив [PostResponse](#postresponse)

#### Создать пост
**Endpoint:** `POST /admin/posts`

**Тело запроса:** [PostCreate](#postcreate)

**Ответ:** [PostResponse](#postresponse) (201 Created)

#### Получить пост по ID
**Endpoint:** `GET /admin/posts/{post_id}`

**Path параметры:**
- `post_id` (integer) - идентификатор поста

**Ответ:** [PostResponse](#postresponse)

#### Обновить пост
**Endpoint:** `PUT /admin/posts/{post_id}`

**Path параметры:**
- `post_id` (integer) - идентификатор поста

**Тело запроса:** [PostUpdate](#postupdate)

**Ответ:** [PostResponse](#postresponse)

#### Удалить пост
**Endpoint:** `DELETE /admin/posts/{post_id}`

**Path параметры:**
- `post_id` (integer) - идентификатор поста

**Ответ:** `204 No Content`

### Управление сменами

#### Получить все смены
**Endpoint:** `GET /admin/shifts`

**Query параметры:**
- `skip` (опционально) - пагинация, пропустить N записей
- `limit` (опционально) - пагинация, ограничить количество записей

**Ответ:** Массив [ShiftResponse](#shiftresponse)

#### Создать смену
**Endpoint:** `POST /admin/shifts`

**Тело запроса:** [ShiftCreate](#shiftcreate)

**Ответ:** [ShiftResponse](#shiftresponse) (201 Created)

**Ограничения:** Нельзя создать две смены на один пост в один день

#### Получить смену по ID
**Endpoint:** `GET /admin/shifts/{shift_id}`

**Path параметры:**
- `shift_id` (integer) - идентификатор смены

**Ответ:** [ShiftResponse](#shiftresponse)

#### Обновить смену
**Endpoint:** `PUT /admin/shifts/{shift_id}`

**Path параметры:**
- `shift_id` (integer) - идентификатор смены

**Тело запроса:** [ShiftUpdate](#shiftupdate)

**Ответ:** [ShiftResponse](#shiftresponse)

#### Удалить смену
**Endpoint:** `DELETE /admin/shifts/{shift_id}`

**Path параметры:**
- `shift_id` (integer) - идентификатор смены

**Ответ:** `204 No Content`

#### Изменить статус смены
**Endpoint:** `PATCH /admin/shifts/{shift_id}/status`

**Path параметры:**
- `shift_id` (integer) - идентификатор смены

**Query параметры:**
- `status` (string) - новый статус: `planned`, `active`, `completed`

**Ответ:** [ShiftResponse](#shiftresponse)

### Управление назначениями на смены

#### Назначить работника на смену
**Endpoint:** `POST /admin/shifts/{shift_id}/assign`

**Path параметры:**
- `shift_id` (integer) - идентификатор смены

**Query параметры:**
- `user_id` (UUID) - идентификатор пользователя
- `is_leader` (boolean, опционально) - является ли старшим смены (по умолчанию `false`)

**Ответ:** `201 Created` с телом:
```json
{
  "message": "Assigned successfully"
}
```

**Ограничения:**
- Не больше `max_workers` поста
- Работник не может быть назначен на две смены в один день
- Только один лидер на смену
- Город работника должен совпадать с городом поста (для работников)

#### Удалить назначение
**Endpoint:** `DELETE /admin/shifts/{shift_id}/assign/{user_id}`

**Path параметры:**
- `shift_id` (integer) - идентификатор смены
- `user_id` (UUID) - идентификатор пользователя

**Ответ:** `204 No Content`

### Управление журналом

#### Получить все записи журнала
**Endpoint:** `GET /admin/journal`

**Ответ:** Массив [JournalEntryResponse](#journalentryresponse)

#### Создать запись в журнале от имени администратора
**Endpoint:** `POST /admin/journal/{shift_id}`

**Path параметры:**
- `shift_id` (integer) - идентификатор смены

**Query параметры:**
- `note` (string) - текст записи
- `entry_type` (string) - тип записи: `routine`, `incident`, `remark`

**Ответ:** [JournalEntryResponse](#journalentryresponse) (201 Created)

**Ограничение:** Администратор должен быть назначен на смену

---

## Работник (Worker)

*Все эндпоинты ниже требуют роли `worker`*

### Профиль работника

#### Получить свой профиль
**Endpoint:** `GET /worker/profile`

**Ответ:** [UserResponse](#userresponse)

#### Обновить свой профиль
**Endpoint:** `PUT /worker/profile`

**Тело запроса:** [UserUpdate](#userupdate) (только поля, доступные для работника: `photo_url`, `phone`)

**Ответ:** [UserResponse](#userresponse)

### Коллеги

#### Получить коллег
**Endpoint:** `GET /worker/colleagues`

**Ответ:** Массив [UserResponse](#userresponse)

**Примечание:** Возвращаются только работники из того же города.

### Смены работника

#### Получить свои смены
**Endpoint:** `GET /worker/my-shifts`

**Query параметры:**
- `month` (опционально) - фильтр по месяцу в формате `YYYY-MM`

**Ответ:** Массив [ShiftResponse](#shiftresponse)

**Примечание:** Возвращаются только смены, на которые назначен работник.

#### Получить детали смены
**Endpoint:** `GET /worker/shifts/{shift_id}`

**Path параметры:**
- `shift_id` (integer) - идентификатор смены

**Ответ:** [ShiftResponse](#shiftresponse)

**Ограничение:** Работник должен быть назначен на смену

### Журнал работника

#### Получить записи журнала для смены
**Endpoint:** `GET /worker/shifts/{shift_id}/journal`

**Path параметры:**
- `shift_id` (integer) - идентификатор смены

**Ответ:** Массив [JournalEntryResponse](#journalentryresponse)

**Ограничение:** Работник должен быть назначен на смену

#### Создать запись в журнале
**Endpoint:** `POST /worker/shifts/{shift_id}/journal`

**Path параметры:**
- `shift_id` (integer) - идентификатор смены

**Тело запроса:**
```json
{
  "note": "string",
  "entry_type": "string"
}
```

**Ответ:** [JournalEntryResponse](#journalentryresponse) (201 Created)

**Ограничения:**
- Работник должен быть назначен на смену
- Смена должна иметь статус `active`

---

## Модели данных

### UserResponse
```json
{
  "id": "uuid",
  "email": "string",
  "login": "string",
  "full_name": "string",
  "city_id": integer,
  "role": "admin" | "worker",
  "rank": "string",
  "phone": "string",
  "password_changed": boolean,
  "photo_url": "string | null",
  "created_at": "datetime"
}
```

### UserCreate
```json
{
  "email": "string",
  "login": "string",
  "full_name": "string",
  "city_id": integer,
  "role": "admin" | "worker",
  "rank": "string",
  "phone": "string",
  "password": "string"
}
```

### UserUpdate
```json
{
  "email": "string | null",
  "full_name": "string | null",
  "city_id": "integer | null",
  "rank": "string | null",
  "phone": "string | null",
  "photo_url": "string | null"
}
```

### CityResponse
```json
{
  "id": integer,
  "name": "string",
  "region": "string",
  "timezone": "string"
}
```

### CityCreate
```json
{
  "name": "string",
  "region": "string",
  "timezone": "string"
}
```

### CityUpdate
```json
{
  "name": "string | null",
  "region": "string | null",
  "timezone": "string | null"
}
```

### PostResponse
```json
{
  "id": integer,
  "name": "string",
  "description": "string",
  "default_start_time": "datetime | null",
  "default_end_time": "datetime | null",
  "price_per_shift": number,
  "max_workers": integer,
  "photo_url": "string | null",
  "city_id": integer
}
```

### PostCreate
```json
{
  "name": "string",
  "city_id": integer,
  "max_workers": integer,
  "description": "string",
  "default_start_time": "datetime | null",
  "default_end_time": "datetime | null",
  "price_per_shift": number,
  "photo_url": "string | null"
}
```

### PostUpdate
```json
{
  "name": "string | null",
  "description": "string | null",
  "default_start_time": "datetime | null",
  "default_end_time": "datetime | null",
  "price_per_shift": "number | null",
  "max_workers": "integer | null",
  "photo_url": "string | null"
}
```

### ShiftResponse
```json
{
  "id": integer,
  "post_id": integer,
  "shift_date": "date",
  "start_time": "datetime",
  "end_time": "datetime",
  "status": "planned" | "active" | "completed",
  "created_by": "uuid | null",
  "created_at": "datetime"
}
```

### ShiftCreate
```json
{
  "post_id": integer,
  "shift_date": "date",
  "start_time": "datetime",
  "end_time": "datetime",
  "status": "planned" | "active" | "completed"
}
```

### ShiftUpdate
```json
{
  "post_id": "integer | null",
  "shift_date": "date | null",
  "start_time": "datetime | null",
  "end_time": "datetime | null",
  "status": "string | null"
}
```

### JournalEntryResponse
```json
{
  "id": integer,
  "shift_id": integer,
  "user_id": "uuid",
  "full_name_snapshot": "string",
  "note": "string",
  "entry_type": "routine" | "incident" | "remark",
  "created_at": "datetime"
}
```

### Примеры кодов ответов

- `200 OK` — успешный запрос
- `201 Created` — ресурс создан
- `204 No Content` — ресурс удален или нет содержимого
- `400 Bad Request` — неверные параметры запроса
- `401 Unauthorized` — неверные или отсутствующие учетные данные
- `403 Forbidden` — недостаточно прав
- `404 Not Found` — ресурс не найден
- `500 Internal Server Error` — внутренняя ошибка сервера

### Важные замечания

1. **Время:** Все временные метки возвращаются в UTC (Z-суффикс).
2. **Даты:** Формат даты `YYYY-MM-DD`, дата-время в формате ISO 8601.
3. **Пагинация:** Для эндпоинтов с пагинацией используйте `skip` и `limit`.
4. **Фильтрация:** Доступна фильтрация по `city_id` для постов и коллег.
5. **Бизнес-правила:** Учитывайте ограничения (max_workers, одна смена в день на пост и т.д.).

### Тестовые пользователи

- **Администратор:** `VodalchukMNK` / `Vodalchuk123`
- **Работник:** `MorozovMNK` / `Morozov1234`
