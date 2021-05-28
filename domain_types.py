from dataclasses import dataclass
from enum import Enum, IntEnum, auto
from typing import List, Dict


class TimeAvailable(IntEnum):
    an_hour = auto()
    two_hours = auto()
    four_hours = auto()
    evening = auto()
    all_day = auto()
    all_weekend = auto()
    four_days = auto()
    one_week_plus = auto()

class HowFarPlanningAhead(Enum):
    today = auto()
    tomorrow = auto()
    this_week = auto()
    next_week = auto()
    months_ahead = auto()

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

class CovidSituation(IntEnum):
    lockdown = auto()
    tier_three = auto()
    allowed_to_meet_inside = auto()
    freedom = auto()

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

class Snowiness(IntEnum):
    no_snow = auto()
    dusting = auto()
    lots = auto()

class TiredOrInjuredness(IntEnum):
    no_problems = auto()
    pretty_tired_or_niggling_injury = auto()
    really_tired = auto()
    properly_injured = auto()


class Suitablility(IntEnum):
    no = auto()
    i_guess_i_could_do = auto()
    yeah = auto()
    yay = auto()

class Temperature(Enum):
    one_or_less = auto()
    two_to_six = auto()
    seven_to_ten = auto()
    ten_to_fourteen = auto()
    fifteen_to_nineteen = auto()
    twenty_to_twenty_four = auto()
    twenty_five_plus = auto()

@dataclass
class Result:
    suitability: Suitablility
    notes: List[str]

@dataclass
class Forecast:
    wind: WindsurfForecast
    surf: SurfForecast
    sun_and_rain: Weather
    temperature: Temperature
    snowiness: Snowiness

@dataclass()
class WebData:
    bristol: Forecast
    porthcawl: Forecast
    woolacombe: Forecast
    brecon: Forecast
    llanberis: Forecast
    keswick: Forecast
    fort_william: Forecast
    poole: Forecast
    truro: Forecast
    newquay: Forecast
    weymouth: Forecast
    aviemore: Forecast
    axbridge: Forecast
    llandegfedd: Forecast
    weston: Forecast


@dataclass
class Input:
    time_available: TimeAvailable
    how_far_ahead: HowFarPlanningAhead
    day: DayOfWeek
    month: Month
    budget: Budget
    covid: CovidSituation
    forecasts: WebData
    legs: TiredOrInjuredness
    arms: TiredOrInjuredness