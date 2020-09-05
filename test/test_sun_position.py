import pytest

from sun_position import hour_to_time, day_to_time, JD


@pytest.mark.parametrize(
    'hours,hours_minutes_seconds',
    [
        (1, (1, 0, 0)),
        (1.5, (1, 30, 0)),
        (1.54, (1, 32, 24)),
        (1.0/3, (0, 20, 0))
    ]
)
def test_hour_to_time(hours, hours_minutes_seconds):
    assert hour_to_time(hours) == hours_minutes_seconds


@pytest.mark.parametrize(
    'days,days_hours_minutes_seconds',
    [
        (1, (1, 0, 0, 0)),
        (1.5, (1, 12, 0, 0)),
        (1.54, (1, 12, 57, 36)),
        (1.0/3, (0, 8, 0, 0))
    ]
)
def test_day_to_time(days, days_hours_minutes_seconds):
    assert day_to_time(days) == days_hours_minutes_seconds


@pytest.mark.parametrize(
    'year,month,day,hour,minute,julian_date',
    [
        (0, 0, 0, 0, 0, 1721024.5),
        (1, 2, 3, 4, 5, 1721456.670138889),
        (2020, 4, 30, 12, 0, 2458970.0)
    ]
)
def test_JD(year, month, day, hour, minute, julian_date):
    assert JD(year, month, day, hour, minute) == julian_date
