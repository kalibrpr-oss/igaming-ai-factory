Alembic (схема БД)

1) Установить зависимости: pip install -r requirements.txt (нужен psycopg[binary] для Alembic: postgresql+psycopg).

2) Переменная DATABASE_URL в .env не используется напрямую — URL берётся из app.config settings.database_url (asyncpg). env.py подменяет +asyncpg на +psycopg для alembic.

3) Применить миграции (из каталога backend):
   alembic upgrade head

4) Если таблицы уже созданы через init_db() / create_all:
   alembic stamp head
   (помечает текущую ревизию без DDL; убедитесь, что схема совпадает с моделями.)

5) Продакшен: только alembic upgrade head; init_db(create_all) — только локально/тесты.

6) Новая миграция после изменения моделей:
   alembic revision --autogenerate -m "описание"
   (проверить diff вручную перед применением.)
