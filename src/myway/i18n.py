"""User-facing copy in Russian and English.

The bot's own chrome lives here. Coaching content is generated in the user's
language by the model — see `coach.prompts`.
"""

from __future__ import annotations

from .models import Domain, Lang

STRINGS: dict[str, dict[Lang, str]] = {
    "greeting": {
        Lang.EN: (
            "This is {product}.\n\n"
            "I interview you about where your life is actually leaking, then name "
            "one thing to fix — not five. The direction I point you in is backed by "
            "published research, and I show you the sources.\n\n"
            "Two things I am not: a therapist, and a source of encouragement.\n\n"
            "Answer by text or voice — whichever is easier. Voice is usually more honest.\n\n"
            "/begin to start. /help for everything else."
        ),
        Lang.RU: (
            "Это {product}.\n\n"
            "Я расспрошу вас о том, где ваша жизнь на самом деле теряет силы, а затем "
            "назову одну вещь, которую нужно исправить, — не пять. Направление, в которое "
            "я вас направляю, опирается на опубликованные исследования, и я показываю "
            "источники.\n\n"
            "Чем я не являюсь: терапевтом и источником подбадривания.\n\n"
            "Отвечайте текстом или голосом — как удобнее. Голосом обычно честнее.\n\n"
            "/begin — начать. /help — всё остальное."
        ),
    },
    "help": {
        Lang.EN: (
            "/begin — start a new interview\n"
            "/status — where we are right now\n"
            "/lang — switch between Russian and English\n"
            "/sources — the research library behind the advice\n"
            "/cancel — abandon the current interview\n"
            "/forget — delete everything I hold about you\n"
            "/about — what this is and what it is not"
        ),
        Lang.RU: (
            "/begin — начать новое интервью\n"
            "/status — на каком мы этапе\n"
            "/lang — переключить русский/английский\n"
            "/sources — библиотека исследований, на которых всё держится\n"
            "/cancel — прервать текущее интервью\n"
            "/forget — удалить всё, что я о вас храню\n"
            "/about — что это такое и чем это не является"
        ),
    },
    "about": {
        Lang.EN: (
            "{product} works across five types of wealth — time, social, mental, "
            "physical, financial — a framing drawn from Sahil Bloom's "
            "\"The 5 Types of Wealth\" (2025).\n\n"
            "Every claim I make about what tends to work comes from a fixed library of "
            "peer-reviewed studies that ship with this bot. I cannot cite a paper that "
            "is not in it, which means I cannot invent one. Run /sources to read the "
            "whole library.\n\n"
            "What that evidence does and does not do: it supports the direction of the "
            "advice. Most of these effects are small to moderate, measured across "
            "populations, and none of them predict what will happen to you specifically. "
            "Anyone who tells you otherwise is selling something.\n\n"
            "I am not a clinician. If what you are dealing with needs a professional, I "
            "will say so and stop."
        ),
        Lang.RU: (
            "{product} работает с пятью видами богатства — время, отношения, психика, "
            "тело, деньги. Эта рамка взята из книги Сахила Блума "
            "«The 5 Types of Wealth» (2025).\n\n"
            "Каждое утверждение о том, что обычно работает, взято из фиксированной "
            "библиотеки рецензируемых исследований, которая поставляется вместе с ботом. "
            "Я не могу сослаться на работу, которой там нет, а значит, не могу её "
            "выдумать. Вся библиотека — по команде /sources.\n\n"
            "Что эти данные дают и чего не дают: они подтверждают направление совета. "
            "Большинство эффектов небольшие или умеренные, измерены на группах людей, и "
            "ни один из них не предсказывает, что произойдёт именно с вами. Кто говорит "
            "иначе — вам что-то продаёт.\n\n"
            "Я не врач. Если то, с чем вы имеете дело, требует специалиста, я скажу это "
            "прямо и остановлюсь."
        ),
    },
    "opening_question": {
        Lang.EN: (
            "One question to start, and take it seriously.\n\n"
            "What is the thing you keep meaning to deal with and keep not dealing with?\n\n"
            "Not the tidy version. Voice note is fine."
        ),
        Lang.RU: (
            "Один вопрос для начала — и отнеситесь к нему серьёзно.\n\n"
            "Что вы всё собираетесь решить и всё никак не решаете?\n\n"
            "Не причёсанную версию. Голосовое сообщение — нормально."
        ),
    },
    "pulse_intro": {
        Lang.EN: (
            "Now a quick baseline. Rate each of the five, 1 to 5.\n"
            "1 = badly broken. 5 = genuinely strong. Answer fast; first instinct is "
            "more accurate than a considered one."
        ),
        Lang.RU: (
            "Теперь быстрая базовая оценка. Оцените каждую из пяти сфер от 1 до 5.\n"
            "1 = совсем плохо. 5 = действительно сильно. Отвечайте быстро: первая "
            "реакция точнее продуманной."
        ),
    },
    "pulse_prompt": {
        Lang.EN: "{icon} <b>{domain}</b> — {hint}",
        Lang.RU: "{icon} <b>{domain}</b> — {hint}",
    },
    "pulse_done": {
        Lang.EN: "Baseline recorded. Now the part that actually matters.",
        Lang.RU: "Базовая оценка записана. Теперь то, что действительно важно.",
    },
    "thinking": {
        Lang.EN: "Working through what you told me…",
        Lang.RU: "Разбираю то, что вы рассказали…",
    },
    "verdict_header": {
        Lang.EN: "<b>The one thing</b>",
        Lang.RU: "<b>Одна вещь</b>",
    },
    "verdict_why": {
        Lang.EN: "<b>Why this and not the rest</b>",
        Lang.RU: "<b>Почему именно это, а не остальное</b>",
    },
    "verdict_notnow": {
        Lang.EN: "<b>Not now:</b> {domains}",
        Lang.RU: "<b>Не сейчас:</b> {domains}",
    },
    "verdict_action": {
        Lang.EN: "<b>What you do</b>",
        Lang.RU: "<b>Что вы делаете</b>",
    },
    "verdict_evidence": {
        Lang.EN: "<b>What the research says</b>",
        Lang.RU: "<b>Что говорят исследования</b>",
    },
    "evidence_caveat": {
        Lang.EN: (
            "These findings support the direction, not a guarantee. Effects are mostly "
            "small to moderate and measured across populations, not people."
        ),
        Lang.RU: (
            "Эти данные подтверждают направление, а не гарантию. Эффекты в основном "
            "небольшие или умеренные и измерены на группах, а не на отдельных людях."
        ),
    },
    "commit_prompt": {
        Lang.EN: (
            "Last thing. Reply <b>yes</b> if you are doing this, or tell me what you would "
            "change about it. If you would not do it, say that — a plan you will not "
            "start is worse than no plan."
        ),
        Lang.RU: (
            "Последнее. Ответьте <b>да</b>, если вы это делаете, или скажите, что бы вы "
            "изменили. Если не будете делать — так и скажите: план, который не начнут, "
            "хуже, чем отсутствие плана."
        ),
    },
    "committed": {
        Lang.EN: (
            "Recorded. I will ask you about it — that is not a courtesy, tracking your "
            "own progress measurably improves the odds you follow through.\n\n"
            "/begin when you want to look at the next thing. Not before you have moved "
            "on this one."
        ),
        Lang.RU: (
            "Записано. Я о нём спрошу — и это не вежливость: отслеживание собственного "
            "прогресса измеримо повышает шансы дойти до конца.\n\n"
            "/begin — когда захотите взяться за следующее. Не раньше, чем сдвинете это."
        ),
    },
    "escalation": {
        Lang.EN: (
            "Before the plan: what you are describing looks like something that needs a "
            "professional rather than a coaching bot. That is not a brush-off, and it is "
            "not a diagnosis — it is the honest read. Cognitive behavioural therapy has "
            "the strongest evidence base of any psychological treatment for problems "
            "shaped like this. Please talk to someone licensed."
        ),
        Lang.RU: (
            "Прежде чем план: то, что вы описываете, похоже на ситуацию, где нужен "
            "специалист, а не коуч-бот. Это не отговорка и не диагноз — это честная "
            "оценка. У когнитивно-поведенческой терапии самая сильная доказательная база "
            "среди психологических методов для проблем такой формы. Пожалуйста, "
            "обратитесь к лицензированному специалисту."
        ),
    },
    "crisis": {
        Lang.EN: (
            "I am stopping the interview here.\n\n"
            "What you just wrote needs a person, not a bot. Please contact your local "
            "emergency number or a crisis line right now. In many countries you can "
            "reach one by dialling 112; the international directory at "
            "findahelpline.com lists services by country.\n\n"
            "I am not equipped for this and I am not going to pretend otherwise."
        ),
        Lang.RU: (
            "Я останавливаю интервью.\n\n"
            "То, что вы написали, требует человека, а не бота. Пожалуйста, свяжитесь "
            "прямо сейчас со службой экстренной помощи или кризисной линией. Во многих "
            "странах это номер 112; международный справочник findahelpline.com "
            "перечисляет службы по странам.\n\n"
            "Я для этого не приспособлен и не буду делать вид, что это не так."
        ),
    },
    "no_session": {
        Lang.EN: "No interview in progress. /begin to start one.",
        Lang.RU: "Интервью не идёт. /begin — начать.",
    },
    "cancelled": {
        Lang.EN: "Interview abandoned. /begin when you want to try again.",
        Lang.RU: "Интервью прервано. /begin — когда захотите попробовать снова.",
    },
    "forgotten": {
        Lang.EN: "Deleted: {count} session(s), all transcripts, and your language setting.",
        Lang.RU: "Удалено: сессий — {count}, все расшифровки и настройка языка.",
    },
    "lang_switched": {
        Lang.EN: "Switched to English.",
        Lang.RU: "Переключено на русский.",
    },
    "voice_unsupported": {
        Lang.EN: "Voice notes are turned off on this instance. Please type your answer.",
        Lang.RU: "Голосовые сообщения на этом сервере отключены. Напишите ответ текстом.",
    },
    "transcribing": {
        Lang.EN: "Listening…",
        Lang.RU: "Слушаю…",
    },
    "transcribe_failed": {
        Lang.EN: "I could not make out that recording. Try again, or type it.",
        Lang.RU: "Не смог разобрать запись. Попробуйте снова или напишите текстом.",
    },
    "too_short": {
        Lang.EN: (
            "That is not enough to work with. Give me a couple of sentences — what "
            "actually happens, not the summary."
        ),
        Lang.RU: (
            "С этим не поработать. Дайте пару предложений — что происходит на самом "
            "деле, а не итог."
        ),
    },
    "engine_error": {
        Lang.EN: (
            "Something broke on my side. Your answers are saved — send anything to "
            "retry, or /cancel to drop it."
        ),
        Lang.RU: (
            "У меня что-то сломалось. Ваши ответы сохранены — отправьте что угодно, "
            "чтобы повторить, или /cancel, чтобы прервать."
        ),
    },
    "not_allowed": {
        Lang.EN: "This instance is private.",
        Lang.RU: "Этот бот приватный.",
    },
    "status": {
        Lang.EN: "Stage: {state}. Questions answered: {answers}.",
        Lang.RU: "Этап: {state}. Отвечено вопросов: {answers}.",
    },
    "sources_header": {
        Lang.EN: (
            "The full library — {count} studies. I can cite from this list and nothing "
            "else.\n"
        ),
        Lang.RU: (
            "Полная библиотека — {count} исследований. Я могу ссылаться только на этот "
            "список и ни на что другое.\n"
        ),
    },
}

DOMAIN_LABEL: dict[Domain, dict[Lang, str]] = {
    Domain.TIME: {Lang.EN: "Time", Lang.RU: "Время"},
    Domain.SOCIAL: {Lang.EN: "Social", Lang.RU: "Отношения"},
    Domain.MENTAL: {Lang.EN: "Mental", Lang.RU: "Психика"},
    Domain.PHYSICAL: {Lang.EN: "Physical", Lang.RU: "Тело"},
    Domain.FINANCIAL: {Lang.EN: "Financial", Lang.RU: "Деньги"},
}

DOMAIN_HINT: dict[Domain, dict[Lang, str]] = {
    Domain.TIME: {
        Lang.EN: "control over your hours and attention",
        Lang.RU: "контроль над своими часами и вниманием",
    },
    Domain.SOCIAL: {
        Lang.EN: "depth and reliability of your relationships",
        Lang.RU: "глубина и надёжность ваших отношений",
    },
    Domain.MENTAL: {
        Lang.EN: "clarity, sleep, recovery, thoughts that stop circling",
        Lang.RU: "ясность, сон, восстановление, мысли, которые не ходят по кругу",
    },
    Domain.PHYSICAL: {
        Lang.EN: "movement, strength, energy, health",
        Lang.RU: "движение, сила, энергия, здоровье",
    },
    Domain.FINANCIAL: {
        Lang.EN: "security, buffer, freedom from money anxiety",
        Lang.RU: "защищённость, запас, свобода от тревоги о деньгах",
    },
}

DOMAIN_ICON: dict[Domain, str] = {
    Domain.TIME: "⏳",
    Domain.SOCIAL: "👥",
    Domain.MENTAL: "🧠",
    Domain.PHYSICAL: "💪",
    Domain.FINANCIAL: "💰",
}

STATE_LABEL: dict[str, dict[Lang, str]] = {
    "onboarding": {Lang.EN: "not started", Lang.RU: "не начато"},
    "opening": {Lang.EN: "opening question", Lang.RU: "первый вопрос"},
    "pulse": {Lang.EN: "baseline ratings", Lang.RU: "базовые оценки"},
    "probe": {Lang.EN: "interview", Lang.RU: "интервью"},
    "verdict": {Lang.EN: "verdict", Lang.RU: "вердикт"},
    "commit": {Lang.EN: "commitment", Lang.RU: "обязательство"},
    "idle": {Lang.EN: "between sessions", Lang.RU: "между сессиями"},
}


def t(key: str, lang: Lang, **kwargs: object) -> str:
    """Look up a string and format it. Unknown keys fail loudly in tests."""
    try:
        template = STRINGS[key][lang]
    except KeyError as exc:
        raise KeyError(f"missing translation: {key}/{lang.value}") from exc
    return template.format(**kwargs) if kwargs else template


def domain_label(domain: Domain, lang: Lang) -> str:
    return DOMAIN_LABEL[domain][lang]


def domain_hint(domain: Domain, lang: Lang) -> str:
    return DOMAIN_HINT[domain][lang]


def state_label(state: str, lang: Lang) -> str:
    return STATE_LABEL.get(state, {}).get(lang, state)
