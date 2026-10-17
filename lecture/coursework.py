"""Самостоятельная работа к лекции № 4: задания 2, 3 и 4.

Запуск: python coursework.py transactions|compose|json
Все функции работают с локальными данными и проверяют свой контракт.
"""

from __future__ import annotations

import argparse
import json
import math
from collections.abc import Callable, Iterable
from datetime import date
from decimal import Decimal
from functools import reduce, singledispatch
from itertools import groupby
from operator import itemgetter
from typing import Any, TypeVar

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
Transaction = tuple[str, str, Decimal]


def expense_report(
    transactions: Iterable[Transaction],
) -> dict[str, dict[str, Decimal]]:
    """Посчитать расходы по категориям и месяцам, не меняя вход.

    Дата должна иметь вид YYYY-MM-DD, сумма должна быть конечным
    неотрицательным Decimal. Месяц включает год, поэтому разные годы
    не объединяются. Валюта учебных записей: тенге.
    """
    rows = list(transactions)
    for day, category, amount in rows:
        parsed = date.fromisoformat(day)
        if parsed.isoformat() != day:
            raise ValueError("Дата должна иметь вид YYYY-MM-DD")
        if not category.strip():
            raise ValueError("Категория не должна быть пустой")
        if not isinstance(amount, Decimal):
            raise TypeError("Сумма должна иметь тип Decimal")
        if not amount.is_finite() or amount < 0:
            raise ValueError("Расход должен быть конечным и неотрицательным")

    def grouped_totals(
        key: Callable[[Transaction], str],
    ) -> dict[str, Decimal]:
        """Сортировать и группировать строго по одной функции ключа."""
        ordered = sorted(rows, key=key)
        return {
            name: sum(map(itemgetter(2), group), Decimal("0.00"))
            for name, group in groupby(ordered, key=key)
        }

    return {
        "categories": grouped_totals(itemgetter(1)),
        "months": grouped_totals(lambda row: row[0][:7]),
    }


def run_transactions() -> None:
    """Выполнить СРС 2 и проверить суммы независимо от группировки."""
    transactions: list[Transaction] = [
        ("2026-10-08", "Транспорт", Decimal("1000.00")),
        ("2026-09-02", "Продукты", Decimal("4500.50")),
        ("2026-10-03", "Учёба", Decimal("3200.00")),
        ("2026-09-03", "Транспорт", Decimal("800.00")),
        ("2026-09-15", "Продукты", Decimal("1250.25")),
        ("2026-10-01", "Продукты", Decimal("2000.00")),
        ("2026-09-19", "Учёба", Decimal("1500.00")),
    ]
    before = transactions.copy()
    result = expense_report(transactions)
    print("Исходные транзакции, тенге:")
    for row in transactions:
        print(f"{row[0]} | {row[1]} | {row[2]:.2f}")
    report_fields = [("По категориям", "categories"), ("По месяцам", "months")]
    for heading, field in report_fields:
        print(heading + ":")
        for name, total in result[field].items():
            print(f"  {name}: {total:.2f}")
    expected_categories = {
        "Продукты": Decimal("7750.75"),
        "Транспорт": Decimal("1800.00"),
        "Учёба": Decimal("4700.00"),
    }
    expected_months = {"2026-09": Decimal("8050.75"), "2026-10": Decimal("6200.00")}
    assert result == {
        "categories": expected_categories,
        "months": expected_months,
    }
    total = sum(map(itemgetter(2), transactions), Decimal("0.00"))
    assert total == Decimal("14250.75")
    assert sum(result["categories"].values()) == total
    assert sum(result["months"].values()) == total
    assert transactions == before
    assert expense_report([]) == {"categories": {}, "months": {}}
    years = [("2025-10-01", "A", Decimal("1")), ("2026-10-01", "A", Decimal("2"))]
    assert len(expense_report(years)["months"]) == 2
    for bad in [
        [("2026-02-30", "A", Decimal("1"))],
        [("2026-10-01", "", Decimal("1"))],
        [("2026-10-01", "A", Decimal("-1"))],
        [("2026-10-01", "A", Decimal("NaN"))],
    ]:
        try:
            expense_report(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("Некорректная транзакция не отклонена")
    print(f"Контрольный итог обоих отчётов: {total:.2f}")
    print("Проверены пустой вход, разные годы, неверная дата и сумма.")
    print("Исходный список не изменился.")


def compose2(f: Callable[[U], V], g: Callable[[T], U]) -> Callable[[T], V]:
    """Вернуть композицию f(g(x)); сначала применяется g."""

    def composed(value: T) -> V:
        """Выполнить правую функцию, затем левую."""
        return f(g(value))

    return composed


def identity(value: T) -> T:
    """Вернуть значение без изменения."""
    return value


def compose(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Объединить унарные функции справа налево; пустой набор даёт identity.

    Для произвольной цепочки типы промежуточных значений могут различаться.
    Аннотация Any здесь описывает этот общий интерфейс; вызывающий код
    должен передавать функции с совместимыми входами и выходами.
    """
    return reduce(compose2, funcs, identity)


def run_compose() -> None:
    """Выполнить СРС 3 и проверить порядок вызовов и пустую композицию."""

    def double(x: int) -> int:
        """Удвоить целое число."""
        return x * 2

    def plus_one(x: int) -> int:
        """Увеличить целое число на единицу."""
        return x + 1

    def square(x: int) -> int:
        """Возвести целое число в квадрат."""
        return x * x

    two = compose2(double, plus_one)
    many = compose(square, double, plus_one)
    print("compose2(double, plus_one)(3) =", two(3))
    print("compose(square, double, plus_one)(3) =", many(3))
    print("compose()(7) =", compose()(7))
    normalized = compose(str.upper, str.strip)("  map  ")
    print("compose(str.upper, str.strip)('  map  ') =", normalized)
    assert two(3) == 8 and many(3) == 64
    assert compose2(plus_one, double)(3) == 7
    assert compose()(7) == 7 and compose(plus_one)(7) == 8
    assert normalized == "MAP"
    assert compose(str, len, str.strip)("  ab  ") == "2"
    initial = [1, 2]
    assert compose()(initial) is initial
    calls: list[str] = []

    def first(x: int) -> int:
        """Отметить применение внешней функции."""
        calls.append("first")
        return x + 10

    def second(x: int) -> int:
        """Отметить применение внутренней функции."""
        calls.append("second")
        return x * 2

    assert compose(first, second)(3) == 16
    assert calls == ["second", "first"]
    print("Фактический порядок вызовов:", calls)


def make_json_encoder() -> Callable[[object], str]:
    """Построить singledispatch-кодировщик без глобального реестра.

    Контракт: конечные int/float, str, bool, None, ациклические list/tuple
    и dict со строковыми ключами. Строки экранируются стандартным json.dumps.
    Комплексные числа и специальные числовые классы не входят в контракт.
    """

    @singledispatch
    def to_json_like(value: object) -> str:
        """Отклонить тип, для которого не зарегистрирован обработчик."""
        raise TypeError(f"Неподдерживаемый тип: {type(value).__name__}")

    @to_json_like.register(type(None))
    def encode_none(value: None) -> str:
        """Представить отсутствие значения как null."""
        return "null"

    @to_json_like.register(bool)
    def encode_bool(value: bool) -> str:
        """Кодировать bool отдельно, поскольку bool является подклассом int."""
        return "true" if value else "false"

    @to_json_like.register(int)
    def encode_int(value: int) -> str:
        """Преобразовать целое число в десятичную запись."""
        return str(value)

    @to_json_like.register(float)
    def encode_float(value: float) -> str:
        """Преобразовать конечное вещественное число."""
        if not math.isfinite(value):
            raise ValueError("NaN и бесконечность не допускаются")
        return repr(value)

    @to_json_like.register(str)
    def encode_str(value: str) -> str:
        """Экранировать кавычки, обратные косые черты и управляющие символы."""
        return json.dumps(value, ensure_ascii=False)

    @to_json_like.register(list)
    @to_json_like.register(tuple)
    def encode_sequence(value: list[object] | tuple[object, ...]) -> str:
        """Рекурсивно кодировать список или кортеж как JSON-массив."""
        return "[" + ", ".join(map(to_json_like, value)) + "]"

    @to_json_like.register(dict)
    def encode_dict(value: dict[str, object]) -> str:
        """Рекурсивно кодировать словарь с проверкой строковых ключей."""
        if not all(isinstance(key, str) for key in value):
            raise TypeError("Ключи словаря должны быть строками")
        return (
            "{"
            + ", ".join(
                f"{to_json_like(key)}: {to_json_like(item)}"
                for key, item in value.items()
            )
            + "}"
        )

    return to_json_like


def run_json() -> None:
    """Выполнить СРС 4 и разобрать каждую полученную строку модулем json."""
    to_json_like = make_json_encoder()
    inputs: list[object] = [
        42,
        -3.5,
        'строка с "кавычками"\nи переносом',
        [1, "два", True],
        {"имя": "Виктория", "баллы": (95, 100), "сдано": True},
        (1, "x", None),
        [],
        {},
        (),
        False,
        None,
    ]
    for value in inputs:
        encoded = to_json_like(value)
        print(f"{type(value).__name__}: {encoded}")
        expected = json.loads(json.dumps(value, ensure_ascii=False))
        assert json.loads(encoded) == expected
    assert to_json_like(True) == "true"
    assert to_json_like(False) == "false" and to_json_like(None) == "null"
    nested = {"a": [1, {"b": (2, 3)}], "slash": "a\\b"}
    assert json.loads(to_json_like(nested)) == {
        "a": [1, {"b": [2, 3]}],
        "slash": "a\\b",
    }
    invalid_values = [
        {1: "x"},
        {1, 2},
        complex(1, 2),
        float("nan"),
        float("inf"),
    ]
    for invalid in invalid_values:
        try:
            to_json_like(invalid)
        except (TypeError, ValueError) as error:
            print(f"Отклонён {type(invalid).__name__}: {type(error).__name__}")
        else:
            raise AssertionError("Некорректное значение должно быть отклонено")
    print("Результаты разобраны json.loads.")
    print("Вложенность и экранирование проверены.")


def main() -> None:
    """Выбрать одну задачу СРС и выполнить её с проверками."""
    tasks: dict[str, Callable[[], None]] = {
        "transactions": run_transactions,
        "compose": run_compose,
        "json": run_json,
    }
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", choices=tasks)
    args = parser.parse_args()
    print(f"Лекция 04. СРС: {args.task}")
    tasks[args.task]()
    print("ПРОВЕРКИ ПРОЙДЕНЫ")


if __name__ == "__main__":
    main()
