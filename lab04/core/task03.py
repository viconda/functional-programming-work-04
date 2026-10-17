"""Задание 3. operator и воспроизводимое измерение на 10**6 записей."""

import json
import platform
import statistics
import sys
import timeit
from collections.abc import Callable, Sequence
from functools import partial, reduce
from operator import add, attrgetter, itemgetter, methodcaller, mul, truth
from pathlib import Path
from typing import Any, NamedTuple


class Person(NamedTuple):
    """Запись для демонстрации attrgetter."""

    name: str
    score: int


def operator_solution(records: Sequence[dict[str, Any]]) -> tuple[Any, ...]:
    """Выполнить исходные пять преобразований без лямбда-выражений."""
    names = list(map(itemgetter("name"), records))
    total = reduce(add, map(itemgetter("score"), records), 0)
    best = max(records, key=itemgetter("score"))
    tags = list(map(methodcaller("split", ","), map(itemgetter("tags"), records)))
    by_two = sorted(records, key=itemgetter("score", "name"))
    return names, total, best, tags, by_two


def lambda_solution(records: Sequence[dict[str, Any]]) -> tuple[Any, ...]:
    """Сохранить исходные операции как эталон для сравнения."""
    names = list(map(lambda record: record["name"], records))
    total = reduce(lambda a, b: a + b, map(lambda record: record["score"], records), 0)
    best = max(records, key=lambda record: record["score"])
    tags = list(map(lambda record: record["tags"].split(","), records))
    by_two = sorted(records, key=lambda record: (record["score"], record["name"]))
    return names, total, best, tags, by_two


def make_record(index: int) -> dict[str, str | int]:
    """Создать тестовую запись с разнообразными значениями ключей."""
    return {"name": chr(65 + index % 26), "score": index % 101, "tags": "x,y"}


def measure_case(
    label: str, first: Callable[[], Any], second: Callable[[], Any]
) -> dict[str, Any]:
    """Проверить равенство, затем сделать три независимых замера каждого."""
    assert first() == second(), label
    samples_lambda = timeit.repeat(first, repeat=3, number=1)
    samples_operator = timeit.repeat(second, repeat=3, number=1)
    median_lambda = statistics.median(samples_lambda)
    median_operator = statistics.median(samples_operator)
    print(f"{label}: lambda {median_lambda:.6f} с; operator {median_operator:.6f} с")
    print("  3 повтора lambda:", tuple(map(partial(round, ndigits=6), samples_lambda)))
    print(
        "  3 повтора operator:", tuple(map(partial(round, ndigits=6), samples_operator))
    )
    return {
        "case": label,
        "lambda_seconds": samples_lambda,
        "operator_seconds": samples_operator,
        "lambda_median": median_lambda,
        "operator_median": median_operator,
        "ratio_lambda_over_operator": median_lambda / median_operator,
    }


def main() -> None:
    """Напечатать исходный пример и измерить восемь видов операций."""
    example = [
        {"name": "A", "score": 70, "tags": "x,y"},
        {"name": "B", "score": 85, "tags": "y"},
    ]
    result = operator_solution(example)
    assert result == lambda_solution(example)
    print("Пример: names =", result[0], "; total =", result[1])
    print("best =", result[2], "; tags =", result[3])
    print("by_two =", result[4])
    count = 10**6
    records = list(map(make_record, range(count)))
    people = list(map(Person._make, map(itemgetter("name", "score"), records)))
    numbers = list(range(count))
    print("Среда:", platform.platform(), "; Python", sys.version.split()[0])
    print("Процессор:", platform.processor())
    print("N = 1000000; repeat = 3; number = 1; сравнение по медиане.")
    print("Создание входов не измеряется; сборка мусора timeit отключена.")
    cases = (
        (
            "names/itemgetter",
            lambda: list(map(lambda r: r["name"], records)),
            lambda: list(map(itemgetter("name"), records)),
        ),
        (
            "total/add+itemgetter",
            lambda: reduce(lambda a, b: a + b, map(lambda r: r["score"], records), 0),
            lambda: reduce(add, map(itemgetter("score"), records), 0),
        ),
        (
            "best/itemgetter",
            lambda: max(records, key=lambda r: r["score"]),
            lambda: max(records, key=itemgetter("score")),
        ),
        (
            "tags/methodcaller",
            lambda: list(map(lambda r: r["tags"].split(","), records)),
            lambda: list(
                map(methodcaller("split", ","), map(itemgetter("tags"), records))
            ),
        ),
        (
            "sort/itemgetter",
            lambda: sorted(records, key=lambda r: (r["score"], r["name"])),
            lambda: sorted(records, key=itemgetter("score", "name")),
        ),
        (
            "attributes/attrgetter",
            lambda: list(map(lambda p: p.score, people)),
            lambda: list(map(attrgetter("score"), people)),
        ),
        (
            "multiply/mul",
            lambda: list(map(lambda x: x * 2, numbers)),
            lambda: list(map(partial(mul, 2), numbers)),
        ),
        (
            "truth/truth",
            lambda: list(map(lambda x: bool(x), numbers)),
            lambda: list(map(truth, numbers)),
        ),
    )
    measured = tuple(map(lambda case: measure_case(*case), cases))
    payload = {
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "n": count,
        "repeat": 3,
        "number": 1,
        "cases": measured,
    }
    output = Path(__file__).with_name("benchmark_operator.json")
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("PASS: результаты каждого варианта совпали; измерения сохранены.")
    print("Преимущество operator зависит от операции и среды, а не гарантируется.")


if __name__ == "__main__":
    main()
