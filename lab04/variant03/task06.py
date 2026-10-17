"""Лабораторная 4, вариант 3. Анализ учебных показаний электросчётчика."""

from argparse import ArgumentParser
from collections.abc import Callable
from datetime import date
from functools import partial, reduce
from itertools import accumulate, groupby, pairwise
from operator import add, attrgetter
from typing import NamedTuple


class Reading(NamedTuple):
    """Неизменяемая запись накопленного показания одного счётчика, кВт·ч."""

    taken_on: date
    meter: str
    kwh: int


class Usage(NamedTuple):
    """Расход между двумя соседними показаниями одного счётчика."""

    start: date
    end: date
    month: str
    kwh: int


class MonthUsage(NamedTuple):
    """Суммарное потребление за полностью покрытый календарный месяц."""

    month: str
    kwh: int


def create_readings() -> tuple[Reading, ...]:
    """Создаёт 25 явно заданных учебных записей с января по июль 2026 года."""
    return (
        Reading(date(2026, 1, 1), "ЭЛ-001", 10_000),
        Reading(date(2026, 1, 10), "ЭЛ-001", 10_100),
        Reading(date(2026, 1, 20), "ЭЛ-001", 10_220),
        Reading(date(2026, 1, 25), "ЭЛ-001", 10_290),
        Reading(date(2026, 2, 1), "ЭЛ-001", 10_380),
        Reading(date(2026, 2, 10), "ЭЛ-001", 10_490),
        Reading(date(2026, 2, 20), "ЭЛ-001", 10_590),
        Reading(date(2026, 2, 25), "ЭЛ-001", 10_670),
        Reading(date(2026, 3, 1), "ЭЛ-001", 10_760),
        Reading(date(2026, 3, 10), "ЭЛ-001", 10_830),
        Reading(date(2026, 3, 20), "ЭЛ-001", 10_910),
        Reading(date(2026, 3, 25), "ЭЛ-001", 10_960),
        Reading(date(2026, 4, 1), "ЭЛ-001", 11_020),
        Reading(date(2026, 4, 10), "ЭЛ-001", 11_080),
        Reading(date(2026, 4, 20), "ЭЛ-001", 11_150),
        Reading(date(2026, 4, 25), "ЭЛ-001", 11_190),
        Reading(date(2026, 5, 1), "ЭЛ-001", 11_240),
        Reading(date(2026, 5, 10), "ЭЛ-001", 11_290),
        Reading(date(2026, 5, 20), "ЭЛ-001", 11_350),
        Reading(date(2026, 5, 25), "ЭЛ-001", 11_390),
        Reading(date(2026, 6, 1), "ЭЛ-001", 11_440),
        Reading(date(2026, 6, 10), "ЭЛ-001", 11_500),
        Reading(date(2026, 6, 20), "ЭЛ-001", 11_580),
        Reading(date(2026, 6, 25), "ЭЛ-001", 11_630),
        Reading(date(2026, 7, 1), "ЭЛ-001", 11_700),
    )


def difference(pair: tuple[Reading, Reading]) -> Usage:
    """Вычисляет расход, проверяя время, счётчик и отсутствие его сброса."""
    earlier, later = pair
    if earlier.meter != later.meter:
        raise ValueError("Нельзя вычитать показания разных счётчиков")
    if later.taken_on <= earlier.taken_on:
        raise ValueError("Даты должны строго возрастать")
    if later.kwh < earlier.kwh:
        raise ValueError("Уменьшение показаний требует отдельного учёта сброса")
    month = earlier.taken_on.strftime("%Y-%m")
    next_month = date(
        earlier.taken_on.year + earlier.taken_on.month // 12,
        earlier.taken_on.month % 12 + 1,
        1,
    )
    if later.taken_on > next_month:
        raise ValueError("Интервал пересёк границу месяца без показания на ней")
    return Usage(earlier.taken_on, later.taken_on, month, later.kwh - earlier.kwh)


def intervals(readings: tuple[Reading, ...]) -> tuple[Usage, ...]:
    """Возвращает разности соседних записей, не изменяя исходный кортеж."""
    return tuple(map(difference, pairwise(readings)))


def monthly_usage(readings: tuple[Reading, ...]) -> tuple[MonthUsage, ...]:
    """Считает расход полных месяцев, если крайние даты лежат на границах."""
    if len(readings) < 2:
        return ()
    if readings[0].taken_on.day != 1 or readings[-1].taken_on.day != 1:
        raise ValueError("Нужны показания на начале и конце полных месяцев")
    by_month = groupby(intervals(readings), key=attrgetter("month"))
    return tuple(
        map(
            lambda group: MonthUsage(
                group[0], reduce(add, map(attrgetter("kwh"), group[1]), 0)
            ),
            by_month,
        )
    )


def above_limit(limit: int, month: MonthUsage) -> bool:
    """Определяет, превысил ли месячный расход заданный порог, кВт·ч."""
    return month.kwh > limit


def high_usage(months: tuple[MonthUsage, ...], limit: int) -> tuple[MonthUsage, ...]:
    """Отбирает месяцы по предикату с порогом, закреплённым через partial."""
    return tuple(filter(partial(above_limit, limit), months))


def peak_months(months: tuple[MonthUsage, ...]) -> tuple[MonthUsage, ...]:
    """Возвращает все месяцы с максимальным потреблением, включая равные."""
    if not months:
        return ()
    peak = reduce(lambda current, month: max(current, month.kwh), months, 0)
    return tuple(filter(lambda month: month.kwh == peak, months))


def cumulative_usage(months: tuple[MonthUsage, ...]) -> tuple[MonthUsage, ...]:
    """Вычисляет накопленное потребление от начала рассматриваемого периода."""
    return tuple(
        map(
            lambda pair: MonthUsage(*pair),
            zip(
                map(attrgetter("month"), months),
                accumulate(map(attrgetter("kwh"), months), add),
            ),
        )
    )


def run_checks() -> None:
    """Проверяет расчёты, граничные случаи и причины отклонения неверных данных."""
    readings = create_readings()
    snapshot = tuple(map(tuple, readings))
    usage = intervals(readings)
    months = monthly_usage(readings)
    assert len(readings) == 25
    assert len(usage) == 24
    assert tuple(map(attrgetter("kwh"), usage)) == (
        100,
        120,
        70,
        90,
        110,
        100,
        80,
        90,
        70,
        80,
        50,
        60,
        60,
        70,
        40,
        50,
        50,
        60,
        40,
        50,
        60,
        80,
        50,
        70,
    )
    assert tuple(map(attrgetter("kwh"), months)) == (380, 380, 260, 220, 200, 260)
    assert tuple(map(attrgetter("month"), peak_months(months))) == (
        "2026-01",
        "2026-02",
    )
    assert high_usage(months, 300) == months[:2]
    assert high_usage(months, 380) == ()
    assert tuple(map(attrgetter("kwh"), cumulative_usage(months))) == (
        380,
        760,
        1020,
        1240,
        1440,
        1700,
    )
    assert reduce(add, map(attrgetter("kwh"), usage), 0) == 1700
    assert reduce(add, map(attrgetter("kwh"), months), 0) == (
        readings[-1].kwh - readings[0].kwh
    )
    assert cumulative_usage(months)[-1].kwh == 1700
    assert tuple(map(tuple, readings)) == snapshot
    assert intervals(()) == ()
    assert intervals(readings[:1]) == ()
    assert monthly_usage(()) == ()
    assert peak_months(()) == ()
    assert cumulative_usage(()) == ()
    assert (
        difference((readings[0], readings[0]._replace(taken_on=date(2026, 1, 2)))).kwh
        == 0
    )
    assert difference((readings[3], readings[4])).month == "2026-01"
    assert (
        difference(
            (
                Reading(date(2026, 12, 25), "ЭЛ-001", 100),
                Reading(date(2027, 1, 1), "ЭЛ-001", 120),
            )
        ).month
        == "2026-12"
    )
    check_invalid(lambda: difference((readings[1], readings[0])))
    check_invalid(lambda: difference((readings[0], readings[0])))
    check_invalid(lambda: difference((readings[0], readings[1]._replace(kwh=99))))
    check_invalid(
        lambda: difference((readings[0], readings[1]._replace(meter="ЭЛ-002")))
    )
    check_invalid(lambda: difference((readings[0], readings[5])))
    check_invalid(lambda: monthly_usage(readings[1:]))
    print("Проверки: 26/26 успешно, включая 6 ожидаемых ValueError.")


def check_invalid(call: Callable[[], object]) -> None:
    """Проверяет отклонение неоднозначного или некорректного набора данных."""
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Ожидалось исключение ValueError")


def main() -> None:
    """Печатает исходные записи и все результаты для отчёта."""
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--part", choices=("all", "data", "diffs", "months", "checks"), default="all"
    )
    part = parser.parse_args().part
    readings = create_readings()
    months = monthly_usage(readings)
    print("Лабораторная 4. Задание 6. Вариант 3. Электроэнергия.")
    print("Данные учебные, счётчик ЭЛ-001. Единицы: кВт·ч.")
    print("25 показаний. Снимок на первое число относится к началу суток.")
    if part in ("all", "data"):
        print("ИСХОДНЫЕ ПОКАЗАНИЯ")
        print(
            "\n".join(
                map(
                    lambda record: (
                        f"{record.taken_on} | {record.meter} | {record.kwh:5d}"
                    ),
                    readings,
                )
            )
        )
    if part in ("all", "diffs"):
        print("РАЗНОСТИ СОСЕДНИХ ПОКАЗАНИЙ")
        print(
            "\n".join(
                map(
                    lambda item: (
                        f"{item.start} .. {item.end} | {item.kwh:3d} | {item.month}"
                    ),
                    intervals(readings),
                )
            )
        )
    if part in ("all", "months"):
        print("РАСХОД ПО ПОЛНЫМ МЕСЯЦАМ")
        print("\n".join(map(lambda item: f"{item.month}: {item.kwh}", months)))
        print("Пиковые месяцы:", tuple(map(tuple, peak_months(months))))
        print("Месяцы с расходом > 300:", tuple(map(tuple, high_usage(months, 300))))
        print("Накопительный расход:", tuple(map(tuple, cumulative_usage(months))))
        print("Инвариант: 380 + 380 + 260 + 220 + 200 + 260 = 11700 - 10000 = 1700.")
        print(
            "Исходные записи неизменны; 01.07 закрывает июнь, расход июля неизвестен."
        )
    if part in ("all", "checks"):
        run_checks()


if __name__ == "__main__":
    main()
