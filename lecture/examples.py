"""Проверяемые примеры всех разделов лекции № 4.

Запуск: python examples.py <номер от 01 до 15>.
Числа населения и другие наборы служат только учебными данными.
"""

from __future__ import annotations

import argparse
import math
import operator
from collections import Counter
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from functools import (
    cache,
    cmp_to_key,
    lru_cache,
    partial,
    reduce,
    singledispatch,
    total_ordering,
    wraps,
)
from itertools import (
    accumulate,
    chain,
    combinations,
    count,
    dropwhile,
    groupby,
    islice,
    pairwise,
    product,
    starmap,
    takewhile,
)
from typing import Any, NamedTuple, TypeVar

T = TypeVar("T")
U = TypeVar("U")


def apply_to_all(func: Callable[[T], U], items: Iterable[T]) -> list[U]:
    """Применить переданную функцию ко всем входным элементам."""
    return [func(item) for item in items]


def make_multiplier(k: int) -> Callable[[int], int]:
    """Вернуть функцию умножения, которая запоминает множитель k."""

    def multiply(x: int) -> int:
        """Умножить x на множитель из замыкания."""
        return x * k

    return multiply


def example_01() -> None:
    """Функция как аргумент и функция как результат."""
    double, triple = make_multiplier(2), make_multiplier(3)
    doubled = apply_to_all(double, [1, 2, 3])
    tripled = apply_to_all(triple, [1, 2, 3])
    upper = apply_to_all(str.upper, ["map", "filter"])
    print(doubled, tripled, upper, sep="\n")
    assert doubled == [2, 4, 6] and tripled == [3, 6, 9]
    assert upper == ["MAP", "FILTER"]
    assert apply_to_all(double, []) == []
    assert double(-3) == -6 and triple(0) == 0
    assert sorted(["aaa", "b", "cc"], key=len) == ["b", "cc", "aaa"]
    assert max(["aaa", "b", "cc"], key=len) == "aaa"
    print("Проверены пустой вход, отрицательное число, sorted и max с key.")


def example_02() -> None:
    """map: один вход, несколько входов, ленивость и исчерпание."""
    celsius = [-10, 0, 25.5, 36.6, 100]
    fahrenheit = map(lambda c: c * 9 / 5 + 32, celsius)
    print(fahrenheit)
    temperatures = list(fahrenheit)
    powers = list(map(pow, [2, 3, 4], [5, 2, 3]))
    digits = list(map(int, "2026"))
    print(temperatures, powers, digits, sep="\n")
    expected = [14.0, 32.0, 77.9, 97.88, 212.0]
    assert all(math.isclose(a, b) for a, b in zip(temperatures, expected))
    assert len(temperatures) == len(expected)
    assert powers == [32, 9, 64] and digits == [2, 0, 2, 6]
    assert list(fahrenheit) == []
    assert list(map(pow, [2, 3, 4], [5, 2])) == [32, 9]
    assert list(map(int, [])) == []
    calls: list[int] = []

    def observed_square(x: int) -> int:
        """Зарегистрировать вызов для проверки ленивого вычисления."""
        calls.append(x)
        return x * x

    lazy = map(observed_square, [2, 3])
    assert calls == []
    assert next(lazy) == 4 and calls == [2]
    assert list(lazy) == [9] and calls == [2, 3]
    print("Ленивость, короткий вход, пустой вход и повторный обход проверены.")


def is_prime(n: int) -> bool:
    """Определить простоту целого числа без ошибки округления корня."""
    return n > 1 and all(n % d for d in range(2, math.isqrt(n) + 1))


def example_03() -> None:
    """filter с предикатом и с None."""
    primes = list(filter(is_prime, range(30)))
    truthy = list(filter(None, [0, 1, "", "ok", None, [], [0]]))
    digits = list(filter(str.isdigit, ["12", "abc", "7", "3.5"]))
    print(primes, truthy, digits, sep="\n")
    assert primes == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    assert truthy == [1, "ok", [0]] and digits == ["12", "7"]
    assert not any(is_prime(x) for x in [-7, -1, 0, 1, 4, 49])
    assert is_prime(2) and is_prime(97)
    assert list(filter(is_prime, [])) == []
    print("Проверены отрицательные числа, 0, 1, квадрат 49 и пустой вход.")


def example_04() -> None:
    """Левая свёртка суммы, произведения и максимума."""
    nums = [3, 1, 4, 1, 5, 9, 2, 6]
    total = reduce(lambda acc, x: acc + x, nums, 0)
    multiplied = reduce(lambda acc, x: acc * x, nums, 1)
    maximum = reduce(lambda a, b: a if a > b else b, nums)
    print(total, multiplied, maximum)

    def traced_add(acc: int, x: int) -> int:
        """Напечатать один шаг свёртки и вернуть новый аккумулятор."""
        print(f"acc={acc:>2}, x={x} -> {acc + x}")
        return acc + x

    assert (total, multiplied, maximum) == (31, 6480, 9)
    assert reduce(traced_add, [1, 2, 3, 4], 0) == 10
    assert reduce(operator.add, [], 0) == 0
    assert reduce(operator.mul, [], 1) == 1
    assert reduce(operator.sub, [1, 2, 3], 0) == -6
    assert sum(nums) == total and math.prod(nums) == multiplied
    assert max(nums) == maximum
    print("Проверены нейтральные элементы и порядок левой свёртки.")


def map_with_reduce(func: Callable[[T], U], xs: Iterable[T]) -> list[U]:
    """Выразить отображение через reduce с новым списком на каждом шаге."""
    return reduce(lambda acc, x: acc + [func(x)], xs, [])


def filter_with_reduce(pred: Callable[[T], bool], xs: Iterable[T]) -> list[T]:
    """Выразить фильтрацию через reduce без изменения входного списка."""
    return reduce(lambda acc, x: acc + [x] if pred(x) else acc, xs, [])


def example_05() -> None:
    """Частоты слов, map и filter, выраженные через reduce."""
    words = ["лямбда", "map", "фильтр", "map", "свёртка", "лямбда", "map"]
    before = words.copy()
    freq = reduce(lambda acc, w: {**acc, w: acc.get(w, 0) + 1}, words, {})
    lengths = map_with_reduce(len, words[:3])
    long_words = filter_with_reduce(lambda w: len(w) > 3, words)
    print(freq)
    print(lengths, long_words)
    assert freq == {"лямбда": 2, "map": 3, "фильтр": 1, "свёртка": 1}
    assert freq == dict(Counter(words))
    assert lengths == [6, 3, 6]
    assert long_words == ["лямбда", "фильтр", "свёртка", "лямбда"]
    assert map_with_reduce(len, []) == []
    assert filter_with_reduce(bool, []) == []
    assert words == before
    print("Результаты совпали с Counter; исходный список не изменился.")
    print("Пустые последовательности проверены.")


class City(NamedTuple):
    """Учебная запись о городе."""

    name: str
    population: int


def example_06() -> None:
    """Операции и готовые функции доступа из operator."""
    print(reduce(operator.add, range(1, 11)), reduce(operator.mul, range(1, 6)))
    rows = [("Алматы", 2_200_000), ("Астана", 1_400_000), ("Шымкент", 1_200_000)]
    ordered = sorted(rows, key=operator.itemgetter(1))
    names = list(map(operator.itemgetter(0), rows))
    cities = [City(*row) for row in rows]
    largest = max(cities, key=operator.attrgetter("population")).name
    replaced = list(
        map(operator.methodcaller("replace", "а", "*"), ["Алматы", "Астана"])
    )
    pairs = list(map(operator.itemgetter(0, 1), [(1, 2, 3), (4, 5, 6)]))
    print(ordered, names, largest, replaced, pairs, sep="\n")
    assert ordered == [rows[2], rows[1], rows[0]]
    assert names == ["Алматы", "Астана", "Шымкент"] and largest == "Алматы"
    assert replaced == ["Алм*ты", "Аст*н*"] and pairs == [(1, 2), (4, 5)]
    assert rows[0] == ("Алматы", 2_200_000)


def power(base: int, exponent: int) -> int:
    """Возвести целое основание в неотрицательную целую степень."""
    if exponent < 0:
        raise ValueError("В примере степень должна быть неотрицательной")
    return base**exponent


def example_07() -> None:
    """Частичное применение позиционных и именованных аргументов."""
    square, cube = partial(power, exponent=2), partial(power, exponent=3)
    two_to = partial(power, 2)
    parsed = list(map(partial(int, base=2), ["101", "1111", "100000"]))
    print(square(7), cube(3), two_to(10))
    print(parsed)
    assert (square(7), cube(3), two_to(10)) == (49, 27, 1024)
    assert parsed == [5, 15, 32]
    assert square(0) == 0 and square(-3) == 9 and two_to(0) == 1
    assert square(2, exponent=3) == 8
    print("Keyword можно переопределить: square(2, exponent=3) = 8.")


def compare_versions(a: str, b: str) -> int:
    """Сравнить версии из числовых компонентов, разделённых точками."""
    pa, pb = tuple(map(int, a.split("."))), tuple(map(int, b.split(".")))
    return (pa > pb) - (pa < pb)


def example_08() -> None:
    """Сортировка версий через преобразователь компаратора cmp_to_key."""
    versions = ["3.10.1", "3.9.18", "3.12.0", "3.10.0"]
    result = sorted(versions, key=cmp_to_key(compare_versions))
    print(result)
    assert result == ["3.9.18", "3.10.0", "3.10.1", "3.12.0"]
    assert compare_versions("3.10.0", "3.10.0") == 0
    assert compare_versions("3.9.18", "3.10.0") == -1
    assert compare_versions("3.12.0", "3.10.0") == 1
    assert sorted([], key=cmp_to_key(compare_versions)) == []
    print("Равные версии, обе стороны сравнения и пустой список проверены.")


def example_09() -> None:
    """Выбор обработчика по типу первого аргумента."""

    @singledispatch
    def describe(value: object) -> str:
        """Описать тип значения при отсутствии специального обработчика."""
        return f"объект типа {type(value).__name__}"

    @describe.register(int)
    def describe_int(value: int) -> str:
        """Описать целое число."""
        return f"целое число {value}"

    @describe.register(list)
    def describe_list(value: list[object]) -> str:
        """Рекурсивно описать содержимое списка."""
        return f"список из {len(value)} элементов: " + ", ".join(map(describe, value))

    first, second = describe(42), describe([1, "a", 2.5])
    print(first, second, sep="\n")
    assert first == "целое число 42"
    assert second == (
        "список из 3 элементов: целое число 1, объект типа str, объект типа float"
    )
    assert describe([]) == "список из 0 элементов: "
    assert describe(True) == "целое число True"
    assert "список из 1 элементов: целое число 2" in describe([[2]])
    print("Пустой и вложенный списки проверены; bool наследуется от int.")


def example_10() -> None:
    """Все десять строк основного примера itertools из лекции."""
    results = [
        list(accumulate([1, 2, 3, 4, 5])),
        list(accumulate([1, 2, 3, 4, 5], operator.mul)),
        list(chain([1, 2], (3, 4), "ab")),
        list(islice(count(10, 5), 4)),
        list(takewhile(lambda x: x < 5, [1, 3, 6, 2])),
        list(dropwhile(lambda x: x < 5, [1, 3, 6, 2])),
        list(starmap(pow, [(2, 3), (10, 2)])),
        list(product("AB", [0, 1])),
        list(combinations("ABCD", 2)),
        list(pairwise([1, 4, 9, 16])),
    ]
    for result in results:
        print(result)
    assert results == [
        [1, 3, 6, 10, 15],
        [1, 2, 6, 24, 120],
        [1, 2, 3, 4, "a", "b"],
        [10, 15, 20, 25],
        [1, 3],
        [6, 2],
        [8, 100],
        [("A", 0), ("A", 1), ("B", 0), ("B", 1)],
        [("A", "B"), ("A", "C"), ("A", "D"), ("B", "C"), ("B", "D"), ("C", "D")],
        [(1, 4), (4, 9), (9, 16)],
    ]


def example_11() -> None:
    """Группировка соседних записей и суммы по городам."""
    sales = [
        ("Алматы", 120),
        ("Астана", 80),
        ("Алматы", 60),
        ("Астана", 40),
        ("Караганда", 30),
    ]
    by_city = sorted(sales, key=operator.itemgetter(0))
    totals = {
        city: sum(map(operator.itemgetter(1), group))
        for city, group in groupby(by_city, key=operator.itemgetter(0))
    }
    print(totals)
    assert totals == {"Алматы": 180, "Астана": 120, "Караганда": 30}
    assert sum(totals.values()) == sum(map(operator.itemgetter(1), sales))
    ungrouped = [
        (name, len(list(group)))
        for name, group in groupby(sales, key=operator.itemgetter(0))
    ]
    assert len(ungrouped) == 5
    print("Без сортировки получаются пять отдельных соседних групп:")
    print(ungrouped)


def example_12() -> None:
    """Сравнить map/filter и списковое включение на одном входе."""
    nums = range(1, 11)
    a = list(map(lambda x: x * x, filter(lambda x: x % 2 == 0, nums)))
    b = [x * x for x in nums if x % 2 == 0]
    print(a == b, b)
    assert a == b == [4, 16, 36, 64, 100]
    for values in [[], [-4, -3, -2, -1, 0], [1, 3, 5]]:
        left = list(map(lambda x: x * x, filter(lambda x: x % 2 == 0, values)))
        right = [x * x for x in values if x % 2 == 0]
        assert left == right
    generator = (x * x for x in nums if x % 2 == 0)
    assert list(generator) == b
    print("Проверены также пустой вход, отрицательные и нечётные числа.")


def example_13() -> None:
    """Реально воспроизвести и проверить типичные ошибки лекции."""
    mapped = map(int, ["1", "2"])
    first, second = list(mapped), list(mapped)
    print("Повторный обход map:", first, second)
    assert first == [1, 2] and second == []
    filtered = filter(bool, [0, 1])
    assert list(filtered) == [1] and list(filtered) == []
    try:
        reduce(operator.add, [])
    except TypeError as error:
        print("Пустой reduce без initial:", type(error).__name__)
    else:
        raise AssertionError("Ожидался TypeError")
    events: list[int] = []
    pending = map(events.append, [10, 20])
    print("Побочные эффекты до обхода:", events)
    assert events == []
    list(pending)
    print("Побочные эффекты после обхода:", events)
    assert events == [10, 20]
    groups = [(key, list(part)) for key, part in groupby("ABA")]
    print("groupby без сортировки:", groups)
    assert groups == [("A", ["A"]), ("B", ["B"]), ("A", ["A"])]


def example_14() -> None:
    """Оставшиеся операции из таблицы operator."""
    arithmetic = [
        operator.add(8, 3),
        operator.sub(8, 3),
        operator.mul(8, 3),
        operator.truediv(8, 2),
        operator.mod(8, 3),
        operator.pow(2, 3),
    ]
    comparisons = [
        operator.eq(2, 2),
        operator.ne(2, 3),
        operator.lt(2, 3),
        operator.le(2, 2),
        operator.gt(3, 2),
        operator.ge(2, 2),
    ]
    unary = [operator.not_([]), operator.truth([0]), operator.neg(7)]
    print("add, sub, mul, truediv, mod, pow:", arithmetic)
    print("eq, ne, lt, le, gt, ge:", comparisons)
    print("not_, truth, neg:", unary)
    assert arithmetic == [11, 5, 24, 4.0, 2, 8]
    assert comparisons == [True] * 6 and unary == [True, True, -7]
    try:
        operator.truediv(1, 0)
    except ZeroDivisionError:
        print("Деление на ноль: ожидаемый ZeroDivisionError.")
    else:
        raise AssertionError("Ожидался ZeroDivisionError")


def example_15() -> None:
    """Упомянутые в лекции wraps, cache, lru_cache и total_ordering."""

    def checked(func: Callable[[int], int]) -> Callable[[int], int]:
        """Сохранить метаданные функции при добавлении проверки аргумента."""

        @wraps(func)
        def wrapper(value: int) -> int:
            """Проверить аргумент и вызвать исходную функцию."""
            if value < 0:
                raise ValueError("Аргумент должен быть неотрицательным")
            return func(value)

        return wrapper

    @checked
    def square(value: int) -> int:
        """Вернуть квадрат числа."""
        return value * value

    assert square(5) == 25 and square.__name__ == "square"
    assert square.__doc__ == "Вернуть квадрат числа."
    print("wraps:", square.__name__, square.__doc__, square(5))

    @cache
    def fib(n: int) -> int:
        """Вычислить число Фибоначчи для неотрицательного n."""
        if n < 0:
            raise ValueError("n должно быть неотрицательным")
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    assert fib(10) == 55
    before = fib.cache_info()
    assert fib(10) == 55
    after = fib.cache_info()
    assert after.hits == before.hits + 1
    print("cache: fib(10) =", fib(10), "; промахов =", after.misses)

    @lru_cache(maxsize=2)
    def cube(n: int) -> int:
        """Вернуть куб числа с ограниченным кешем."""
        return n**3

    assert [cube(x) for x in [1, 2, 1, 3]] == [1, 8, 1, 27]
    assert cube.cache_info().currsize == 2
    print("lru_cache:", cube.cache_info())

    @total_ordering
    @dataclass(frozen=True)
    class Score:
        """Неизменяемая оценка, упорядоченная по баллам."""

        points: int

        def __lt__(self, other: Any) -> bool:
            """Сравнить оценки, отказавшись от несовместимого типа."""
            if not isinstance(other, Score):
                return NotImplemented
            return self.points < other.points

    assert Score(3) < Score(5) and Score(3) <= Score(3)
    assert Score(5) > Score(3) and Score(5) >= Score(5)
    print("total_ordering: 3 < 5, 3 <= 3, 5 > 3, 5 >= 5:", True)


def main() -> None:
    """Выбрать и выполнить один пример с обязательными проверками."""
    examples: dict[str, Callable[[], None]] = {
        "01": example_01,
        "02": example_02,
        "03": example_03,
        "04": example_04,
        "05": example_05,
        "06": example_06,
        "07": example_07,
        "08": example_08,
        "09": example_09,
        "10": example_10,
        "11": example_11,
        "12": example_12,
        "13": example_13,
        "14": example_14,
        "15": example_15,
    }
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("example", choices=examples)
    args = parser.parse_args()
    print(f"Лекция 04. Пример {args.example}")
    examples[args.example]()
    print("ПРОВЕРКИ ПРОЙДЕНЫ")


if __name__ == "__main__":
    main()
