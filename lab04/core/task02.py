"""Задание 2. Семь задач, выраженных чистыми левыми свёртками."""

import sys
from collections.abc import Callable, Hashable, Iterable
from functools import partial, reduce
from operator import add, mul
from typing import Any, TypeVar

T = TypeVar("T")
K = TypeVar("K", bound=Hashable)
_MISSING = object()


def product(xs: Iterable[int | float]) -> int | float:
    """Перемножить элементы; пустое произведение равно единице."""
    return reduce(mul, xs, 1)


def choose_larger(accumulator: Any, value: Any) -> Any:
    """Выбрать больший элемент без встроенной max."""
    return value if accumulator is _MISSING or value > accumulator else accumulator


def maximum(xs: Iterable[T]) -> T:
    """Найти максимум непустого входа; для пустого поднять ValueError."""
    result = reduce(choose_larger, xs, _MISSING)
    if result is _MISSING:
        raise ValueError("maximum() arg is an empty sequence")
    return result


def flatten(list_of_lists: Iterable[Iterable[T]]) -> list[T]:
    """Сплющить ровно один уровень, создавая новый список."""
    return reduce(add, map(list, list_of_lists), [])


def identity(value: Any) -> Any:
    """Вернуть аргумент без изменения."""
    return value


def compose_step(
    accumulated: Callable[[Any], Any], function: Callable[[Any], Any]
) -> Callable[[Any], Any]:
    """Присоединить следующую внешнюю функцию к композиции."""
    return lambda value: function(accumulated(value))


def compose(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Скомпоновать справа налево; compose() является тождественной."""
    return reduce(compose_step, reversed(funcs), identity)


def rle_step(accumulator: list[tuple[str, int]], char: str) -> list[tuple[str, int]]:
    """Вернуть новое кодирование после добавления одного символа."""
    if accumulator and accumulator[-1][0] == char:
        return accumulator[:-1] + [(char, accumulator[-1][1] + 1)]
    return accumulator + [(char, 1)]


def rle(text: str) -> list[tuple[str, int]]:
    """Закодировать соседние одинаковые символы парами символ/длина."""
    return reduce(rle_step, text, [])


def digit_step(accumulator: int, digit: int) -> int:
    """Добавить десятичную цифру справа и проверить её допустимость."""
    if type(digit) is not int or not 0 <= digit <= 9:
        raise ValueError("Ожидается целая цифра от 0 до 9")
    return 10 * accumulator + digit


def digits_to_int(digits: Iterable[int]) -> int:
    """Построить число из десятичных цифр; пустой вход означает ноль."""
    return reduce(digit_step, digits, 0)


def count_step(key: Callable[[T], K], counts: dict[K, int], value: T) -> dict[K, int]:
    """Вернуть новую таблицу частот с учётом одного значения."""
    group = key(value)
    return {**counts, group: counts.get(group, 0) + 1}


def count_by(key: Callable[[T], K], xs: Iterable[T]) -> dict[K, int]:
    """Посчитать элементы каждого ключа без Counter и мутаций входа."""
    return reduce(partial(count_step, key), xs, {})


def show(section: int, *values: object) -> None:
    """Показать выбранный подпункт; проверки всё равно выполняются целиком."""
    if len(sys.argv) == 1 or section == 0 or int(sys.argv[1]) == section:
        print(*values)


def main() -> None:
    """Показать результаты всех семи функций и граничные проверки."""
    assert product((2, 3, 4)) == 24 and product(()) == 1
    show(1, "2.1 product([2,3,4]) =", product((2, 3, 4)), "; product([]) = 1")
    assert maximum((-7, -2, -9)) == -2 and maximum((5,)) == 5
    try:
        maximum(())
    except ValueError:
        show(2, "2.2 maximum([-7,-2,-9]) = -2; пустой вход: ValueError")
    else:
        raise AssertionError("Пустой максимум должен отклоняться")
    nested = [[1, 2], [], [3, [4]]]
    assert flatten(nested) == [1, 2, 3, [4]]
    assert nested == [[1, 2], [], [3, [4]]] and flatten(()) == []
    show(3, "2.3 flatten([[1,2],[],[3,[4]]]) =", flatten(nested))
    f = compose(lambda x: x + 1, lambda x: x * 2)
    assert f(3) == 7 and compose()(3) == 3
    show(4, "2.4 compose(x+1, x*2)(3) = 7; порядок справа налево")
    assert rle("aaabccdddd") == [("a", 3), ("b", 1), ("c", 2), ("d", 4)]
    assert rle("") == [] and rle("абба") == [("а", 1), ("б", 2), ("а", 1)]
    show(5, "2.5 rle('aaabccdddd') =", rle("aaabccdddd"))
    assert digits_to_int((2, 0, 2, 6)) == 2026 and digits_to_int(()) == 0
    assert digits_to_int((0, 0, 7)) == 7
    try:
        digits_to_int((2, 10))
    except ValueError:
        show(6, "2.6 digits_to_int([2,0,2,6]) = 2026; цифра 10: ValueError")
    else:
        raise AssertionError("Некорректная цифра должна отклоняться")
    words = ("дом", "лес", "река", "мир")
    assert count_by(len, words) == {3: 3, 4: 1} and count_by(len, ()) == {}
    show(7, "2.7 count_by(len, ['дом','лес','река','мир']) =", count_by(len, words))
    show(0, "PASS: все 7 свёрток, пустые входы, порядок, входы не изменены.")


if __name__ == "__main__":
    main()
