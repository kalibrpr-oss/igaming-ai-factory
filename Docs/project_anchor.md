# ПРОЕКТНЫЙ ЯКОРЬ - CONVEER / IGAMING AI-FACTORY

## ОБЩЕЕ
- Рабочее бренд-имя: Conveer.
- Продукт: SaaS для генерации SEO-статей, в первую очередь под iGaming/casino SEO, с архитектурой без жесткой привязки только к этой нише.
- Смысл продукта: AI-конвейер для генерации SEO-текстов с ручной модерацией на старте.
- Текущий режим: MVP, локальная разработка на Windows.
- Стиль продукта: темный, технологичный, premium, слегка агрессивный, без мягкой блогерской подачи.

## КЛЮЧЕВАЯ ИДЕЯ ПРОДУКТА
1. Клиент регистрируется.
2. Подтверждает почту кодом.
3. Логинится.
4. Пополняет внутренний баланс.
5. Создает заказ.
6. Система считает цену.
7. Если хватает баланса - списывает.
8. После оплаты можно генерировать текст.
9. Текст уходит на ручной review.
10. Только после approve клиент получает результат.

## ПРАВИЛА ПОЛЬЗОВАТЕЛЯ
- Отвечать кратко, профессионально, без воды.
- Не подлизывать и не льстить.
- Если мнение расходится с пользователем - коротко объяснить почему.
- Опираться на современные, качественные, эталонные решения.
- Все, что предназначено для копирования, давать одним цельным блоком.
- Промпты для Cursor давать одним непрерывным блоком.
- Важные действия, которые требуются от пользователя, выделять максимально явно.
- Если для продолжения нужен перезапуск backend, всегда отдельно и четко писать, как именно это сделать.
- Когда пользователь просит пошагово, идти по одному шагу.
- Не закапываться бесконечно в одну проблему; если нужен радикальный путь, предлагать его.
- Стиль общения: прямой, собранный, без лишней мягкости.
- Для дизайна и продукта ориентир - польза для клиента и продукта, а не личные вкусы ассистента.

## ПРАВИЛА ДЛЯ CURSOR / АГЕНТА
- Не делать быстро и кое-как.
- Не ломать текущую архитектуру.
- Не прыгать через этапы без необходимости.
- Не плодить лишние сущности.
- Не дублировать логику.
- Если правка точечная - править точечно.
- Ничего не менять сверх поставленной задачи.
- Если задача только на аудит/план - не кодить.
- В ответе четко перечислять: какие файлы изменены, что сделано, что дальше.
- Деньги, баланс, расчеты, права доступа - только на backend.

## ТЕХСТЕК
- Frontend: Next.js, папка `apps/web`.
- Backend: FastAPI, папка `backend/app`.
- База: PostgreSQL локально.
- Миграции: Alembic.
- Redis упоминается в env, но не основная текущая точка.
- Email: SMTP через Mail.ru.
- LLM: базовая завязка под Anthropic/Claude, но текущий фокус не на модели, а на product/backend flow.

## СТРУКТУРА ПРОЕКТА
- `apps/web` - frontend.
- `backend/app` - backend.
- `backend/alembic` - миграции.
- `backend/.env` - локальные env backend.
- В backend есть модели: users/orders/payments/balance_transactions/email_verification.
- Есть auth/orders/admin routes и сервисы auth/payments/orders/mail/llm.

## ЧТО РЕАЛИЗОВАНО ПО BACKEND
1. Auth foundation:
   - register;
   - login;
   - me;
   - verify-email;
   - resend-verification-email;
   - email verification token model;
   - user fields: `email_verified_at`, `is_email_verified`, `balance_cents`, `referral_code`, `referrer_user_id`, `first_order_bonus_expires_at`, `first_order_bonus_consumed_at`.
2. Email verification:
   - токены создаются;
   - есть verify endpoint;
   - есть resend;
   - токены одноразовые;
   - TTL ужат до разумного;
   - есть rate limiting на выпуск verification token.
3. Mail:
   - реализован `SmtpEmailSender`;
   - `MAIL_TRANSPORT=smtp`;
   - SMTP через `smtp.mail.ru`;
   - почта: `conveer.ai@mail.ru`;
   - app password добавлен в `backend/.env`;
   - IMAP/POP/SMTP доступ на стороне Mail.ru включен.
4. Users/Orders/Payments/Balance:
   - `User` расширен;
   - `Order` расширен breakdown-ценой и moderation полями;
   - `Payment` расширен (`kind`, `user_id`, nullable `order_id`);
   - `BalanceTransaction` добавлен как ledger;
   - есть логика внутреннего баланса.
5. Pricing:
   - фикс: 0.7 RUB/слово;
   - breakdown: `price_base_cents`, `discount_cents`, `price_cents`;
   - бонус первого заказа: 30% / 7 дней / применяется один раз / фиксируется в `User`.
6. Order payment:
   - списание с баланса за заказ;
   - идемпотентность;
   - order debit transaction;
   - корректная ошибка при недостатке средств.
7. Internal wallet test flow:
   - есть dev/test mock topup + confirm;
   - использовалось для проверки денежного контура;
   - не продовый способ оплаты.
8. Generation flow:
   - генерация только для paid order;
   - после генерации статус `review_required`;
   - `generated_text` сохраняется в order;
   - при ошибке генерации статус `failed`.
9. Review flow:
   - есть review queue для admin;
   - approve -> `completed`;
   - reject -> `paid`;
   - reject не использует `failed`;
   - moderation fields: `moderated_at`, `moderated_by_user_id`, `moderation_notes`.
10. Result delivery protection:
    - клиент не видит `generated_text`, пока `order.status != completed`;
    - `generated_text` маскируется в пользовательских responses до `completed`.
11. CORS:
    - была ошибка OPTIONS 400;
    - исправлялось через `CORSMiddleware`;
    - важный нюанс: frontend может идти не с localhost, а с `172.18.0.1:3333` (next-server/VPN/dev-среда).
12. SQLAlchemy issue:
    - `AmbiguousForeignKeysError` между `Order.user` и `Order.moderator`;
    - исправлено явным `foreign_keys` в `models/order.py` и `models/user.py`.
13. Password hashing:
    - была проблема passlib/bcrypt на Windows и лимит bcrypt 72 bytes;
    - переход на Argon2 (`passlib[argon2]` + `argon2-cffi`);
    - регистрация перестала падать на `hash_password`.

## ЧТО РЕАЛИЗОВАНО ПО FRONTEND
- Есть landing.
- Есть register page.
- Есть login page.
- Есть dashboard/кабинет.
- Исправлено:
  - после register больше нет автологина;
  - после register переход на `/verify-email?email=...`.
- Добавлена verify-email page.
- Login должен быть закрыт для неподтвержденного email.
- `AuthGate` проверяет `/auth/me` и не должен пускать неподтвержденного пользователя в кабинет.

## ДИЗАЙН / БРЕНД
- Бренд: Conveer.
- Почему выбран:
  - звучит как бренд;
  - ассоциация с conveyor/конвейером;
  - подходит под AI pipeline;
  - сильнее, чем Konveer.
- Визуал:
  - темный;
  - premium;
  - технологичный;
  - не мягкий.
- Обсуждались карточки стилей, персонажи, иллюстрации, световые эффекты, кнопки, иконки, визуальный баланс hero и другие UI-детали.

## CONTENT / STYLE LOGIC
- В продукте есть стили текстов: Aggressive / Expert / Friendly.
- Критично для тона:
  - без уныния;
  - без тильта, лузстрика и депрессивных вайбов;
  - без очевидного AI-запаха;
  - без одинаковой подачи у всех стилей.
- Стилевые требования:
  - Aggressive - харизматичный, жесткий, энергичный;
  - Expert - спокойный и точный;
  - Friendly - теплый и понятный.
- Пользователь чувствителен к tone и клиентскому ощущению.

## ЧТО УЖЕ ДЕЛАЛ ПОЛЬЗОВАТЕЛЬ РУКАМИ
- Создал почту `conveer.ai@mail.ru`.
- Включал 2FA, пароли приложений и SMTP-доступ.
- Создал `backend/.env` и добавил SMTP settings.
- Установил Python 3.12.
- Установил PostgreSQL 16.
- Через `psql` создал базу `igaming_factory`.
- Научился вручную запускать backend:
  - `cd "C:\Users\user\Desktop\iGaming Project\backend"`
  - `python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`
- Научился держать отдельно frontend и backend терминалы.

## ТЕКУЩАЯ ТОЧКА / ГЛАВНАЯ НЕЗАВЕРШЕННАЯ ПРОБЛЕМА
- Регистрация доходит до экрана ввода кода, но письмо с кодом не приходит.
- Уже известно:
  - регистрация проходит;
  - verify-email page открывается;
  - backend не валится;
  - письмо не видно во входящих.
- Возможные причины:
  - SMTP send реально падает;
  - письмо уходит в spam;
  - mail sender логирует ошибку, но не валит регистрацию;
  - проблема в Mail.ru SMTP или в логике вызова send task.
- Что проверять первым:
  1. backend logs после регистрации;
  2. есть ли `SMTP send start/success/failed`;
  3. вызывается ли `tasks.send_verification_email_task`;
  4. нет ли SMTP auth error;
  5. нет ли проблем с sender/from;
  6. приходит ли письмо в spam;
  7. если SMTP не взлетит быстро - рассмотреть временный запасной sender/provider.

## ЧТО УЖЕ НЕ НУЖНО ПЕРЕДЕЛЫВАТЬ
- CORS уже не основная проблема.
- Python/PostgreSQL уже установлены.
- БД уже создана.
- Argon2 уже внедрен.
- verify-email page уже есть.
- backend в целом запускается стабильно.

## КАК ПЕРЕЗАПУСКАТЬ BACKEND
Если backend уже запущен:
1. В терминале backend нажать `Ctrl + C`.
2. Запустить снова:
   - `cd "C:\Users\user\Desktop\iGaming Project\backend"`
   - `python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`

## КАК ЗАПУСКАТЬ FRONTEND
Обычно:
1. Открыть терминал frontend.
2. Перейти:
   - `cd "C:\Users\user\Desktop\iGaming Project\apps\web"`
3. Запустить:
   - `npm run dev`
- Если `3333 already in use`, значит frontend уже где-то запущен.

## ЧТО ДАЛЬШЕ ПО ПРОДУКТУ
- Ближайшее:
  - добить SMTP/доставку кода;
  - проверить verify-email end-to-end;
  - после этого идти в реальные платежи;
  - потом UX/polish/admin improvements.
- Среднесрочное:
  - реальная оплата через провайдера;
  - реферальная система;
  - email result/delivery;
  - DOCX/экспорт;
  - production deploy.
- Дальняя цель:
  - полноценный SaaS для SEO article generation pipeline с устойчивой экономикой, балансом, оплатами, review и масштабированием.

## BACKLOG — НЕ ЗАБЫТЬ (после регистрации / к продакшену)
Зафиксировано по запросу владельца — реализовать, когда дойдём очереди:
- **Сброс пароля** — flow «забыл пароль», письмо со ссылкой/кодом, срок жизни токена.
- **Лимиты и антибот по IP** — rate limit на `/auth/*`, регистрацию, resend; при необходимости капча/turnstile.
- **Письма и доставляемость** — SPF, DKIM, DMARC, нормальный From, тесты на попадание во «Входящие», не только SMTP «отправилось».
- **Юридическое** — публичные страницы: оферта, политика конфиденциальности; чекбоксы/ссылки при регистрации и в футере; актуальность под юрисдикцию продукта.

## CHECKLIST ДЛЯ НОВОГО ЧАТА
- Проект называется Conveer.
- Нужен быстрый, прямой, рабочий стиль общения.
- Не подлизывать.
- Всегда явно писать, как перезапускать backend, если это нужно.
- Уже реализован почти весь MVP-контур.
- Главная текущая проблема: код подтверждения email не приходит.
- Начинать с диагностики SMTP-отправки после регистрации.
- Не возвращаться к закрытым темам без причины.
- Все промпты для Cursor давать одним цельным блоком.
- Все для копирования давать в одном code block.
