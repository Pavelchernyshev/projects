#!/usr/bin/env python3
"""Генератор справочников docs/sources.md и docs/texts-bot.md.

Оба файла собираются из кода, а не пишутся руками, — иначе документация
разойдётся с тем, что бот на самом деле говорит и цитирует.

    python scripts/build_docs.py          # перезаписать файлы
    python scripts/build_docs.py --check  # только проверить актуальность

Проверка на актуальность запускается и тестом tests/test_docs.py, так что
забыть перегенерировать не получится.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from myway.i18n import STRINGS  # noqa: E402
from myway.models import Domain, Lang  # noqa: E402
from myway.science.library import CROSS_CUTTING, Library  # noqa: E402

DOCS = ROOT / "docs"

WARNING = (
    "<!-- ФАЙЛ СОБИРАЕТСЯ АВТОМАТИЧЕСКИ. Правки здесь потеряются. -->\n"
    "<!-- Источник данных: {source}. Пересобрать: python scripts/build_docs.py -->\n"
)

DOMAIN_TITLE = {
    "time": "Время",
    "social": "Отношения",
    "mental": "Психика",
    "physical": "Тело",
    "financial": "Деньги",
    CROSS_CUTTING: "Изменение поведения (общее для всех сфер)",
}

STRENGTH_TITLE = {
    "strong": "сильная",
    "moderate": "средняя",
    "suggestive": "слабая",
}

# Где и когда пользователь видит каждую строку. Держится здесь, а не в i18n.py,
# чтобы не тащить документацию в рантайм. Полнота проверяется ниже: добавили
# строку в i18n — обязаны описать её тут, иначе сборка падает.
WHEN_SHOWN = {
    "greeting": "Команда /start — первое, что видит человек.",
    "help": "Команда /help — список команд.",
    "about": "Команда /about — что это такое и границы применимости.",
    "opening_question": "Сразу после /begin. Единственный открытый вопрос интервью.",
    "pulse_intro": "После ответа на открытый вопрос, перед оценками сфер.",
    "pulse_prompt": "Подпись к каждой из пяти кнопочных оценок (1–5).",
    "pulse_done": "После пятой оценки, перед первым уточняющим вопросом.",
    "thinking": "Пока модель готовит вердикт (занимает 10–40 секунд).",
    "verdict_header": "Заголовок первого сообщения вердикта.",
    "verdict_why": "Подзаголовок: почему выбрана именно эта сфера.",
    "verdict_notnow": "Перечисление отложенных сфер.",
    "verdict_action": "Заголовок сообщения с планом действия.",
    "verdict_evidence": "Заголовок сообщения со ссылками на исследования.",
    "evidence_caveat": "Оговорка под ссылками: данные подтверждают направление, не результат.",
    "commit_prompt": "После плана — просьба подтвердить или возразить.",
    "committed": "После подтверждения плана. Сессия закрывается.",
    "escalation": "Если модель считает картину клинической. Показывается ПЕРЕД планом.",
    "crisis": "Если в сообщении сработал скрин на угрозу жизни. Интервью прерывается.",
    "no_session": "Сообщение пришло, а интервью не идёт.",
    "cancelled": "Команда /cancel.",
    "forgotten": "Команда /forget — всё удалено.",
    "lang_switched": "Команда /lang.",
    "voice_unsupported": "Голосовое сообщение при STT_BACKEND=none.",
    "transcribing": "Пока расшифровывается голосовое сообщение.",
    "transcribe_failed": "Расшифровка не удалась.",
    "too_short": "Ответ короче 15 символов — интервью на таком не построить.",
    "engine_error": "Сбой обращения к модели. Ответы сохранены.",
    "not_allowed": "Пользователь не в ALLOWLIST.",
    "status": "Команда /status.",
    "sources_header": "Первое сообщение команды /sources.",
}


def build_sources() -> str:
    lib = Library()
    unverified = lib.unverified()

    out: list[str] = [WARNING.format(source="src/myway/science/corpus/*.yaml")]
    out.append("# Библиотека исследований\n")
    out.append(
        "Полный список работ, на которые бот имеет право ссылаться. Больше он не "
        "может сослаться ни на что: модель возвращает только идентификаторы из "
        "этого списка, а выходные данные подставляет приложение. Подробнее — "
        "[bot-logic.md](bot-logic.md#гарантия-ссылок).\n"
    )
    out.append(
        f"**Всего записей:** {len(lib)} · "
        f"**проверено человеком:** {len(lib) - len(unverified)} · "
        f"**не проверено:** {len(unverified)}\n"
    )
    out.append(
        "> **Что значит «не проверено».** Флаг `verified` означает, что человек "
        "открыл статью и убедился: наша формулировка вывода честно передаёт то, "
        "что в работе действительно найдено. Пока флаг `false` — публиковать "
        "бота на реальных людей нельзя.\n"
        ">\n"
        "> Проверить DOI автоматически: `python scripts/verify_corpus.py --resolve-doi`. "
        "Это подтверждает, что ссылка ведёт на ту статью, но не проверяет "
        "формулировку вывода — это может сделать только человек.\n"
    )
    out.append("**Как редактировать:** правьте YAML-файлы в "
               "`src/myway/science/corpus/`, затем `python scripts/build_docs.py`.\n")

    for domain in [d.value for d in Domain.ordered()] + [CROSS_CUTTING]:
        citations = lib.for_domain(domain)
        if not citations:
            continue
        out.append(f"\n## {DOMAIN_TITLE[domain]}\n")
        out.append(f"Файл: `src/myway/science/corpus/{domain}.yaml` · записей: {len(citations)}\n")
        for c in citations:
            flag = "проверено" if c.verified else "**НЕ проверено**"
            out.append(f"\n### `{c.id}`\n")
            out.append(f"{c.finding_ru}\n")
            out.append(f"- **Источник:** {c.authors} ({c.year}). {c.title}. {c.venue}")
            if c.doi:
                out.append(f"- **DOI:** [{c.doi}](https://doi.org/{c.doi})")
            if c.design:
                out.append(f"- **Дизайн исследования:** {c.design}")
            out.append(f"- **Сила доказательства:** {STRENGTH_TITLE.get(c.strength, c.strength)}")
            out.append(f"- **Статус:** {flag}")
            out.append(f"- **Формулировка на английском:** {c.finding_en}")
    return "\n".join(out).rstrip() + "\n"


def build_texts_bot() -> str:
    missing = sorted(set(STRINGS) - set(WHEN_SHOWN))
    if missing:
        raise SystemExit(
            "В WHEN_SHOWN (scripts/build_docs.py) не описаны строки: "
            + ", ".join(missing)
            + "\nДобавьте описание — иначе документация будет неполной."
        )
    stale = sorted(set(WHEN_SHOWN) - set(STRINGS))
    if stale:
        raise SystemExit(
            "В WHEN_SHOWN описаны строки, которых больше нет в i18n.py: "
            + ", ".join(stale)
        )

    out: list[str] = [WARNING.format(source="src/myway/i18n.py")]
    out.append("# Тексты бота\n")
    out.append(
        "Все реплики самого бота. Это не то, что пишет модель, — вердикты и "
        "вопросы интервью она формулирует сама, ими управляют промпты в "
        "[bot-logic.md](bot-logic.md#промпты).\n"
    )
    out.append(
        "**Как редактировать:** правьте `src/myway/i18n.py`, затем "
        "`python scripts/build_docs.py`. Английские версии остаются в файле — "
        "они понадобятся для англоязычного домена; менять их сейчас не нужно.\n"
    )
    out.append(
        "Фигурные скобки вида `{product}` — подстановки. Их нужно сохранять: "
        "тест `test_placeholders_match_across_languages` падает, если "
        "подстановка потерялась. Разметка — HTML (`<b>` для полужирного), "
        "не Markdown.\n"
    )

    for key in STRINGS:
        out.append(f"\n## `{key}`\n")
        out.append(f"*{WHEN_SHOWN[key]}*\n")
        out.append("```")
        out.append(STRINGS[key][Lang.RU])
        out.append("```")
    return "\n".join(out).rstrip() + "\n"


TARGETS = {
    "sources.md": build_sources,
    "texts-bot.md": build_texts_bot,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="не писать, только сверить")
    args = parser.parse_args()

    DOCS.mkdir(exist_ok=True)
    stale = []
    for name, builder in TARGETS.items():
        path = DOCS / name
        fresh = builder()
        if args.check:
            current = path.read_text(encoding="utf-8") if path.exists() else ""
            if current != fresh:
                stale.append(name)
            continue
        path.write_text(fresh, encoding="utf-8")
        print(f"собран docs/{name} ({len(fresh.splitlines())} строк)")

    if args.check:
        if stale:
            print("устарело: " + ", ".join(stale))
            print("пересоберите: python scripts/build_docs.py")
            return 1
        print("docs актуальны")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
