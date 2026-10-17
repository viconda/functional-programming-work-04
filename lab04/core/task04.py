"""Задание 4. partial, cmp_to_key и singledispatch."""

import re
import sys
from decimal import Decimal
from fractions import Fraction
from functools import cmp_to_key, partial, singledispatch
from itertools import dropwhile
from numbers import Number
from typing import Any


def convert(value: Decimal, rate: Decimal, fee: Decimal) -> Decimal:
    """Перевести сумму в тенге: value * rate * (1 - fee)."""
    if value < 0 or rate <= 0 or not Decimal(0) <= fee < Decimal(1):
        raise ValueError("Проверьте сумму, курс и долю комиссии")
    return (value * rate * (Decimal(1) - fee)).quantize(Decimal("0.01"))


def prerelease_part(text: str) -> tuple[int, int | str]:
    """Числовые части предрелиза упорядочить перед текстовыми."""
    return (0, int(text)) if text.isdigit() else (1, text)


def version_key(text: str) -> tuple[tuple[int, ...], int, tuple[Any, ...]]:
    """Разобрать версию; конечные нули нейтральны, релиз старше предрелиза."""
    match = re.fullmatch(
        r"(\d+(?:\.\d+)*)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?", text
    )
    if match is None:
        raise ValueError(f"Неверная версия: {text}")
    main, suffix = match.groups()
    numbers = tuple(map(int, main.split(".")))
    normalized = tuple(reversed(tuple(dropwhile(lambda n: n == 0, reversed(numbers)))))
    prerelease = tuple(map(prerelease_part, suffix.split("."))) if suffix else ()
    return normalized, int(suffix is None), prerelease


def compare_versions(left: str, right: str) -> int:
    """Вернуть -1, 0 или 1 по порядку нормализованных версий."""
    a, b = version_key(left), version_key(right)
    return (a > b) - (a < b)


@singledispatch
def summarize(value: Any) -> Number | Decimal:
    """Свернуть поддерживаемое значение; неизвестный тип отклонить."""
    raise TypeError(f"Неподдерживаемый тип: {type(value).__name__}")


@summarize.register(Number)
@summarize.register(Decimal)
def summarize_number(value: Number | Decimal) -> Number | Decimal:
    """Числа возвращаются без изменения."""
    return value


@summarize.register(bool)
def summarize_bool(value: bool) -> int:
    """Явно трактовать bool как 1 или 0, поскольку bool наследует int."""
    return int(value)


@summarize.register(str)
def summarize_string(value: str) -> int:
    """Вернуть длину строки в кодовых точках Unicode."""
    return len(value)


@summarize.register(list)
@summarize.register(tuple)
def summarize_sequence(value: list[Any] | tuple[Any, ...]) -> Number | Decimal:
    """Рекурсивно сложить результаты обработки элементов."""
    return sum(map(summarize, value))


@summarize.register(dict)
def summarize_mapping(value: dict[Any, Any]) -> Number | Decimal:
    """Рекурсивно сложить результаты для значений, не для ключей."""
    return sum(map(summarize, value.values()))


def show(section: int, *values: object) -> None:
    """Печатать выбранный пункт, выполняя проверки всех функций."""
    if len(sys.argv) == 1 or section == 0 or int(sys.argv[1]) == section:
        print(*values)


def main() -> None:
    """Проверить каждый из трёх пунктов на обычных и граничных данных."""
    values = tuple(map(Decimal, ("10", "50", "100")))
    usd = partial(convert, rate=Decimal("500"), fee=Decimal("0.01"))
    eur = partial(convert, rate=Decimal("550"), fee=Decimal("0.015"))
    rub = partial(convert, rate=Decimal("5"), fee=Decimal("0.02"))
    converted = tuple(
        map(lambda converter: tuple(map(converter, values)), (usd, eur, rub))
    )
    assert converted == (
        (Decimal("4950"), Decimal("24750"), Decimal("49500")),
        (Decimal("5417.50"), Decimal("27087.50"), Decimal("54175")),
        (Decimal("49"), Decimal("245"), Decimal("490")),
    )
    assert usd(Decimal(0)) == 0
    show(1, "4.1. Учебные курсы, НЕ рыночные: USD=500, EUR=550, RUB=5 KZT.")
    show(1, "Суммы 10, 50, 100; комиссии 1%, 1.5%, 2% удерживаются из результата.")
    show(1, "USD -> KZT:", converted[0])
    show(1, "EUR -> KZT:", converted[1])
    show(1, "RUB -> KZT:", converted[2])

    versions = (
        "1.10.2",
        "1.9",
        "1.10",
        "2.0.0-beta",
        "2.0.0",
        "1.10.0",
        "2.0.0-alpha.10",
        "2.0.0-alpha.2",
    )
    ordered = sorted(versions, key=cmp_to_key(compare_versions))
    assert ordered == [
        "1.9",
        "1.10",
        "1.10.0",
        "1.10.2",
        "2.0.0-alpha.2",
        "2.0.0-alpha.10",
        "2.0.0-beta",
        "2.0.0",
    ]
    assert compare_versions("1.10", "1.10.0") == 0
    assert compare_versions("2.0.0-beta", "2.0.0") == -1
    assert compare_versions("1.0.1", "1") == 1
    show(2, "4.2. cmp_to_key:", ordered)
    show(2, "1.10 == 1.10.0; alpha.2 < alpha.10 < beta < релиз.")

    nested = {"a": [1, "abc", (2, "xy")], "b": {"x": 4.5, "flag": True}}
    assert summarize(nested) == 13.5
    assert summarize(False) == 0 and type(summarize(True)) is int
    assert summarize([]) == 0 and summarize({}) == 0
    assert summarize(Decimal("1.25")) == Decimal("1.25")
    fraction = Fraction(1, 2)
    complex_value = complex(1, 2)
    assert summarize(fraction) is fraction
    assert summarize(complex_value) is complex_value
    assert summarize([Fraction(1, 2), Fraction(1, 4)]) == Fraction(3, 4)
    assert nested == {"a": [1, "abc", (2, "xy")], "b": {"x": 4.5, "flag": True}}
    show(3, "4.3. summarize(", nested, ") =", summarize(nested))
    show(3, "Расчёт: 1 + 3 + 2 + 2 + 4.5 + 1 = 13.5; True=1, False=0.")
    show(3, "Number: Fraction(1,2) и complex(1,2) возвращены без изменения.")
    try:
        summarize({1, 2})
    except TypeError:
        show(3, "Неизвестный тип set: TypeError. Пустые структуры: 0.")
    else:
        raise AssertionError("Множество должно отклоняться")
    show(0, "PASS: partial, порядок версий, вложенные структуры, неизменность.")


if __name__ == "__main__":
    main()
