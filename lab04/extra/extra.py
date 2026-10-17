"""Дополнительное задание: окна, глобальная группировка и сравнение с toolz."""

import sys
from argparse import ArgumentParser
from collections.abc import Callable, Hashable, Iterable, Iterator
from functools import reduce
from importlib.metadata import version
from itertools import count, islice, tee
from operator import itemgetter
from pathlib import Path
from timeit import repeat
from typing import TypeVar

T = TypeVar("T")
K = TypeVar("K", bound=Hashable)


def sliding_window(n: int, iterable: Iterable[T]) -> Iterator[tuple[T, ...]]:
    """Лениво возвращает полные окна длины n, не изменяя элементы источника."""
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError("Размер окна должен быть положительным целым числом")
    shifted = map(
        lambda pair: islice(pair[1], pair[0], None),
        enumerate(tee(iterable, n)),
    )
    return zip(*shifted)


def group_by(
    key: Callable[[T], K], iterable: Iterable[T]
) -> Iterator[tuple[K, tuple[T, ...]]]:
    """Откладывает глобальную группировку до первого next; хранит весь вход."""

    def collect(groups: dict[K, tuple[T, ...]], value: T) -> dict[K, tuple[T, ...]]:
        """Создаёт новый словарь и новый кортеж только изменяемой группы."""
        group_key = key(value)
        return {**groups, group_key: groups.get(group_key, ()) + (value,)}

    yield from reduce(collect, iterable, {}).items()


def check_error(call: Callable[[], object], expected: type[Exception]) -> None:
    """Проверяет, что вычисление действительно вызывает ожидаемую ошибку."""
    try:
        call()
    except expected:
        return
    raise AssertionError(f"Ожидалось исключение {expected.__name__}")


def run_checks(
    toolz_window: Callable[..., object], toolz_groups: Callable[..., object]
) -> None:
    """Проверяет значения, границы, отложенность и сохранность входа."""
    data = (1, 2, 3, 4, 5)
    assert list(sliding_window(3, data)) == [(1, 2, 3), (2, 3, 4), (3, 4, 5)]
    assert list(sliding_window(1, data)) == [(1,), (2,), (3,), (4,), (5,)]
    assert list(sliding_window(6, data)) == []
    assert list(sliding_window(2, ())) == []
    assert list(sliding_window(5, data)) == [data]
    assert list(sliding_window(3, iter(data))) == list(toolz_window(3, data))
    check_error(lambda: sliding_window(0, data), ValueError)
    check_error(lambda: sliding_window(-2, data), ValueError)
    assert list(islice(sliding_window(3, count()), 3)) == [
        (0, 1, 2),
        (1, 2, 3),
        (2, 3, 4),
    ]
    source = iter(data)
    windows = sliding_window(3, source)
    assert next(source) == 1  # Создание окон не читало источник.
    assert next(windows) == (2, 3, 4)
    assert data == (1, 2, 3, 4, 5)
    words = ("кот", "мир", "кит", "мак", "кошка")
    expected = {"к": ("кот", "кит", "кошка"), "м": ("мир", "мак")}
    assert dict(group_by(itemgetter(0), words)) == expected
    assert dict(group_by(itemgetter(0), ())) == {}
    assert dict(group_by(lambda value: value % 2, data)) == {1: (1, 3, 5), 0: (2, 4)}
    assert dict(
        map(lambda pair: (pair[0], list(pair[1])), group_by(itemgetter(0), words))
    ) == toolz_groups(itemgetter(0), words)
    source2 = iter(data)
    groups = group_by(lambda value: value % 2, source2)
    assert next(source2) == 1  # До первого next группировка не читает вход.
    assert dict(groups) == {0: (2, 4), 1: (3, 5)}
    assert tuple(source2) == ()  # Для завершённых групп понадобился весь вход.
    assert words == ("кот", "мир", "кит", "мак", "кошка")
    print("Проверки: 20/20 успешно, в том числе 2 ожидаемые ошибки.")


def benchmark(
    toolz_window: Callable[..., object], toolz_groups: Callable[..., object]
) -> None:
    """Измеряет полные результаты, исключив подготовку входа из таймера."""
    window_data = tuple(range(20_000))
    group_data = tuple(range(5_000))

    def key(value: int) -> int:
        """Распределяет тестовые числа по десяти остаткам от деления."""
        return value % 10

    own_window = (
        min(repeat(lambda: tuple(sliding_window(5, window_data)), repeat=5, number=10))
        / 10
    )
    ref_window = (
        min(repeat(lambda: tuple(toolz_window(5, window_data)), repeat=5, number=10))
        / 10
    )
    own_group = (
        min(repeat(lambda: dict(group_by(key, group_data)), repeat=5, number=3)) / 3
    )
    ref_group = (
        min(repeat(lambda: toolz_groups(key, group_data), repeat=5, number=3)) / 3
    )
    assert tuple(sliding_window(5, window_data)) == tuple(toolz_window(5, window_data))
    assert dict(
        map(
            lambda pair: (pair[0], tuple(pair[1])),
            toolz_groups(key, group_data).items(),
        )
    ) == dict(group_by(key, group_data))
    print("timeit: минимум из 5 серий, секунды на один полный результат.")
    print(
        f"Окна: N=20000, n=5, 10 запусков/серию; своё={own_window:.6f}, "
        f"toolz={ref_window:.6f}."
    )
    print(
        f"Группы: N=5000, 10 ключей, 3 запуска/серию; своё={own_group:.6f}, "
        f"toolz={ref_group:.6f}."
    )
    print("Повторное измерение может дать иное время; значения не гарантированы.")


def main() -> None:
    """Печатает выбранную часть задания и проверяет фактические результаты."""
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--part", choices=("all", "windows", "groups", "benchmark"), default="all"
    )
    part = parser.parse_args().part
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "vendor_local"))
    import toolz

    print("Дополнительное задание. Python", sys.version.split()[0])
    print("toolz", version("toolz"))
    run_checks(toolz.sliding_window, toolz.groupby)
    if part in ("all", "windows"):
        data = (1, 2, 3, 4, 5)
        print("sliding_window(3):", list(sliding_window(3, data)))
        print("toolz.sliding_window:", list(toolz.sliding_window(3, data)))
        print("Первые окна count:", list(islice(sliding_window(3, count()), 3)))
        print("Короткий вход:", list(sliding_window(6, data)))
        print("Окна читают источник при next; бесконечный источник допустим.")
    if part in ("all", "groups"):
        words = ("кот", "мир", "кит", "мак", "кошка")
        print("group_by:", dict(group_by(itemgetter(0), words)))
        print("toolz.groupby:", toolz.groupby(itemgetter(0), words))
        print("Группы совпали после приведения к одному типу контейнера.")
        print("group_by отложенная, но НЕ потоковая: первый next читает весь вход.")
        print("Глобальные завершённые группы требуют конца входа и O(N) памяти.")
    if part in ("all", "benchmark"):
        benchmark(toolz.sliding_window, toolz.groupby)


if __name__ == "__main__":
    main()
