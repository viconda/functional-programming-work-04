"""Запустить все 72 практических пункта и сохранить фактические протоколы."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COMMANDS = (
    ("L01", ("lecture/examples.py", "01")),
    ("L02", ("lecture/examples.py", "02")),
    ("L03", ("lecture/examples.py", "03")),
    ("L04", ("lecture/examples.py", "04")),
    ("L05", ("lecture/examples.py", "05")),
    ("L06", ("lecture/examples.py", "06")),
    ("L07", ("lecture/examples.py", "07")),
    ("L08", ("lecture/examples.py", "08")),
    ("L09", ("lecture/examples.py", "09")),
    ("L10", ("lecture/examples.py", "10")),
    ("L11", ("lecture/examples.py", "11")),
    ("L12", ("lecture/examples.py", "12")),
    ("L13", ("lecture/examples.py", "13")),
    ("L14", ("lecture/examples.py", "14")),
    ("L15", ("lecture/examples.py", "15")),
    ("S1_01", ("lecture/itertools_reference.py", "count")),
    ("S1_02", ("lecture/itertools_reference.py", "cycle")),
    ("S1_03", ("lecture/itertools_reference.py", "repeat")),
    ("S1_04", ("lecture/itertools_reference.py", "accumulate")),
    ("S1_05", ("lecture/itertools_reference.py", "chain")),
    ("S1_06", ("lecture/itertools_reference.py", "compress")),
    ("S1_07", ("lecture/itertools_reference.py", "dropwhile")),
    ("S1_08", ("lecture/itertools_reference.py", "takewhile")),
    ("S1_09", ("lecture/itertools_reference.py", "filterfalse")),
    ("S1_10", ("lecture/itertools_reference.py", "groupby")),
    ("S1_11", ("lecture/itertools_reference.py", "islice")),
    ("S1_12", ("lecture/itertools_reference.py", "pairwise")),
    ("S1_13", ("lecture/itertools_reference.py", "starmap")),
    ("S1_14", ("lecture/itertools_reference.py", "tee")),
    ("S1_15", ("lecture/itertools_reference.py", "zip_longest")),
    ("S1_16", ("lecture/itertools_reference.py", "batched")),
    ("S1_17", ("lecture/itertools_reference.py", "product")),
    ("S1_18", ("lecture/itertools_reference.py", "permutations")),
    ("S1_19", ("lecture/itertools_reference.py", "combinations")),
    ("S1_20", ("lecture/itertools_reference.py", "combinations_with_replacement")),
    ("S2", ("lecture/coursework.py", "transactions")),
    ("S3", ("lecture/coursework.py", "compose")),
    ("S4", ("lecture/coursework.py", "json")),
    ("0.1", ("lab04/core/task00.py", "1")),
    ("0.2", ("lab04/core/task00.py", "2")),
    ("0.3", ("lab04/core/task00.py", "3")),
    ("0.4", ("lab04/core/task00.py", "4")),
    ("1", ("lab04/core/task01.py",)),
    ("2.1", ("lab04/core/task02.py", "1")),
    ("2.2", ("lab04/core/task02.py", "2")),
    ("2.3", ("lab04/core/task02.py", "3")),
    ("2.4", ("lab04/core/task02.py", "4")),
    ("2.5", ("lab04/core/task02.py", "5")),
    ("2.6", ("lab04/core/task02.py", "6")),
    ("2.7", ("lab04/core/task02.py", "7")),
    ("3", ("lab04/core/task03.py",)),
    ("4.1", ("lab04/core/task04.py", "1")),
    ("4.2", ("lab04/core/task04.py", "2")),
    ("4.3", ("lab04/core/task04.py", "3")),
    ("5.1", ("lab04/core/task05.py", "1")),
    ("5.2", ("lab04/core/task05.py", "2")),
    ("5.3", ("lab04/core/task05.py", "3")),
    ("5.4", ("lab04/core/task05.py", "4")),
    ("5.5", ("lab04/core/task05.py", "5")),
    ("5.6", ("lab04/core/task05.py", "6")),
    ("5.7", ("lab04/core/task05.py", "7")),
    ("5.8", ("lab04/core/task05.py", "8")),
    ("5.9", ("lab04/core/task05.py", "9")),
    ("5.10", ("lab04/core/task05.py", "10")),
    ("task06_data", ("lab04/variant03/task06.py", "--part", "data")),
    ("task06_differences", ("lab04/variant03/task06.py", "--part", "diffs")),
    ("task06_months", ("lab04/variant03/task06.py", "--part", "months")),
    ("task06_peaks", ("lab04/variant03/task06.py", "--part", "months")),
    ("task06_checks", ("lab04/variant03/task06.py", "--part", "checks")),
    ("extra_windows", ("lab04/extra/extra.py", "--part", "windows")),
    ("extra_groupby", ("lab04/extra/extra.py", "--part", "groups")),
    ("extra_timeit", ("lab04/extra/extra.py", "--part", "benchmark")),
)


def run_one(item: tuple[str, tuple[str, ...]]) -> int:
    """Запустить один пункт, напечатать вывод и записать его в журнал."""
    name, arguments = item
    env = {**os.environ, "PYTHONUTF8": "1"}
    process = subprocess.run(
        [sys.executable, *arguments],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    result = process.stdout + process.stderr
    print(f"\n=== {name}: python {' '.join(arguments)} ===")
    print(result, end="" if result.endswith("\n") else "\n")
    output = ROOT / "verification" / "runs"
    output.mkdir(parents=True, exist_ok=True)
    (output / f"{name}.txt").write_text(result, encoding="utf-8")
    if process.returncode:
        print(f"ОШИБКА: код завершения {process.returncode}")
    return int(process.returncode != 0)


def main() -> None:
    """Выполнить весь комплект, завершиться ненулевым кодом при ошибке."""
    failures = sum(map(run_one, COMMANDS))
    print(f"\nИТОГ: {len(COMMANDS) - failures}/{len(COMMANDS)} запусков успешны.")
    raise SystemExit(int(failures != 0))


if __name__ == "__main__":
    main()
