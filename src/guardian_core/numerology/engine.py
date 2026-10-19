"""Deterministic numerology calculations (Hebrew gematria).

Formulas follow the Revital Cohen method as described in
sources/numerology/ ("מכניקת החישוב"). Everything here is pure arithmetic:
no AI, no knowledge-package lookups. Interpretation text lives elsewhere.

Assumptions not stated in the sources (flagged for review):
  * destiny path = digital root of every digit in the birth date;
  * final letters (ך ם ן ף ץ) take the value of their regular forms;
  * results reduce to 1-9 (no master-number retention).
"""
from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict

_GEMATRIA = {
    "א": 1, "ב": 2, "ג": 3, "ד": 4, "ה": 5, "ו": 6, "ז": 7, "ח": 8, "ט": 9,
    "י": 10, "כ": 20, "ל": 30, "מ": 40, "נ": 50, "ס": 60, "ע": 70, "פ": 80, "צ": 90,
    "ק": 100, "ר": 200, "ש": 300, "ת": 400,
    "ך": 20, "ם": 40, "ן": 50, "ף": 80, "ץ": 90,
}

HARMONIES = {
    "individual": (1, 5, 7),
    "framework": (2, 4, 8, 6),
    "universal": (3, 6, 9),
}


def reduce_number(value: int) -> int:
    """Digital root: 1-9 for positive input, 0 for 0."""
    if value < 0:
        raise ValueError("value must be non-negative")
    while value > 9:
        value = sum(int(d) for d in str(value))
    return value


def gematria(text: str) -> int:
    """Sum of Hebrew letter values; niqqud, spaces, punctuation and non-Hebrew are ignored."""
    return sum(_GEMATRIA.get(ch, 0) for ch in text)


class PersonalCycle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    year_classic: int
    year_extended: int
    month_extended: int
    day_extended: int


class NumerologyProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    destiny_path: int
    birth_day: int
    full_name_value: int
    full_name_number: int
    first_name_number: int
    power_number: int
    reduced_age: int
    cycle: PersonalCycle
    harmonies: list[str]


def _age(birth: date, today: date) -> int:
    return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))


def calculate_profile(*, birth_date: date, full_name: str, today: date | None = None) -> NumerologyProfile:
    today = today or date.today()
    if birth_date > today:
        raise ValueError("birth_date is in the future")
    name_value = gematria(full_name)
    if name_value == 0:
        raise ValueError("full_name must contain Hebrew letters")
    first_name = full_name.split()[0]

    destiny = reduce_number(sum(int(d) for d in f"{birth_date.day}{birth_date.month}{birth_date.year}"))
    age = reduce_number(_age(birth_date, today))
    year_classic = reduce_number(age + destiny)
    year_extended = reduce_number(year_classic + age)
    month_extended = reduce_number(year_classic + reduce_number(today.month))
    day_extended = reduce_number(month_extended + reduce_number(today.day))
    name_number = reduce_number(name_value)

    present = {destiny, reduce_number(birth_date.day), name_number}
    harmonies = [name for name, members in HARMONIES.items() if len(present & set(members)) >= 2]

    return NumerologyProfile(
        destiny_path=destiny,
        birth_day=reduce_number(birth_date.day),
        full_name_value=name_value,
        full_name_number=name_number,
        first_name_number=reduce_number(gematria(first_name)),
        power_number=reduce_number(name_value + destiny),
        reduced_age=age,
        cycle=PersonalCycle(
            year_classic=year_classic,
            year_extended=year_extended,
            month_extended=month_extended,
            day_extended=day_extended,
        ),
        harmonies=harmonies,
    )
