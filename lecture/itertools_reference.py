"""СРС 1. Собственные проверяемые примеры всех 20 функций itertools.

Запуск: python itertools_reference.py count
Каждая функция выбирается по своему имени. Требуется Python 3.12+.
"""

from __future__ import annotations

import argparse
import itertools as it
from collections.abc import Callable
from operator import mul


def demo_count() -> None:
    """Получить первые четыре номера с шагом 25."""
    result = list(it.islice(it.count(100, 25), 4))
    print("Номера заказов:", result)
    assert result == [100, 125, 150, 175]
    assert list(it.islice(it.count(), 0)) == []


def demo_cycle() -> None:
    """Повторить чередование смен и явно ограничить длину."""
    result = list(it.islice(it.cycle(["утро", "вечер"]), 5))
    print("Пять смен:", result)
    assert result == ["утро", "вечер", "утро", "вечер", "утро"]
    assert list(it.cycle([])) == []


def demo_repeat() -> None:
    """Повторить неизменяемый объект заданное число раз."""
    result = list(it.repeat("проверить", 3))
    print("Три напоминания:", result)
    assert result == ["проверить"] * 3
    assert list(it.repeat("x", 0)) == []
    assert list(it.islice(it.repeat(7), 2)) == [7, 7]


def demo_accumulate() -> None:
    """Посчитать остаток средств после поступления и списаний."""
    result = list(it.accumulate([500, -200, -100], initial=1000))
    print("Остатки, включая начальный:", result)
    assert result == [1000, 1500, 1300, 1200]
    assert list(it.accumulate([])) == []
    assert list(it.accumulate([], initial=1000)) == [1000]


def demo_chain() -> None:
    """Объединить элементы вложенных списков по одному уровню."""
    result = list(it.chain.from_iterable([["A", "B"], [], ["C"]]))
    print("Общий список заявок:", result)
    assert result == ["A", "B", "C"]
    assert list(it.chain([], [])) == []


def demo_compress() -> None:
    """Отобрать согласованные заявки по параллельной маске."""
    result = list(it.compress(["A1", "A2", "A3", "A4"], [1, 0, True, False]))
    print("Согласованные заявки:", result)
    assert result == ["A1", "A3"]
    assert list(it.compress(["A", "B"], [1])) == ["A"]
    assert list(it.compress([], [True])) == []


def demo_dropwhile() -> None:
    """Пропустить начальные отрицательные измерения."""
    result = list(it.dropwhile(lambda x: x < 0, [-3, -1, 0, -2, 4]))
    print("После первого неотрицательного:", result)
    assert result == [0, -2, 4]
    assert list(it.dropwhile(lambda x: x < 0, [-3, -1])) == []
    assert list(it.dropwhile(bool, [])) == []


def demo_takewhile() -> None:
    """Взять непрерывную начальную серию допустимых температур."""
    result = list(it.takewhile(lambda x: x < 80, [70, 75, 90, 72]))
    print("До первого перегрева:", result)
    assert result == [70, 75]
    assert list(it.takewhile(lambda x: x < 80, [90, 70])) == []
    assert list(it.takewhile(bool, [])) == []


def demo_filterfalse() -> None:
    """Оставить все нечётные числа независимо от позиции."""
    result = list(it.filterfalse(lambda x: x % 2 == 0, range(1, 8)))
    print("Нечётные числа:", result)
    assert result == [1, 3, 5, 7]
    assert list(it.filterfalse(None, [0, 1, "", "x", None])) == [0, "", None]
    assert list(it.filterfalse(bool, [])) == []


def demo_groupby() -> None:
    """Посчитать соседние серии статусов и затем общие количества."""
    statuses = ["ok", "ok", "fail", "ok"]
    runs = [(status, len(list(group))) for status, group in it.groupby(statuses)]
    totals = [
        (status, len(list(group))) for status, group in it.groupby(sorted(statuses))
    ]
    print("Соседние серии:", runs)
    print("После сортировки:", totals)
    assert runs == [("ok", 2), ("fail", 1), ("ok", 1)]
    assert totals == [("fail", 1), ("ok", 3)]
    assert list(it.groupby([])) == []


def demo_islice() -> None:
    """Взять элементы с индексами 1, 3 и 5 без создания входного списка."""
    result = list(it.islice(it.count(10), 1, 7, 2))
    print("Выбранные номера:", result)
    assert result == [11, 13, 15]
    assert list(it.islice([], 5)) == []


def demo_pairwise() -> None:
    """Найти изменения показаний между соседними измерениями."""
    readings = [100, 104, 109, 107]
    pairs = list(it.pairwise(readings))
    changes = [right - left for left, right in pairs]
    print("Соседние пары:", pairs)
    print("Изменения:", changes)
    assert pairs == [(100, 104), (104, 109), (109, 107)]
    assert changes == [4, 5, -2]
    assert list(it.pairwise([100])) == [] and list(it.pairwise([])) == []


def demo_starmap() -> None:
    """Вычислить площади прямоугольников по парам сторон."""
    result = list(it.starmap(mul, [(3, 4), (2, 5), (0, 7)]))
    print("Площади:", result)
    assert result == [12, 10, 0]
    assert list(it.starmap(mul, [])) == []


def demo_tee() -> None:
    """Разделить один источник для двух независимых вычислений."""
    first, second = it.tee(iter([2, 4, 6]), 2)
    total = sum(first)
    squares = list(map(lambda x: x * x, second))
    print("Сумма:", total)
    print("Квадраты во втором проходе:", squares)
    assert total == 12 and squares == [4, 16, 36]
    assert list(first) == [] and list(second) == []
    assert it.tee([], 0) == ()


def demo_zip_longest() -> None:
    """Сопоставить два списка, сохранив непарную запись."""
    result = list(
        it.zip_longest(
            ["Ира", "Оля", "Вика"],
            [95, 88],
            fillvalue=None,
        )
    )
    print("Оценки:", result)
    assert result == [("Ира", 95), ("Оля", 88), ("Вика", None)]
    assert list(it.zip_longest([], [])) == []


def demo_batched() -> None:
    """Разделить пять заявок на пакеты по две."""
    result = list(it.batched(["A1", "A2", "A3", "A4", "A5"], 2))
    print("Пакеты заявок:", result)
    assert result == [("A1", "A2"), ("A3", "A4"), ("A5",)]
    assert list(it.batched([], 2)) == []
    try:
        list(it.batched([1], 0))
    except ValueError:
        print("Размер пакета 0: ожидаемый ValueError.")
    else:
        raise AssertionError("Ожидался ValueError")


def demo_product() -> None:
    """Перечислить варианты размера и цвета товара."""
    result = list(it.product(["S", "M"], ["белый", "синий"]))
    print("Варианты товара:", result)
    assert result == [("S", "белый"), ("S", "синий"), ("M", "белый"), ("M", "синий")]
    assert list(it.product([], [1])) == []
    assert list(it.product()) == [()]


def demo_permutations() -> None:
    """Выбрать капитана и помощника из трёх людей, учитывая порядок."""
    result = list(it.permutations(["Аня", "Вика", "Ира"], 2))
    print("Капитан и помощник:", result)
    assert result == [
        ("Аня", "Вика"),
        ("Аня", "Ира"),
        ("Вика", "Аня"),
        ("Вика", "Ира"),
        ("Ира", "Аня"),
        ("Ира", "Вика"),
    ]
    assert len(result) == 6
    assert list(it.permutations([1], 2)) == []
    assert list(it.permutations([], 0)) == [()]


def demo_combinations() -> None:
    """Выбрать двух дежурных без учёта порядка."""
    result = list(it.combinations(["Аня", "Вика", "Ира"], 2))
    print("Пары дежурных:", result)
    assert result == [("Аня", "Вика"), ("Аня", "Ира"), ("Вика", "Ира")]
    assert list(it.combinations([1], 2)) == []
    assert list(it.combinations([], 0)) == [()]


def demo_combinations_with_replacement() -> None:
    """Выбрать две краски, разрешая повтор одного цвета."""
    result = list(it.combinations_with_replacement(["синий", "жёлтый"], 2))
    print("Наборы красок:", result)
    assert result == [("синий", "синий"), ("синий", "жёлтый"), ("жёлтый", "жёлтый")]
    assert list(it.combinations_with_replacement([], 2)) == []
    assert list(it.combinations_with_replacement([], 0)) == [()]


def main() -> None:
    """Выполнить выбранный собственный пример и его проверки."""
    demos: dict[str, Callable[[], None]] = {
        "count": demo_count,
        "cycle": demo_cycle,
        "repeat": demo_repeat,
        "accumulate": demo_accumulate,
        "chain": demo_chain,
        "compress": demo_compress,
        "dropwhile": demo_dropwhile,
        "takewhile": demo_takewhile,
        "filterfalse": demo_filterfalse,
        "groupby": demo_groupby,
        "islice": demo_islice,
        "pairwise": demo_pairwise,
        "starmap": demo_starmap,
        "tee": demo_tee,
        "zip_longest": demo_zip_longest,
        "batched": demo_batched,
        "product": demo_product,
        "permutations": demo_permutations,
        "combinations": demo_combinations,
        "combinations_with_replacement": demo_combinations_with_replacement,
    }
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("function", choices=demos)
    args = parser.parse_args()
    print(f"СРС 1. itertools.{args.function}")
    demos[args.function]()
    print("ПРОВЕРКИ ПРОЙДЕНЫ")


if __name__ == "__main__":
    main()
