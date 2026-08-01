<!-- ФАЙЛ СОБИРАЕТСЯ АВТОМАТИЧЕСКИ. Правки здесь потеряются. -->
<!-- Источник данных: src/myway/science/corpus/*.yaml. Пересобрать: python scripts/build_docs.py -->

# Библиотека исследований

Полный список работ, на которые бот имеет право ссылаться. Больше он не может сослаться ни на что: модель возвращает только идентификаторы из этого списка, а выходные данные подставляет приложение. Подробнее — [bot-logic.md](bot-logic.md#гарантия-ссылок).

**Всего записей:** 28 · **проверено человеком:** 0 · **не проверено:** 28

> **Что значит «не проверено».** Флаг `verified` означает, что человек открыл статью и убедился: наша формулировка вывода честно передаёт то, что в работе действительно найдено. Пока флаг `false` — публиковать бота на реальных людей нельзя.
>
> Проверить DOI автоматически: `python scripts/verify_corpus.py --resolve-doi`. Это подтверждает, что ссылка ведёт на ту статью, но не проверяет формулировку вывода — это может сделать только человек.

**Как редактировать:** правьте YAML-файлы в `src/myway/science/corpus/`, затем `python scripts/build_docs.py`.


## Время

Файл: `src/myway/science/corpus/time.yaml` · записей: 4


### `time.sharif2021`

Благополучие растёт вместе со свободным временем, но выходит на плато примерно на двух часах в день и снижается после пяти. Плохо и когда времени нет совсем, и когда его много, но оно ничем не наполнено. Цель — умеренный защищённый блок, а не максимум пустоты.

- **Источник:** Sharif, Mogilner & Hershfield (2021). Having too little or too much time is linked to lower subjective well-being. Journal of Personality and Social Psychology 121(4)
- **DOI:** [10.1037/pspp0000391](https://doi.org/10.1037/pspp0000391)
- **Дизайн исследования:** Two large datasets (n > 35,000) plus two experiments
- **Сила доказательства:** средняя
- **Статус:** **НЕ проверено**
- **Формулировка на английском:** Well-being rises with discretionary time but plateaus at roughly two hours a day and declines past about five. Having no free time hurts; having nothing to do with a lot of free time hurts too. The target is a moderate, protected block — not maximum emptiness.

### `time.giurge2020`

Дефицит времени — хроническое ощущение, что дел слишком много, а времени слишком мало — предсказывает более низкое благополучие, худшее физическое здоровье и снижение продуктивности, причём в значительной степени независимо от дохода. Нехватка времени — самостоятельный фактор риска, а не просто следствие занятости.

- **Источник:** Giurge, Whillans & West (2020). Why time poverty matters for individuals, organisations and nations. Nature Human Behaviour 4
- **DOI:** [10.1038/s41562-020-0920-z](https://doi.org/10.1038/s41562-020-0920-z)
- **Дизайн исследования:** Review of survey and experimental evidence
- **Сила доказательства:** средняя
- **Статус:** **НЕ проверено**
- **Формулировка на английском:** Time poverty — the chronic sense of having too much to do and too little time — predicts lower well-being, worse physical health, and reduced productivity, and it does so largely independently of income. Feeling short of time is its own risk factor, not just a symptom of being busy.

### `time.whillans2017`

Люди, которые тратят деньги, чтобы избавиться от неприятных задач, сообщают о более высокой удовлетворённости жизнью, а в полевом эксперименте покупка, экономящая время, улучшала настроение к концу дня сильнее, чем материальная покупка на ту же сумму. Большинство по умолчанию покупает вещи, а не время.

- **Источник:** Whillans, Dunn, Smeets, Bekkers & Norton (2017). Buying time promotes happiness. PNAS 114(32)
- **DOI:** [10.1073/pnas.1706541114](https://doi.org/10.1073/pnas.1706541114)
- **Дизайн исследования:** Surveys across several countries plus a field experiment
- **Сила доказательства:** средняя
- **Статус:** **НЕ проверено**
- **Формулировка на английском:** People who spend money to offload disliked tasks report higher life satisfaction, and in a field experiment a time-saving purchase raised end-of-day mood more than a material purchase of the same value. Most people default to buying things rather than buying time.

### `time.mogilner2010`

Когда человека просят подумать о времени, он чаще выбирает общение вместо работы; когда о деньгах — наоборот. То, в чём вы измеряете свои дни, определяет, на что вы их тратите.

- **Источник:** Mogilner (2010). The pursuit of happiness: Time, money, and social connection. Psychological Science 21(9)
- **DOI:** [10.1177/0956797610380696](https://doi.org/10.1177/0956797610380696)
- **Дизайн исследования:** Experiments priming time versus money
- **Сила доказательства:** слабая
- **Статус:** **НЕ проверено**
- **Формулировка на английском:** Being prompted to think about time makes people more likely to choose socialising over working; being prompted to think about money pushes the opposite way. What you measure your days in shapes what you spend them on.

## Отношения

Файл: `src/myway/science/corpus/social.yaml` · записей: 4


### `social.holtlunstad2010`

По данным 148 исследований, у людей с более крепкими социальными связями вероятность выживания за период наблюдения была примерно на 50% выше. Эффект сохранялся после поправки на возраст, пол и исходное состояние здоровья и по величине был сопоставим с такими признанными факторами риска, как курение и ожирение.

- **Источник:** Holt-Lunstad, Smith & Layton (2010). Social relationships and mortality risk: A meta-analytic review. PLoS Medicine 7(7)
- **DOI:** [10.1371/journal.pmed.1000316](https://doi.org/10.1371/journal.pmed.1000316)
- **Дизайн исследования:** Meta-analysis of 148 prospective studies (n ≈ 309,000)
- **Сила доказательства:** сильная
- **Статус:** **НЕ проверено**
- **Формулировка на английском:** Across 148 studies, people with stronger social relationships had roughly a 50% greater likelihood of survival over the follow-up period. The effect held after adjusting for age, sex, and initial health status, and was comparable in size to well-established risk factors like smoking and obesity.

### `social.holtlunstad2015`

Одиночество, объективная социальная изоляция и жизнь в одиночку каждое независимо повышали риск смертности — примерно на 26%, 29% и 32% соответственно. Чувствовать себя одиноким и быть одиноким — разные риски; устранение одного не решает автоматически другое.

- **Источник:** Holt-Lunstad, Smith, Baker, Harris & Stephenson (2015). Loneliness and social isolation as risk factors for mortality: A meta-analytic review. Perspectives on Psychological Science 10(2)
- **DOI:** [10.1177/1745691614568352](https://doi.org/10.1177/1745691614568352)
- **Дизайн исследования:** Meta-analysis of 70 independent prospective studies (n > 3.4 million)
- **Сила доказательства:** сильная
- **Статус:** **НЕ проверено**
- **Формулировка на английском:** Loneliness, objective social isolation, and living alone each independently raised mortality risk — by roughly 26%, 29%, and 32% respectively. Feeling alone and being alone are separate risks; fixing one does not automatically fix the other.

### `social.waldinger2010`

В одном из самых длительных лонгитюдных исследований развития взрослых качество отношений — а не их количество — предсказывало ежедневное настроение и субъективное здоровье спустя десятилетия. Надёжная привязанность смягчала влияние физической боли на настроение.

- **Источник:** Waldinger & Schulz (2010). What's love got to do with it? Social functioning, perceived health, and daily happiness in married octogenarians. Psychology and Aging 25(2)
- **DOI:** [10.1037/a0019087](https://doi.org/10.1037/a0019087)
- **Дизайн исследования:** Longitudinal cohort (Harvard Study of Adult Development), 8-day daily diaries
- **Сила доказательства:** средняя
- **Статус:** **НЕ проверено**
- **Формулировка на английском:** In one of the longest-running longitudinal studies of adult development, relationship quality — not relationship count — predicted daily mood and perceived health decades later. Secure attachment buffered the effect of physical pain on mood.

### `social.epley2014`

Люди, которым поручили поговорить с незнакомцем в дороге, оценивали поездку как более приятную, чем те, кому велели ехать молча, — хотя заранее участники предсказывали обратное. Мы систематически недооцениваем, насколько хорошо будет от контакта, поэтому его и избегаем.

- **Источник:** Epley & Schroeder (2014). Mistakenly seeking solitude. Journal of Experimental Psychology: General 143(5)
- **DOI:** [10.1037/a0037323](https://doi.org/10.1037/a0037323)
- **Дизайн исследования:** Field and laboratory experiments (commuters, waiting rooms)
- **Сила доказательства:** средняя
- **Статус:** **НЕ проверено**
- **Формулировка на английском:** People instructed to talk to a stranger on a commute reported a more positive experience than those told to sit in solitude — yet participants predicted the opposite beforehand. We systematically underestimate how good connection will feel, which is why we skip it.

## Психика

Файл: `src/myway/science/corpus/mental.yaml` · записей: 5


### `mental.killingsworth2010`

Мысли участников блуждали примерно в 47% зафиксированных моментов, и блуждание ума предсказывало снижение настроения в следующий момент — даже когда содержание мыслей было приятным. Для настроения важнее было не то, чем человек занят, а то, присутствовал ли он в этом на самом деле.

- **Источник:** Killingsworth & Gilbert (2010). A wandering mind is an unhappy mind. Science 330(6006)
- **DOI:** [10.1126/science.1192439](https://doi.org/10.1126/science.1192439)
- **Дизайн исследования:** Experience sampling, 2,250 adults, ~250,000 samples
- **Сила доказательства:** средняя
- **Статус:** **НЕ проверено**
- **Формулировка на английском:** People's minds wandered in about 47% of sampled moments, and mind-wandering predicted lower happiness in the next moment — including when the content was pleasant. What you are doing mattered less to mood than whether you were actually there for it.

### `mental.cappuccio2010`

Короткая продолжительность сна была связана с примерно на 12% более высоким риском смерти за период наблюдения по объединённым когортам. Сон — не предпочтение в образе жизни, которое можно оптимизировать; это основа, на которой работает всё остальное.

- **Источник:** Cappuccio, D'Elia, Strazzullo & Miller (2010). Sleep duration and all-cause mortality: A systematic review and meta-analysis. Sleep 33(5)
- **DOI:** [10.1093/sleep/33.5.585](https://doi.org/10.1093/sleep/33.5.585)
- **Дизайн исследования:** Meta-analysis of 16 prospective cohort studies (n > 1.3 million)
- **Сила доказательства:** сильная
- **Статус:** **НЕ проверено**
- **Формулировка на английском:** Short sleep duration was associated with a roughly 12% higher risk of death over follow-up across pooled cohorts. Sleep is not a lifestyle preference that can be optimised away; it is the substrate every other intervention runs on.

### `mental.goyal2014`

Программы медитации осознанности давали небольшие, но устойчивые улучшения при тревоге, депрессии и боли (размер эффекта около 0,3 к восьмой неделе). Эффект реальный и измеримый, но значительно меньше, чем обещает реклама, — стоит делать, но это не лекарство.

- **Источник:** Goyal, Singh, Sibinga et al. (2014). Meditation programs for psychological stress and well-being: A systematic review and meta-analysis. JAMA Internal Medicine 174(3)
- **DOI:** [10.1001/jamainternmed.2013.13018](https://doi.org/10.1001/jamainternmed.2013.13018)
- **Дизайн исследования:** Meta-analysis of 47 randomised trials (n ≈ 3,500)
- **Сила доказательства:** сильная
- **Статус:** **НЕ проверено**
- **Формулировка на английском:** Mindfulness meditation programmes produced small but reliable improvements in anxiety, depression, and pain (effect sizes around 0.3 at eight weeks). Real, measurable, and far smaller than the marketing implies — worth doing, not a cure.

### `mental.hofmann2012`

По данным сотен метаанализов, когнитивно-поведенческая терапия имеет самую сильную доказательную базу среди психологических методов лечения, с наиболее ясными эффектами при тревожных расстройствах, соматических проблемах и депрессии. У некоторых проблем есть лечение, и структурированный план самопомощи им не является.

- **Источник:** Hofmann, Asnaani, Vonk, Sawyer & Fang (2012). The efficacy of cognitive behavioral therapy: A review of meta-analyses. Cognitive Therapy and Research 36(5)
- **DOI:** [10.1007/s10608-012-9476-1](https://doi.org/10.1007/s10608-012-9476-1)
- **Дизайн исследования:** Review of 269 meta-analytic studies
- **Сила доказательства:** сильная
- **Статус:** **НЕ проверено**
- **Формулировка на английском:** Across hundreds of meta-analyses, cognitive behavioural therapy showed the strongest evidence base of any psychological treatment, with the clearest effects for anxiety disorders, somatic problems, and depression. Some problems have a treatment; a structured self-help plan is not it.

### `mental.nolenhoeksema2008`

Рефлексивное «прокручивание» — повторяющееся обдумывание проблемы без перехода к действию — предсказывает начало и затяжной характер депрессивных эпизодов и устойчиво ухудшает решение проблем, а не улучшает его. Думать об этом больше — не то же самое, что работать над этим.

- **Источник:** Nolen-Hoeksema, Wisco & Lyubomirsky (2008). Rethinking rumination. Perspectives on Psychological Science 3(5)
- **DOI:** [10.1111/j.1745-6924.2008.00088.x](https://doi.org/10.1111/j.1745-6924.2008.00088.x)
- **Дизайн исследования:** Review of longitudinal and experimental evidence
- **Сила доказательства:** средняя
- **Статус:** **НЕ проверено**
- **Формулировка на английском:** Rumination — repetitively going over a problem without moving toward action — predicts the onset and persistence of depressive episodes, and reliably worsens problem-solving rather than improving it. Thinking about it more is not the same as working on it.

## Тело

Файл: `src/myway/science/corpus/physical.yaml` · записей: 4


### `physical.ekelund2019`

Любая физическая активность была связана со существенно более низким риском смертности, причём наибольший прирост — на нижнем конце: переход от «почти ничего» к «немного» давал гораздо больше, чем переход от «много» к «ещё больше». Значение имел общий объём движения, интенсивность не была обязательной.

- **Источник:** Ekelund, Tarp, Steene-Johannessen et al. (2019). Dose-response associations between accelerometry measured physical activity and sedentary time and all cause mortality. BMJ 366
- **DOI:** [10.1136/bmj.l4570](https://doi.org/10.1136/bmj.l4570)
- **Дизайн исследования:** Harmonised meta-analysis of 8 prospective cohorts (n ≈ 36,000), device-measured
- **Сила доказательства:** сильная
- **Статус:** **НЕ проверено**
- **Формулировка на английском:** Any amount of physical activity was associated with substantially lower mortality risk, with the steepest gains at the low end — moving from almost nothing to a little mattered far more than moving from a lot to more. Total movement counted; intensity was not required.

### `physical.wen2011`

Пятнадцать минут умеренной нагрузки в день были связаны со снижением общей смертности на 14% и примерно тремя дополнительными годами ожидаемой продолжительности жизни по сравнению с малоподвижностью. Порог действительно низкий — и это убирает отговорку «у меня нет часа».

- **Источник:** Wen, Wai, Tsai et al. (2011). Minimum amount of physical activity for reduced mortality and extended life expectancy: A prospective cohort study. The Lancet 378(9798)
- **DOI:** [10.1016/S0140-6736(11)60749-6](https://doi.org/10.1016/S0140-6736(11)60749-6)
- **Дизайн исследования:** Prospective cohort (n ≈ 416,000, Taiwan), mean 8 years follow-up
- **Сила доказательства:** средняя
- **Статус:** **НЕ проверено**
- **Формулировка на английском:** Fifteen minutes a day of moderate exercise was associated with a 14% reduction in all-cause mortality and about three years of additional life expectancy compared with being inactive. The floor is genuinely low — which removes the excuse of not having an hour.

### `physical.schuch2018`

Более высокая физическая активность предсказывала меньшую вероятность развития депрессии во всех когортах и возрастных группах, независимо от исходного психического состояния. Это один из немногих случаев, когда работа с физической сферой напрямую улучшает психическую.

- **Источник:** Schuch, Vancampfort, Firth et al. (2018). Physical activity and incident depression: A meta-analysis of prospective cohort studies. American Journal of Psychiatry 175(7)
- **DOI:** [10.1176/appi.ajp.2018.17111194](https://doi.org/10.1176/appi.ajp.2018.17111194)
- **Дизайн исследования:** Meta-analysis of 49 prospective cohorts (n ≈ 267,000)
- **Сила доказательства:** сильная
- **Статус:** **НЕ проверено**
- **Формулировка на английском:** Higher physical activity predicted lower odds of developing depression across cohorts and age groups, independent of baseline mental health. This is one of the few places where fixing the physical domain directly buys improvement in the mental one.

### `physical.momma2022`

Силовые нагрузки объёмом примерно 30–60 минут в неделю были связаны с наименьшим риском общей смертности, причём сверх этого дополнительной пользы не наблюдалось — возможно, даже немного меньше. Похоже, что всё необходимое — это две короткие сессии в неделю.

- **Источник:** Momma, Kawakami, Honda & Sawada (2022). Muscle-strengthening activities are associated with lower risk and mortality in major non-communicable diseases. British Journal of Sports Medicine 56(13)
- **DOI:** [10.1136/bjsports-2021-105061](https://doi.org/10.1136/bjsports-2021-105061)
- **Дизайн исследования:** Systematic review and meta-analysis of 16 prospective cohorts
- **Сила доказательства:** средняя
- **Статус:** **НЕ проверено**
- **Формулировка на английском:** Muscle-strengthening activity of roughly 30–60 minutes per week was associated with the lowest risk of all-cause mortality, with no additional benefit — and possibly slightly less — beyond that. Two short sessions a week appears to be the whole ask.

## Деньги

Файл: `src/myway/science/corpus/financial.yaml` · записей: 5


### `financial.killingsworth2023`

У большинства людей эмоциональное благополучие продолжает расти вместе с доходом далеко за пределами уровня, который раньше считали потолком. Но у несчастливого меньшинства — тех, чьи источники страдания деньгами не решаются — рост выходит на плато при умеренном доходе. Больше денег помогает, если настоящая проблема не в чём-то другом.

- **Источник:** Killingsworth, Kahneman & Mellers (2023). Income and emotional well-being: A conflict resolved. PNAS 120(10)
- **DOI:** [10.1073/pnas.2208661120](https://doi.org/10.1073/pnas.2208661120)
- **Дизайн исследования:** Adversarial collaboration reanalysing experience-sampling data (n ≈ 33,000)
- **Сила доказательства:** сильная
- **Статус:** **НЕ проверено**
- **Формулировка на английском:** For most people, emotional well-being keeps rising with income well past the levels once thought to be a ceiling. But for an unhappy minority — those with sources of misery money cannot touch — it plateaus around a moderate income. More money helps unless something else is the actual problem.

### `financial.kahneman2010`

Доход был связан с тем, как люди оценивали свою жизнь в целом, гораздо теснее, чем с тем, что они на самом деле чувствовали изо дня в день. Это две разные величины, и деньги сдвигают их по-разному: жизнь, которая хорошо выглядит на бумаге, может ощущаться плохо час за часом.

- **Источник:** Kahneman & Deaton (2010). High income improves evaluation of life but not emotional well-being. PNAS 107(38)
- **DOI:** [10.1073/pnas.1011492107](https://doi.org/10.1073/pnas.1011492107)
- **Дизайн исследования:** Analysis of 450,000 survey responses (Gallup-Healthways)
- **Сила доказательства:** сильная
- **Статус:** **НЕ проверено**
- **Формулировка на английском:** Income tracked how people rated their life as a whole far more closely than how they actually felt day to day. These are two different measures, and money moves them by different amounts — a life that scores well on paper can still feel bad hour to hour.

### `financial.netemeyer2018`

Субъективное финансовое благополучие распадается на две отдельные части: текущий стресс от управления деньгами и ожидаемая будущая защищённость. Обе предсказывали общее благополучие так же сильно, как физическое здоровье, — и стресс из-за денег во многом не зависел от их количества.

- **Источник:** Netemeyer, Warmath, Fernandes & Lynch (2018). How am I doing? Perceived financial well-being, its potential antecedents, and its relation to overall well-being. Journal of Consumer Research 45(1)
- **DOI:** [10.1093/jcr/ucx109](https://doi.org/10.1093/jcr/ucx109)
- **Дизайн исследования:** Multi-study survey research with national samples
- **Сила доказательства:** средняя
- **Статус:** **НЕ проверено**
- **Формулировка на английском:** Perceived financial well-being splits into two distinct parts: current money-management stress and expected future security. Both predicted overall well-being as strongly as physical health did — and stress about money was largely separate from how much of it there was.

### `financial.dunn2008`

То, как распределялись деньги, предсказывало счастье лучше, чем их количество: участники, случайно распределённые тратить небольшую сумму на другого человека, заканчивали день счастливее тех, кто тратил её на себя. Рычаг — распределение, а не сумма.

- **Источник:** Dunn, Aknin & Norton (2008). Spending money on others promotes happiness. Science 319(5870)
- **DOI:** [10.1126/science.1150952](https://doi.org/10.1126/science.1150952)
- **Дизайн исследования:** National survey, longitudinal windfall study, and a field experiment
- **Сила доказательства:** средняя
- **Статус:** **НЕ проверено**
- **Формулировка на английском:** How money was allocated predicted happiness better than how much there was: participants randomly assigned to spend a small windfall on someone else ended the day happier than those who spent it on themselves. The lever is allocation, not amount.

### `financial.lusardi2011`

Значительная доля домохозяйств — включая семьи со средним доходом — сообщила, что не сможет найти умеренную сумму на непредвиденные расходы в течение месяца. Уязвимость определяется наличием запаса, а не зарплатой, поэтому небольшой денежный резерв быстро меняет само ощущение денег.

- **Источник:** Lusardi, Schneider & Tufano (2011). Financially fragile households: Evidence and implications. Brookings Papers on Economic Activity, Spring 2011
- **DOI:** [10.1353/eca.2011.0002](https://doi.org/10.1353/eca.2011.0002)
- **Дизайн исследования:** Cross-national survey of coping capacity
- **Сила доказательства:** средняя
- **Статус:** **НЕ проверено**
- **Формулировка на английском:** A large share of households — including middle-income ones — reported they could not come up with a modest emergency sum within a month. Fragility is about buffer, not salary, which is why a small cash reserve changes the felt experience of money quickly.

## Изменение поведения (общее для всех сфер)

Файл: `src/myway/science/corpus/cross_cutting.yaml` · записей: 6


### `change.dalton2012`

Конкретный план помогал, когда человек преследовал одну цель, но преимущество исчезало — а приверженность падала — когда планировалось сразу шесть целей. Планирование многих вещей одновременно делает трудность очевидной, а всё дело — невыполнимым.

- **Источник:** Dalton & Spiller (2012). Too much of a good thing: The benefits of implementation intentions depend on the number of goals. Journal of Consumer Research 39(3)
- **DOI:** [10.1086/663212](https://doi.org/10.1086/663212)
- **Дизайн исследования:** Series of experiments varying goal count
- **Сила доказательства:** средняя
- **Статус:** **НЕ проверено**
- **Формулировка на английском:** Making a concrete plan helped when people pursued a single goal, but the benefit disappeared — and commitment dropped — once they planned for six goals at once. Planning many things simultaneously makes the difficulty vivid and the whole effort feel infeasible.

### `change.gollwitzer2006`

Заранее указанное когда, где и как вы будете действовать («если ситуация X, то я сделаю Y») давало средний-крупный эффект на достижение целей в 94 исследованиях — сверх простого намерения действовать. Выигрыш даёт конкретность, а не мотивация.

- **Источник:** Gollwitzer & Sheeran (2006). Implementation intentions and goal achievement: A meta-analysis of effects and processes. Advances in Experimental Social Psychology 38
- **DOI:** [10.1016/S0065-2601(06)38002-1](https://doi.org/10.1016/S0065-2601(06)38002-1)
- **Дизайн исследования:** Meta-analysis of 94 independent tests
- **Сила доказательства:** сильная
- **Статус:** **НЕ проверено**
- **Формулировка на английском:** Specifying in advance when, where, and how you will act ("if situation X, then I will do Y") had a medium-to-large effect on goal attainment across 94 studies, over and above simply intending to act. The gain comes from the specificity, not the motivation.

### `change.harkin2016`

Побуждение отслеживать собственный прогресс устойчиво повышало достижение целей, причём эффект был сильнее, когда прогресс сообщался публично или физически фиксировался. Отслеживание — не бюрократия, а часть самого вмешательства.

- **Источник:** Harkin, Webb, Chang et al. (2016). Does monitoring goal progress promote goal attainment? A meta-analysis of the experimental evidence. Psychological Bulletin 142(2)
- **DOI:** [10.1037/bul0000025](https://doi.org/10.1037/bul0000025)
- **Дизайн исследования:** Meta-analysis of 138 experimental studies (n ≈ 19,000)
- **Сила доказательства:** сильная
- **Статус:** **НЕ проверено**
- **Формулировка на английском:** Prompting people to monitor their progress reliably increased goal attainment, and the effect was larger when progress was reported publicly or physically recorded. Tracking is not admin overhead; it is part of the intervention.

### `change.lally2010`

Время до автоматизма составило в среднем (медиана) около 66 дней и колебалось примерно от 18 до более 250 в зависимости от поведения и человека. Пропуск одного дня заметно не нарушал траекторию. Цифра «21 день» этими данными не подтверждается.

- **Источник:** Lally, van Jaarsveld, Potts & Wardle (2010). How are habits formed: Modelling habit formation in the real world. European Journal of Social Psychology 40(6)
- **DOI:** [10.1002/ejsp.674](https://doi.org/10.1002/ejsp.674)
- **Дизайн исследования:** 84 participants tracked daily for 12 weeks
- **Сила доказательства:** средняя
- **Статус:** **НЕ проверено**
- **Формулировка на английском:** Time to reach automaticity had a median of about 66 days and ranged from roughly 18 to over 250 depending on the behaviour and the person. Missing a single day did not meaningfully damage the trajectory. The "21 days" figure has no basis in this data.

### `change.oettingen2012`

Простое воображение положительного результата снижало усилия и результативность; сопоставление желаемого исхода с конкретным препятствием на пути повышало и то, и другое. Назвать, что помешает, эффективнее, чем представлять, как всё получится.

- **Источник:** Oettingen (2012). Future thought and behaviour change. European Review of Social Psychology 23(1)
- **DOI:** [10.1080/10463283.2011.643698](https://doi.org/10.1080/10463283.2011.643698)
- **Дизайн исследования:** Review of experimental work on mental contrasting
- **Сила доказательства:** средняя
- **Статус:** **НЕ проверено**
- **Формулировка на английском:** Simply imagining a positive outcome reduced effort and attainment; contrasting the desired outcome against the specific obstacle in the way increased both. Naming what will get in the way beats picturing it going well.

### `change.milkman2021`

Когда 54 разработанных экспертами вмешательства по изменению поведения проверили друг против друга в большом масштабе, большинство дали небольшой эффект, а многие — никакого. Работавшие вмешательства работали за счёт снижения трения и напоминаний, а не за счёт вдохновения.

- **Источник:** Milkman, Gromet, Ho et al. (2021). Megastudies improve the impact of applied behavioural science. Nature 600
- **DOI:** [10.1038/s41586-021-04128-4](https://doi.org/10.1038/s41586-021-04128-4)
- **Дизайн исследования:** Megastudy: 54 interventions tested on ~61,000 participants
- **Сила доказательства:** сильная
- **Статус:** **НЕ проверено**
- **Формулировка на английском:** When 54 expert-designed behaviour-change interventions were tested head to head at scale, most produced small effects and many produced none. Interventions that worked did so by reducing friction and adding reminders — not by inspiring people.
