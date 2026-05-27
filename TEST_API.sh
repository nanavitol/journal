#!/bin/bash
# Автоматизированный сценарий верификации эндпоинтов REST API ВОСВОД

API_BASE="https://api.vodalchuk.ru"

echo "============================================"
echo " 1. ТЕСТИРОВАНИЕ АУТЕНТИФИКАЦИИ"
echo "============================================"

# --- Успешный вход под учетной записью Администратора ---
echo -e "\n>>> [Admin] Успешный вход"
ADMIN_RESPONSE=$(curl -sS -X 'POST' \
  "${API_BASE}/auth/login" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "login": "VodalchukMNK",
  "password": "Vodalchuk123"
}')
echo "$ADMIN_RESPONSE" | jq
ADMIN_TOKEN=$(echo "$ADMIN_RESPONSE" | jq -r '.access_token')
echo "Токен админа получен: ${ADMIN_TOKEN:0:25}..."

# --- Успешный вход под учетной записью Работника ---
echo -e "\n>>> [Worker] Успешный вход"
WORKER_RESPONSE=$(curl -sS -X 'POST' \
  "${API_BASE}/auth/login" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "login": "MorozovMNK",
  "password": "correct_worker_password"
}')
echo "$WORKER_RESPONSE" | jq
WORKER_TOKEN=$(echo "$WORKER_RESPONSE" | jq -r '.access_token')

# --- Негативный сценарий: авторизация с некорректным паролем ---
echo -e "\n>>> [Negative] Неверный пароль"
curl -sS -X 'POST' \
  "${API_BASE}/auth/login" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "login": "VodalchukMNK",
  "password": "wrong_password"
}' | jq

echo "============================================"
echo " 2. ТЕСТИРОВАНИЕ ОБЩИХ ЭНДПОИНТОВ"
echo "============================================"

echo -e "\n>>> [Admin] Получение своего профиля (GET /users/me)"
curl -sS -X 'GET' "${API_BASE}/users/me" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

echo -e "\n>>> [Worker] Получение своего профиля (GET /users/me)"
curl -sS -X 'GET' "${API_BASE}/users/me" \
  -H "Authorization: Bearer $WORKER_TOKEN" | jq

echo -e "\n>>> [Worker] Получение списка коллег (GET /users/colleagues)"
curl -sS -X 'GET' "${API_BASE}/users/colleagues" \
  -H "Authorization: Bearer $WORKER_TOKEN" | jq

echo "============================================"
echo " 3. ТЕСТИРОВАНИЕ АДМИНСКИХ ЭНДПОИНТОВ"
echo "============================================"

echo -e "\n>>> [Admin] Получение всех пользователей (GET /admin/users)"
curl -sS -X 'GET' "${API_BASE}/admin/users" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

echo -e "\n>>> [Admin] Получение своего профиля через админский эндпоинт"
curl -sS -X 'GET' "${API_BASE}/admin/users/88419226-8430-4976-a25d-37c4fc789f2c" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

echo -e "\n>>> [Admin] Получение списка городов (GET /admin/cities)"
curl -sS -X 'GET' "${API_BASE}/admin/cities" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

echo -e "\n>>> [Admin] Создание нового поста (POST /admin/posts)"
POST_RESPONSE=$(curl -sS -X 'POST' "${API_BASE}/admin/posts" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{
  \"name\": \"Тестовый пост от $(date +%s)\",
  \"city_id\": 1,
  \"max_workers\": 5
}")
echo "$POST_RESPONSE" | jq
POST_ID=$(echo "$POST_RESPONSE" | jq -r '.id')

echo -e "\n>>> [Admin] Получение созданного поста (GET /admin/posts/$POST_ID)"
curl -sS -X 'GET' "${API_BASE}/admin/posts/$POST_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

echo -e "\n>>> [Admin] Удаление созданного поста (DELETE /admin/posts/$POST_ID)"
DELETE_CODE=$(curl -sS -o /dev/null -w "%{http_code}" -X 'DELETE' "${API_BASE}/admin/posts/$POST_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
echo "Код ответа на удаление: $DELETE_CODE (ожидается 204)"

echo "============================================"
echo " 4. ТЕСТИРОВАНИЕ РАЗГРАНИЧЕНИЯ РОЛЕЙ"
echo "============================================"

echo -e "\n>>> [Negative] Worker пытается получить всех пользователей - ожидается 403"
curl -sS -X 'GET' "${API_BASE}/admin/users" \
  -H "Authorization: Bearer $WORKER_TOKEN" | jq

echo -e "\n===================="
echo "ТЕСТИРОВАНИЕ ЗАВЕРШЕНО."
echo "===================="
