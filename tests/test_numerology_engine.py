from datetime import date

import pytest

from guardian_core.numerology import calculate_profile, gematria, reduce_number


def test_reduce_number():
    assert reduce_number(0) == 0
    assert reduce_number(9) == 9
    assert reduce_number(10) == 1
    assert reduce_number(29) == 2
    assert reduce_number(999) == 9


def test_gematria_values_and_final_letters():
    assert gematria("אבג") == 6
    assert gematria("שלום") == 300 + 30 + 6 + 40
    assert gematria("ך") == gematria("כ")
    assert gematria("hello, שָׁלוֹם") == gematria("שלום")  # non-Hebrew and niqqud ignored


def test_destiny_path_and_cycles_match_worked_example():
    # 15.03.1990: 1+5+0+3+1+9+9+0 = 28 -> 1
    profile = calculate_profile(birth_date=date(1990, 3, 15), full_name="דנה לוי", today=date(2026, 10, 19))
    assert profile.destiny_path == 1
    assert profile.birth_day == 6
    assert profile.reduced_age == 9  # age 36 -> 9
    assert profile.full_name_value == 105  # דנה=59, לוי=46
    assert profile.full_name_number == 6
    assert profile.power_number == 7  # 105 + 1 = 106 -> 7
    assert profile.cycle.year_classic == 1  # 9 + 1 = 10
    assert profile.cycle.year_extended == 1  # 1 + 9 = 10
    assert profile.cycle.month_extended == 2  # Oct: 1 + 1
    assert profile.cycle.day_extended == 3  # 19 -> 1: 2 + 1


def test_age_respects_birthday_not_yet_reached():
    before = calculate_profile(birth_date=date(1990, 12, 31), full_name="דנה", today=date(2026, 10, 19))
    assert before.reduced_age == 8  # age 35


def test_harmony_detected_when_two_numbers_share_a_group():
    # 5.4.1990: destiny 1, birth day 5, both in individual (1,5,7)
    profile = calculate_profile(birth_date=date(1990, 4, 5), full_name="דנה", today=date(2026, 10, 19))
    assert "individual" in profile.harmonies


def test_invalid_input_rejected():
    with pytest.raises(ValueError):
        calculate_profile(birth_date=date(2030, 1, 1), full_name="דנה", today=date(2026, 10, 19))
    with pytest.raises(ValueError):
        calculate_profile(birth_date=date(1990, 1, 1), full_name="Dana", today=date(2026, 10, 19))
