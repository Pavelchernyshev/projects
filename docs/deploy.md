# Запуск и деплой

Две независимые части: бот (нужен сервер, работает постоянно) и лендинг
(статика на Cloudflare Pages).

## Бот

### Локально

```bash
cp .env.example .env      # вписать TELEGRAM_BOT_TOKEN и ANTHROPIC_API_KEY
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python -m myway
```

Токен бота — у [@BotFather](https://t.me/BotFather): `/newbot`, дальше по
подсказкам. Полученное имя (вида `moyput_bot`) нужно подставить и в лендинг —
см. ниже.

### В Docker

```bash
cp .env.example .env
docker compose up -d
docker compose logs -f
```

Два тома: `/data` — база SQLite, `/models` — кеш весов Whisper (иначе они
скачиваются заново при каждом перезапуске). В образе стоит ffmpeg для
голосовых.

### Настройки

Полный список с пояснениями — в `.env.example`. Те, что меняют чаще всего:

| Переменная | По умолчанию | Что делает |
|---|---|---|
| `PRODUCT_NAME` | `Мой Путь` | Название в приветствии и `/about` |
| `DEFAULT_LANG` | `ru` | Язык для нового пользователя |
| `MODEL_DIAGNOSIS` / `EFFORT_DIAGNOSIS` | `claude-opus-5` / `high` | Вердикт |
| `MODEL_PROBE` / `EFFORT_PROBE` | `claude-opus-5` / `low` | Уточняющие вопросы |
| `MIN_PROBE_QUESTIONS` / `MAX_PROBE_QUESTIONS` | 3 / 6 | Длина интервью |
| `STT_BACKEND` | `local` | `local` \| `openai` \| `none` |
| `WHISPER_MODEL` | `small` | Больше модель — точнее и медленнее |
| `ALLOWLIST` | пусто | Список telegram id; пусто = доступ всем |

**`ALLOWLIST` полезен на старте**: пока 28 исследований не проверены, имеет
смысл впустить только себя и несколько человек.

### Требования к серверу

Минимум для `STT_BACKEND=local` с моделью `small`: 2 ГБ памяти, 1 ядро, 5 ГБ
диска. С `STT_BACKEND=none` или `openai` хватит 512 МБ. Постоянный исходящий
доступ к `api.anthropic.com` и `api.telegram.org`.

Бот работает через long polling, поэтому публичный IP и домен ему не нужны — это
заметно упрощает размещение.

### Что проверить перед публичным запуском

1. `python scripts/verify_corpus.py --resolve-doi` — проходит без ошибок.
2. Все 28 записей помечены `verified: true` (см. [sources.md](sources.md)).
3. `PYTHONPATH=src python -m pytest` — зелёный.
4. Пройти интервью самому от начала до конца.
5. Проверить кризисный скрин: написать боту фразу-триггер и убедиться, что он
   останавливается и выдаёт контакты помощи.
6. Проверить `/forget` и убедиться, что данные действительно исчезли.

---

## Лендинг

Один файл `web/index.html`, без сборки. Перед деплоем — подставить имя бота:

```bash
sed -i '' 's|t.me/moyput_bot|t.me/НАСТОЯЩЕЕ_ИМЯ|g' web/index.html
```

### Cloudflare Pages

**Вариант А — из репозитория, деплой на каждый push:**

Cloudflare → Workers & Pages → Create → Pages → Connect to Git → этот
репозиторий, затем:

| Настройка | Значение |
|---|---|
| Production branch | ваша основная ветка |
| Framework preset | None |
| Build command | *(пусто)* |
| Build output directory | `web` |

**Вариант Б — загрузка с машины:**

```bash
npx wrangler pages deploy web --project-name moyput
```

### Домен

В проекте Pages → Custom domains → добавить `moyput.com`, затем
`www.moyput.com`. Записи создадутся сами, сертификат выпустится за минуту-две.

Чтобы `www` не отдавал копию страницы, а перенаправлял на основной адрес:
Rules → Redirect Rules → Create → hostname равен `www.moyput.com` → 301 на
`https://moyput.com/${http.request.uri.path}`.

---

## Перенос DNS с GoDaddy на Cloudflare

Регистратор остаётся GoDaddy, меняются только серверы имён. Трансфера нет,
платы нет, 60-дневной блокировки нет.

### Сначала две проверки — на них ломается чаще всего

1. **Есть ли почта на домене?** Если на moyput.com заведены ящики (GoDaddy,
   Microsoft 365, Google Workspace) — откройте страницу DNS в GoDaddy и
   выпишите **все** записи `MX` и записи `TXT` для SPF, DKIM, DMARC. Их нужно
   создать в Cloudflare **до** переключения серверов имён, иначе почта перестанет
   доходить в момент переключения. Автоматическое сканирование Cloudflare —
   вспомогательное, не источник истины.

2. **Включён ли DNSSEC в GoDaddy?** GoDaddy → домен → DNSSEC. Если включён —
   **выключите и подождите час** перед переключением. Оставленный DNSSEC с
   новыми серверами имён приводит к тому, что домен перестаёт разрешаться
   вообще: сайт пропадает, и сбросом кеша это не лечится.

Также отключите в GoDaddy переадресацию домена и страницу-заглушку, если они
настроены.

### Дальше

1. Cloudflare → Add a site → `moyput.com` → тариф Free.
2. Cloudflare покажет найденные записи. **Сверьте со своим списком из пункта 1**
   и добавьте пропущенное.
3. Скопируйте два сервера имён (вида `ada.ns.cloudflare.com`).
4. GoDaddy → My Products → moyput.com → DNS → Nameservers → Change → *I'll use
   my own nameservers* → вставить оба, лишние удалить, сохранить.
5. Подождать. Обычно 5–30 минут, изредка до 48 часов. Cloudflare пришлёт письмо.
   Проверить: `dig +short NS moyput.com`
6. После активации: SSL/TLS → Overview → **Full (strict)**, и SSL/TLS → Edge
   Certificates → **Always Use HTTPS: on**.
7. Если выключали DNSSEC — включите его теперь на стороне Cloudflare (DNS →
   Settings → DNSSEC → Enable) и добавьте выданную запись `DS` обратно в GoDaddy.

### Проверка

```bash
dig +short NS moyput.com                                # серверы Cloudflare
dig +short MX moyput.com                                # почта на месте
curl -sSI https://moyput.com | head -1                  # HTTP/2 200
curl -sSI https://moyput.com | grep -i strict-transport  # заголовки применились
curl -sSI https://www.moyput.com | head -1              # 301, если добавили правило
```

Заголовки безопасности лежат в `web/_headers` — Cloudflare Pages читает этот
файл сам. Политика CSP строгая: страница ничего не подгружает извне.
