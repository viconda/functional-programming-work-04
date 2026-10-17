"""Задание 1. Собственные ленивые map/filter и строгая reduce."""

from collections.abc import Callable, Iterable, Iterator
from functools import reduce
from operator import add, mul
from typing import Any

_MISSING = object()


def my_map(function: Callable[..., Any], *iterables: Iterable[Any]) -> Iterator[Any]:
    """Лениво вызвать function, останавливаясь на кратчайшем входе."""
    if not iterables:
        raise TypeError("my_map() must have at least two arguments")
    sources = tuple(map(iter, iterables))

    def generate() -> Iterator[Any]:
        """Отложить вызовы function до чтения результата."""
        for arguments in zip(*sources):
            yield function(*arguments)

    return generate()


def my_filter(
    predicate: Callable[[Any], Any] | None, iterable: Iterable[Any]
) -> Iterator[Any]:
    """Лениво отобрать элементы; None означает проверку их истинности."""
    source = iter(iterable)

    def generate() -> Iterator[Any]:
        """Проверять предикат только при продвижении итератора."""
        for value in source:
            if bool(value) if predicate is None else predicate(value):
                yield value

    return generate()


def my_reduce(
    function: Callable[[Any, Any], Any],
    iterable: Iterable[Any],
    initial: Any = _MISSING,
) -> Any:
    """Выполнить левую свёртку; отличать отсутствие initial от None."""
    source = iter(iterable)
    if initial is _MISSING:
        try:
            result = next(source)
        except StopIteration as error:
            raise TypeError(
                "reduce() of empty iterable with no initial value"
            ) from error
    else:
        result = initial
    for value in source:
        result = function(result, value)
    return result


def error_type(thunk: Callable[[], Any]) -> type[BaseException] | None:
    """Получить класс ошибки для сравнения контрактов в тестах."""
    try:
        thunk()
    except Exception as error:
        return type(error)
    return None


def verify(label: str, actual: Any, expected: Any) -> None:
    """Сравнить фактический результат с эталоном и напечатать PASS."""
    assert actual == expected, (label, actual, expected)
    print("PASS:", label)


def main() -> None:
    """Выполнить 23 проверки, включая ошибки и ленивость."""
    verify(
        "01 map, квадрат",
        list(my_map(lambda x: x * x, range(5))),
        list(map(lambda x: x * x, range(5))),
    )
    verify(
        "02 map, разные длины",
        list(my_map(add, (1, 2, 3), (10, 20))),
        list(map(add, (1, 2, 3), (10, 20))),
    )
    verify(
        "03 map, три входа",
        list(my_map(lambda a, b, c: a + b + c, (1, 2), (3,), (4, 5))),
        list(map(lambda a, b, c: a + b + c, (1, 2), (3,), (4, 5))),
    )
    verify("04 map, пустой вход", list(my_map(str, ())), list(map(str, ())))
    verify(
        "05 filter, предикат",
        list(my_filter(lambda x: x > 0, (-1, 0, 2))),
        list(filter(lambda x: x > 0, (-1, 0, 2))),
    )
    verify(
        "06 filter(None)",
        list(my_filter(None, (0, 1, "", "a", None, [], [2], False))),
        list(filter(None, (0, 1, "", "a", None, [], [2], False))),
    )
    verify("07 filter, пустой вход", list(my_filter(None, ())), list(filter(None, ())))
    verify(
        "08 reduce с initial", my_reduce(add, (1, 2, 3), 10), reduce(add, (1, 2, 3), 10)
    )
    verify("09 reduce без initial", my_reduce(mul, (2, 3, 4)), reduce(mul, (2, 3, 4)))
    verify("10 reduce пустой + initial", my_reduce(add, (), 17), reduce(add, (), 17))
    verify("11 reduce пустой + None", my_reduce(add, (), None), reduce(add, (), None))
    verify(
        "12 reduce пустой без initial",
        error_type(lambda: my_reduce(add, ())),
        error_type(lambda: reduce(add, ())),
    )
    verify(
        "13 map без входов",
        error_type(lambda: my_map(str)),
        error_type(lambda: map(str)),
    )
    verify(
        "14 map неитерируемый вход",
        error_type(lambda: my_map(str, 7)),
        error_type(lambda: map(str, 7)),
    )
    verify(
        "15 filter неитерируемый вход",
        error_type(lambda: my_filter(None, 7)),
        error_type(lambda: filter(None, 7)),
    )
    verify(
        "16 map невызываемая функция",
        error_type(lambda: list(my_map(None, (1,)))),
        error_type(lambda: list(map(None, (1,)))),
    )
    verify("17 reduce один элемент", my_reduce(None, (9,)), reduce(None, (9,)))
    verify(
        "18 reduce с None как значением",
        my_reduce(lambda a, b: (a, b), (5,), None),
        reduce(lambda a, b: (a, b), (5,), None),
    )
    events: list[int] = []

    def record(value: int) -> int:
        """Нечистый датчик вызовов, используемый только для проверки."""
        events.append(value)
        return value * 2

    delayed = my_map(record, (2, 3))
    verify("19 map ленив до next", events, [])
    assert next(delayed) == 4
    verify("20 map вычисляет один элемент", events, [2])
    assert list(delayed) == [6]
    verify("21 map исчерпан", list(delayed), [])
    filter_events: list[int] = []

    def positive(value: int) -> bool:
        """Записать проверки предиката для теста ленивости."""
        filter_events.append(value)
        return value > 0

    selected = my_filter(positive, (-1, 2))
    assert filter_events == []
    assert next(selected) == 2 and filter_events == [-1, 2]
    verify("22 filter ленив и исчерпывается", list(selected), [])
    verify(
        "23 filter ошибка предиката",
        error_type(lambda: list(my_filter(5, (1,)))),
        error_type(lambda: list(filter(5, (1,)))),
    )
    print("Итого: 23 проверки PASS. map/filter возвращают генераторы.")


if __name__ == "__main__":
    main()
