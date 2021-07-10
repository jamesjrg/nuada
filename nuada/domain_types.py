from dataclasses import dataclass
from enum import Enum, IntEnum, auto
from typing import List


class DayOfWeek(IntEnum):
    mon = auto()
    tue = auto()
    wed = auto()
    thu = auto()
    fri = auto()
    sat = auto()
    sun = auto()
    more_than_one = auto()


class Budget(IntEnum):
    fifty_pounds_per_day = auto()
    one_hundred_pounds_per_day = auto()
    one_hundred_fifty_pounds_per_day = auto()
    two_hundred_fifty_pounds_per_day = auto()


class Month(IntEnum):
    jan = 1
    feb = 2
    mar = 3
    apr = 4
    may = 5
    jun = 6
    jul = 7
    aug = 8
    sep = 9
    oct = 10
    nov = 11
    dec = 12


class WindsurfForecast(IntEnum):
    almost_none = auto()
    bobbing_about = auto()
    planing = auto()
    too_much = auto()


class SurfForecast(IntEnum):
    no_surf = auto()
    small_surf = auto()
    big_surf = auto()


class Weather(IntEnum):
    heavy_rain = auto()
    overcast_with_showers = auto()
    sun_with_showers = auto()
    sunny = auto()


class Temperature(Enum):
    one_or_less = auto()
    two_to_six = auto()
    seven_to_ten = auto()
    ten_to_fourteen = auto()
    fifteen_to_nineteen = auto()
    twenty_to_twenty_four = auto()
    twenty_five_plus = auto()


@dataclass
class Requirements:
    data: List[str]


@dataclass
class Activity:
    name: str
    ideally: Requirements
    really: Requirements
    ideal_score: int
    really_score: int
    notes: List[str]
