"""Задание 0. Чистая свёртка банковских операций и её инварианты."""

import sys
from decimal import Decimal
from functools import partial, reduce
from itertools import accumulate, groupby
from operator import attrgetter
from typing import NamedTuple


class Tx(NamedTuple):
    """Неизменяемая банковская операция; суммы указаны в тенге."""

    date: str
    client: str
    kind: str
    amount: Decimal
    target: str | None = None


State = tuple[dict[str, Decimal], list[Tx]]


def journal() -> tuple[Tx, ...]:
    """Вернуть исходные шесть операций из условия."""
    return (
        Tx("2026-10-01", "Айдос", "deposit", Decimal("50000")),
        Tx("2026-10-01", "Дана", "deposit", Decimal("120000")),
        Tx("2026-10-02", "Айдос", "withdraw", Decimal("15000")),
        Tx("2026-10-02", "Дана", "transfer", Decimal("30000"), "Айдос"),
        Tx("2026-10-03", "Тимур", "deposit", Decimal("70000")),
        Tx("2026-10-03", "Айдос", "transfer", Decimal("5000"), "Тимур"),
    )


def commission(amount: Decimal) -> Decimal:
    """Вычислить 1 % суммы, минимум 100 тг; округлить до тиына."""
    return max(amount * Decimal("0.01"), Decimal("100")).quantize(Decimal("0.01"))


def apply_tx(state: State, tx: Tx, *, fees: bool = True) -> State:
    """Вернуть новые балансы и отклонения, не изменяя входную пару."""
    balances, rejected = state
    if tx.kind not in ("deposit", "withdraw", "transfer") or tx.amount <= 0:
        raise ValueError("Некорректный тип или неположительная сумма")
    if tx.kind == "transfer" and (tx.target is None or tx.target == "BANK"):
        raise ValueError("Переводу нужен клиент-получатель")
    balance = balances.get(tx.client, Decimal(0))
    fee = commission(tx.amount) if fees and tx.kind == "transfer" else Decimal(0)
    if tx.kind != "deposit" and balance < tx.amount + fee:
        return dict(balances), rejected + [tx]
    delta = tx.amount if tx.kind == "deposit" else -(tx.amount + fee)
    updated = {**balances, tx.client: balance + delta}
    if tx.kind == "transfer":
        assert tx.target is not None
        updated = {
            **updated,
            tx.target: updated.get(tx.target, Decimal(0)) + tx.amount,
        }
        if fees:
            updated = {**updated, "BANK": updated.get("BANK", Decimal(0)) + fee}
    return updated, rejected


def external_delta(tx: Tx) -> Decimal:
    """Вклад принятой операции в общую денежную массу."""
    return {"deposit": tx.amount, "withdraw": -tx.amount, "transfer": Decimal(0)}[
        tx.kind
    ]


def example_analysis(log: tuple[Tx, ...]) -> tuple[object, ...]:
    """Повторить остальные четыре анализа исходного примера без циклов."""
    turnover = dict(
        map(
            lambda pair: (pair[0], sum(map(attrgetter("amount"), pair[1]))),
            groupby(sorted(log, key=attrgetter("kind")), attrgetter("kind")),
        )
    )
    daily = tuple(
        map(
            lambda pair: (pair[0], sum(map(attrgetter("amount"), pair[1]))),
            groupby(sorted(log, key=attrgetter("date")), attrgetter("date")),
        )
    )
    running = tuple(
        zip(map(lambda row: row[0], daily), accumulate(map(lambda row: row[1], daily)))
    )
    largest = dict(
        map(
            lambda pair: (pair[0], max(map(attrgetter("amount"), pair[1]))),
            groupby(sorted(log, key=attrgetter("client")), attrgetter("client")),
        )
    )
    pairs = tuple(
        sorted(
            map(
                attrgetter("client", "target"),
                filter(lambda tx: tx.kind == "transfer", log),
            )
        )
    )
    mutual = tuple(
        filter(lambda pair: pair[0] < pair[1] and (pair[1], pair[0]) in pairs, pairs)
    )
    return turnover, running, largest, pairs, mutual


def show(section: int, *values: object) -> None:
    """Вывести выбранный подпункт; проверки выполняются для всего задания."""
    if len(sys.argv) == 1 or section == 0 or int(sys.argv[1]) == section:
        print(*values)


def main() -> None:
    """Продемонстрировать каждый пункт и проверить граничные случаи."""
    log = journal()
    snapshot = tuple(log)
    initial: State = ({}, [])
    plain, plain_rejected = reduce(partial(apply_tx, fees=False), log, initial)
    assert plain == {"Айдос": 60000, "Дана": 90000, "Тимур": 75000}
    assert sum(plain.values()) == sum(map(external_delta, log)) == 225000
    assert plain_rejected == []
    turnover, running, largest, pairs, mutual = example_analysis(log)
    assert turnover == {"deposit": 240000, "transfer": 35000, "withdraw": 15000}
    assert running == (
        ("2026-10-01", 170000),
        ("2026-10-02", 215000),
        ("2026-10-03", 290000),
    )
    assert largest == {"Айдос": 50000, "Дана": 120000, "Тимур": 70000}
    assert pairs == (("Айдос", "Тимур"), ("Дана", "Айдос"))
    assert mutual == ()
    show(1, "Оборот по типам:", turnover)
    show(1, "Накопительный оборот:", running)
    show(1, "Крупнейшие операции:", largest)
    show(1, "Направленные переводы:", pairs)
    show(1, "Взаимные пары:", mutual, "; обратных переводов в журнале нет.")
    show(1, "0.1. Без комиссии:", plain)
    show(1, "Инвариант: сумма балансов = 240000 - 15000 = 225000 тг.")

    charged, rejected = reduce(apply_tx, log, initial)
    assert charged == {"Айдос": 59900, "Дана": 89700, "Тимур": 75000, "BANK": 400}
    assert rejected == []
    assert commission(Decimal("30000")) == 300
    assert commission(Decimal("5000")) == 100
    assert commission(Decimal("10000")) == 100
    assert sum(charged.values()) == 225000
    assert sum(charged.values()) - charged["BANK"] == 224600
    assert log == snapshot and initial == ({}, [])
    show(2, "0.2. С комиссией:", charged)
    show(2, "Комиссии переводов: 300 + 100 = 400 тг.")
    show(3, "0.3. Клиенты 224600 + BANK 400 = 225000; входы не изменены.")

    excess = Tx("2026-10-04", "Айдос", "withdraw", Decimal("100000"))
    fee_excess = Tx("2026-10-04", "Айдос", "transfer", Decimal("59900"), "Дана")
    extended = log + (excess, fee_excess)
    final, rejected = reduce(apply_tx, extended, initial)
    assert final == charged and rejected == [excess, fee_excess]
    assert sum(final.values()) == 225000
    assert extended == log + (excess, fee_excess) and log == snapshot
    before: State = ({"А": Decimal("10000")}, [])
    self_tx = Tx("2026-10-04", "А", "transfer", Decimal("1000"), "А")
    after = apply_tx(before, self_tx)
    assert before == ({"А": Decimal("10000")}, [])
    assert after == ({"А": Decimal("9900"), "BANK": Decimal("100")}, [])
    assert reduce(apply_tx, (), ({}, [])) == ({}, [])
    show(4, "0.4. Снятие 100000 тг отклонено: баланс Айдоса 59900 тг.")
    show(4, "Перевод 59900 тг тоже отклонён: не хватает 599 тг комиссии.")
    show(4, "Отклонённых операций:", len(rejected), "; балансы сохранены.")
    show(4, "Принятые пополнения - принятые снятия = 225000 тг.")
    show(0, "PASS: assert; пустой журнал, перевод себе, комиссия, неизменность.")


if __name__ == "__main__":
    main()
