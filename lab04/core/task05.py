"""Задание 5. Десять чистых функций на основе itertools, Python 3.12+."""

import sys
from collections.abc import Iterable, Iterator
from itertools import (
    accumulate,
    batched,
    chain,
    combinations,
    count,
    cycle,
    dropwhile,
    groupby,
    islice,
    pairwise,
    product,
    takewhile,
)
from operator import itemgetter
from typing import TypeVar

T = TypeVar("T")


def progression() -> tuple[int, ...]:
    """Вернуть первые пятнадцать членов 1 + 3k."""
    return tuple(islice(count(1, 3), 15))


def passwords(alphabet: str = "abc") -> tuple[str, ...]:
    """Перечислить двухбуквенные строки с разрешёнными повторениями."""
    return tuple(map("".join, product(alphabet, repeat=2)))


def duties(students: Iterable[str]) -> tuple[tuple[str, ...], ...]:
    """Выбрать все тройки без учёта порядка и без повторений."""
    return tuple(combinations(students, 3))


def running_maximum(temperatures: Iterable[float]) -> tuple[float, ...]:
    """Для каждого префикса вернуть наибольшую температуру."""
    return tuple(accumulate(temperatures, max))


def differences(series: Iterable[float]) -> tuple[float, ...]:
    """Вычесть предыдущее значение из следующего в каждой паре."""
    return tuple(map(lambda pair: pair[1] - pair[0], pairwise(series)))


def batches(values: Iterable[T], size: int = 5) -> tuple[tuple[T, ...], ...]:
    """Разбить поток на пакеты, сохраняя последний неполный."""
    return tuple(batched(values, size))


def split_at_negative(
    values: Iterable[float],
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Разбить перед первым отрицательным, сохранив его в остатке."""
    source = tuple(values)
    return (
        tuple(takewhile(lambda value: value >= 0, source)),
        tuple(dropwhile(lambda value: value >= 0, source)),
    )


def round_robin(tasks: Iterable[T], people: Iterable[str]) -> tuple[tuple[T, str], ...]:
    """Циклически распределить задачи; пустой состав отклонить."""
    workers = tuple(people)
    if not workers:
        raise ValueError("Для распределения нужен хотя бы один исполнитель")
    return tuple(zip(tasks, cycle(workers)))


def join_lists(
    first: Iterable[T], second: Iterable[T], third: Iterable[T]
) -> Iterator[T]:
    """Вернуть ленивый chain, не материализуя промежуточный список."""
    return chain(first, second, third)


def group_words(words: Iterable[str]) -> dict[str, tuple[str, ...]]:
    """Сгруппировать непустые слова по первой букве после сортировки."""
    source = tuple(words)
    if not all(map(bool, source)):
        raise ValueError("У пустого слова нет первой буквы")
    return dict(
        map(
            lambda pair: (pair[0], tuple(pair[1])),
            groupby(sorted(source, key=itemgetter(0)), key=itemgetter(0)),
        )
    )


def demonstrate(number: int) -> None:
    """Запустить выбранный подпункт с проверками и реальным выводом."""
    if number == 1:
        result = progression()
        assert result == tuple(range(1, 44, 3)) and len(result) == 15
        print("5.1 count(1,3) + islice(...,15):", result)
    elif number == 2:
        result = passwords()
        assert result == ("aa", "ab", "ac", "ba", "bb", "bc", "ca", "cb", "cc")
        assert passwords("") == ()
        print("5.2 product('abc', repeat=2):", result, "; количество =", len(result))
    elif number == 3:
        result = duties(("Алия", "Борис", "Вика", "Дана", "Егор", "Жан"))
        assert len(result) == 20 and len(set(result)) == 20 and duties(("А", "Б")) == ()
        print("5.3 Все тройки дежурных, C(6,3) =", len(result))
        tuple(map(print, result))
    elif number == 4:
        source = (12, 10, 15, 14, 18, 17)
        result = running_maximum(source)
        assert result == (12, 12, 15, 15, 18, 18) and running_maximum(()) == ()
        assert running_maximum((-5, -3, -8)) == (-5, -3, -3)
        print("5.4 Температуры:", source, "; частичные максимумы:", result)
    elif number == 5:
        source = (100, 104, 101, 109, 109)
        result = differences(source)
        assert result == (4, -3, 8, 0) and differences((1,)) == ()
        print("5.5 Ряд:", source, "; разности соседей:", result)
    elif number == 6:
        result = batches(range(1, 24))
        assert tuple(map(len, result)) == (5, 5, 5, 5, 3)
        assert tuple(chain.from_iterable(result)) == tuple(range(1, 24))
        assert batches(()) == ()
        print("5.6 batched(range(1,24),5):", result)
        print(
            "Размеры пакетов:", tuple(map(len, result)), "; ни один элемент не потерян."
        )
    elif number == 7:
        source = (3, 0, 5, -2, 7, -1)
        result = split_at_negative(source)
        assert result == ((3, 0, 5), (-2, 7, -1))
        assert split_at_negative((1, 0)) == ((1, 0), ())
        assert split_at_negative((-1, 2)) == ((), (-1, 2))
        assert split_at_negative(()) == ((), ())
        print("5.7 Вход:", source, "; префикс:", result[0], "; остаток:", result[1])
        print("Первое отрицательное сохранено в остатке, исходный список не изменён.")
        strictly_after = result[1][1:]
        assert strictly_after == (7, -1)
        print(
            "Если понимать 'после него' строго, без первого отрицательного:",
            strictly_after,
        )
    elif number == 8:
        result = round_robin(range(1, 11), ("Алия", "Вика", "Дана"))
        assert (
            len(result) == 10
            and result[0] == (1, "Алия")
            and result[-1] == (10, "Алия")
        )
        print("5.8 Круговое распределение 10 задач:")
        tuple(map(print, result))
    elif number == 9:
        result = join_lists((1, 2), (), (3, 4, 5))
        assert isinstance(result, chain)
        materialized = tuple(result)
        assert materialized == (1, 2, 3, 4, 5) and tuple(result) == ()
        print("5.9 chain([1,2], [], [3,4,5]):", materialized)
        print("Объединение ленивое; повторное чтение исчерпанного chain: ().")
    elif number == 10:
        source = ("банан", "арбуз", "вишня", "абрикос", "брусника")
        result = group_words(source)
        assert result == {
            "а": ("арбуз", "абрикос"),
            "б": ("банан", "брусника"),
            "в": ("вишня",),
        }
        assert group_words(()) == {}
        print("5.10 Слова:", source)
        print("После сортировки по первой букве:", result)
    else:
        raise ValueError("Номер подпункта должен быть от 1 до 10")
    print(f"PASS: задание 5.{number}; результаты подтверждены assert.")


def main() -> None:
    """Выполнить все подпункты или один по номеру из командной строки."""
    if len(sys.argv) > 1:
        demonstrate(int(sys.argv[1]))
    else:
        tuple(map(demonstrate, range(1, 11)))


if __name__ == "__main__":
    main()
