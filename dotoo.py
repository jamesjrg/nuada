import asyncio
from datetime import date, timedelta

from domain_types import Input, Weather, TimeAvailable, Budget, Suitablility, Result, \
    TiredOrInjuredness, HowFarPlanningAhead, DayOfWeek, Month, Forecast

from collect_data import collect_web_data

example_usage = """

all day, for today:

python dotoo.py \
all_day today ignored ignored one_hundred_fifty_pounds_per_day tier_three \
no_problems no_problems

all day, for later this week:

python dotoo.py \
all_day this_week thu jan one_hundred_fifty_pounds_per_day tier_three \
really_tired no_problems

for this weekend:

python dotoo.py \
all_weekend this_week more_than_one jan one_hundred_fifty_pounds_per_day tier_three \
no_problems no_problems


"""

TODO = """
- sunny in evening should use sunset and sunrise times instead of month of year
- cold and wet should depend on actual temp and possibly also humidity from forecast not time of year
- use clevedon tide times to suggest when to swim in the sea
- use wind forecasts and tides times to predict when and where to windsurf
- use surf forecasts to predict when and where to surf
- use MWIS and met office to predict when to head to the mountains
- make checks for local activities (slackline etc) adjust location used if I am away from Bristol for a bit
"""

import fire
from typing import List, Tuple

def its_cold_and_wet(forecast: Forecast):
    return (
            forecast.sun_and_rain == Weather.heavy_rain
            or (forecast.sun_and_rain == Weather.overcast_with_showers and not (Month.mar <= inp.month <= Month.oct)))

def evening_is_bright_and_fairly_dry(forecast: Forecast):
    return (
            forecast.sun_and_rain in (Weather.sun_with_showers, Weather.sunny)
            and Month.apr <= forecast.month <= Month.sep)

def evening_or_all_day(inp: Input):
    return inp.time_available in (TimeAvailable.all_day, TimeAvailable.evening)


def can_afford_hotel_one_night(inp: Input):
    return inp.budget >= Budget.one_hundred_pounds_per_day

def can_afford_hotel_every_night(inp: Input):
    return inp.budget >= Budget.one_hundred_fifty_pounds_per_day

def can_afford_cheap_guided_holiday(inp: Input):
    return inp.budget >= Budget.one_hundred_fifty_pounds_per_day

def can_afford_expensive_guided_holiday(inp: Input):
    return inp.budget >= Budget.two_hundred_fifty_pounds_per_day


class Activities:
    def swim_indoors(self, inp: Input):
        lesson_notes = ["Get lessons?"]

        if its_cold_and_wet(inp) and inp.time_available < TimeAvailable.all_weekend:
            return Result(Suitablility.yeah, ["It's cold and damp and not much time"] + lesson_notes)

        if inp.time_available == TimeAvailable.an_hour:
            return Result(Suitablility.yeah, ["Not much time for other stuff"] + lesson_notes)

        return Result(Suitablility.i_guess_i_could_do, lesson_notes)

    def swim_in_sea_or_marine_lake(self, inp: Input):
        if (inp.arms >= TiredOrInjuredness.really_tired):
            return Result(Suitablility.no, ["i am weak"])

        if not its_cold_and_wet(inp.forecasts.bristol) and inp.time_available <= TimeAvailable.all_day:
            return Result(Suitablility.yeah, [])

        return Result(Suitablility.no, ["It's cold and damp"])

    def indoor_bouldering_or_autobelay(self, inp: Input):
        if (inp.arms >= TiredOrInjuredness.really_tired):
            return Result(Suitablility.no, ["i am weak"])

        if (inp.time_available < TimeAvailable.two_hours):
            return Result(Suitablility.no, ["not enough time"])

        if its_cold_and_wet(inp.forecasts.bristol) and inp.time_available < TimeAvailable.all_weekend:
            return Result(Suitablility.yeah, [])
        
        return Result(Suitablility.i_guess_i_could_do, [])

    def indoor_partnered_climbing(self, inp: Input):
        if (inp.arms >= TiredOrInjuredness.really_tired):
            return Result(Suitablility.no, ["i am weak"])

        if (inp.how_far_ahead in (HowFarPlanningAhead.this_week, HowFarPlanningAhead.next_week)
                and evening_or_all_day(inp)):
            return Result(Suitablility.yeah, ["Could try to find a climbing partner"])

        if (evening_or_all_day(inp)
                and not evening_is_bright_and_fairly_dry(inp.forecasts.bristol)):
            return Result(Suitablility.yeah, [])

        return Result(Suitablility.i_guess_i_could_do, [])

    def climb_outside_with_a_partner(self, inp: Input):
        if inp.arms == TiredOrInjuredness.properly_injured:
            return Result(Suitablility.no, ["i am weak"])

        if inp.time_available in (TimeAvailable.an_hour, TimeAvailable.two_hours):
            return Result(Suitablility.no, ["Not enough time"])

        if (evening_is_bright_and_fairly_dry(inp.forecasts.bristol)
                and (inp.day == DayOfWeek.wed or inp.how_far_ahead == HowFarPlanningAhead.this_week)
                and evening_or_all_day(inp)):
            return Result(Suitablility.yeah, [])

        if its_cold_and_wet(inp.forecasts.bristol):
            return Result(Suitablility.no, ["cold and wet"])

        return Result(Suitablility.i_guess_i_could_do, [])

    def climb_outside_on_own_bouldering_or_self_belay(self, inp: Input):
        if (inp.arms >= TiredOrInjuredness.really_tired):
            return Result(Suitablility.no, ["i am weak"])

        if its_cold_and_wet(inp.forecasts.bristol):
            return Result(Suitablility.no, ["cold and wet"])

        if inp.time_available == TimeAvailable.evening and not evening_is_bright_and_fairly_dry(inp.forecasts.bristol):
            return Result(Suitablility.no, ["evening isn't bright and dry"])

        if inp.time_available in (TimeAvailable.an_hour, TimeAvailable.two_hours):
            return Result(Suitablility.no, ["not enough time"])

        if inp.time_available <= TimeAvailable.four_hours:
            return Result(Suitablility.yeah, [])

        return Result(Suitablility.i_guess_i_could_do, [])

    def slackline(self, inp: Input):
        if its_cold_and_wet(inp.forecasts.bristol):
            return Result(Suitablility.no, ["cold and wet"])

        if inp.time_available == TimeAvailable.evening and not evening_is_bright_and_fairly_dry(inp.forecasts.bristol):
            return Result(Suitablility.no, ["evening isn't bright and dry"])

        if inp.time_available == TimeAvailable.an_hour:
            return Result(Suitablility.no, ["not enough time"])

        if inp.time_available in (TimeAvailable.two_hours, TimeAvailable.evening, TimeAvailable.all_day):
            return Result(Suitablility.yeah, [])

        return Result(Suitablility.i_guess_i_could_do, [])

    def kayak_holiday(self, inp: Input):
        if inp.time_available < TimeAvailable.all_weekend:
            return Result(Suitablility.no, ["Time available"])

        if not Month.mar <= inp.month <= Month.oct:
            return Result(Suitablility.no, ["Time of year"])

        return Result(Suitablility.i_guess_i_could_do, [])

    def kayak_with_kayak_club(self, inp: Input):
        return Result(Suitablility.i_guess_i_could_do, [])

    def sail_at_axbridge(self, inp: Input):
        if inp.forecasts.axbridge.sun_and_rain == Weather.heavy_rain:
            return Result(Suitablility.no, ["heavy rain"])

        return Result(Suitablility.i_guess_i_could_do, [])

    def sail_in_southern_england(self, inp: Input):
        if inp.forecasts.weymouth.sun_and_rain == Weather.heavy_rain:
            return Result(Suitablility.no, ["heavy rain"])

        return Result(Suitablility.i_guess_i_could_do, [])

    def windsurf_at_axbridge(self, inp: Input):
        if inp.forecasts.axbridge.sun_and_rain == Weather.heavy_rain:
            return Result(Suitablility.no, ["heavy rain"])

        return Result(Suitablility.i_guess_i_could_do, [])

    def windsurf_uk(self, inp: Input):
        return Result(Suitablility.i_guess_i_could_do, [])

    def windsurf_abroad(self, inp: Input):
        if inp.time_available < TimeAvailable.one_week_plus:
            return Result(Suitablility.no, ["not enough time"])

        return Result(Suitablility.i_guess_i_could_do, [])

    def surf_uk(self, inp: Input):
        if inp.sun_and_rain == Weather.heavy_rain:
            return Result(Suitablility.no, ["heavy rain"])

        return Result(Suitablility.i_guess_i_could_do, [])

    def skiing(self, inp: Input):
        if inp.time_available < TimeAvailable.one_week_plus:
            return Result(Suitablility.no, ["not enough time"])

        return Result(Suitablility.i_guess_i_could_do, ["downhill, ski touring, cross country"])

    def road_bike_locally(self, inp: Input):
        if inp.legs >= TiredOrInjuredness.really_tired:
            return Result(Suitablility.no, ["tired"])

        if not its_cold_and_wet(inp.forecasts.bristol):
            return Result(Suitablility.yeah, [])

        if inp.forecasts.bristol.sun_and_rain == Weather.heavy_rain:
            return Result(Suitablility.no, ["heavy rain"])

        return Result(Suitablility.i_guess_i_could_do, [])

    def road_bike_further_afield(self, inp: Input):
        if inp.legs >= TiredOrInjuredness.really_tired:
            return Result(Suitablility.no, ["tired"])

        if inp.time_available < TimeAvailable.all_day:
            return Result(Suitablility.no, ["not enough time"])
        return Result(Suitablility.i_guess_i_could_do, [])

    def cycle_touring(self, inp: Input):
        if its_cold_and_wet(inp):
            return Result(Suitablility.no, ["cold and wet"])

        if inp.sun_and_rain == Weather.heavy_rain:
            return Result(Suitablility.no, ["heavy rain"])

        if inp.time_available < TimeAvailable.all_weekend:
            return Result(Suitablility.no, ["not enough time"])
        return Result(Suitablility.i_guess_i_could_do, [])

    def orienteering_virtual_course(self, inp: Input):
        if inp.legs >= TiredOrInjuredness.really_tired:
            return Result(Suitablility.no, ["tired"])

        if (inp.time_available > TimeAvailable.all_day
                or inp.time_available < TimeAvailable.two_hours):
            return Result(Suitablility.no, ["unsuitable amount of time"])

        return Result(Suitablility.i_guess_i_could_do, [])

    def orienteering_event(self, inp: Input):
        return Result(Suitablility.i_guess_i_could_do, [])

    def ten_k_run_on_own(self, inp: Input):
        if inp.legs >= TiredOrInjuredness.really_tired:
            return Result(Suitablility.no, ["tired"])

        if not its_cold_and_wet(inp.forecasts.bristol):
            return Result(Suitablility.yeah, [])

        return Result(Suitablility.i_guess_i_could_do, [])

    def long_run_walk_on_own(self, inp: Input):
        if inp.time_available < TimeAvailable.four_hours:
            return Result(Suitablility.no, ["not enough time"])

        if inp.legs != TiredOrInjuredness.no_problems:
            return Result(Suitablility.no, ["too tired or injured"])

        if not its_cold_and_wet(inp.forecasts.bristol):
            return Result(Suitablility.yeah, [])

        return Result(Suitablility.i_guess_i_could_do, [])

    def run_with_local_running_club(self, inp: Input):
        if inp.legs >= TiredOrInjuredness.really_tired:
            return Result(Suitablility.no, ["tired"])

        if not evening_or_all_day(inp):
            return Result(Suitablility.no, ["not enough time"])

        if inp.day == DayOfWeek.sat:
            return Result(Suitablility.yeah, ["parkrun"])

        if inp.day == DayOfWeek.tue:
            return Result(Suitablility.yeah, ["bok or TACH"])

        if inp.day == DayOfWeek.thu:
            return Result(Suitablility.yeah, ["TACH"])

        if inp.day in [DayOfWeek.wed, DayOfWeek.sun]:
            return Result(Suitablility.yeah, ["LARG"])

        return Result(Suitablility.no, ["Wrong day"])

    def organise_micro_tach(self, inp: Input):
        if inp.time_available < TimeAvailable.evening:
            return Result(Suitablility.no, ["time available"])

        if inp.how_far_ahead == HowFarPlanningAhead.today:
            return Result(Suitablility.no, ["can't organise run for today"])

        return Result(Suitablility.i_guess_i_could_do, [])

    def study_first_aid_or_ropework(self, inp: Input):
        return Result(Suitablility.i_guess_i_could_do, [])

    def read_a_book_or_watch_tv(self, inp: Input):
        if (inp.time_available > TimeAvailable.two_hours):
            return Result(Suitablility.no, [])

        return Result(Suitablility.i_guess_i_could_do, [])

    def practice_guitar(self, inp: Input):
        return Result(Suitablility.i_guess_i_could_do, [])

    def learn_to_cook(self, inp: Input):
        return Result(Suitablility.i_guess_i_could_do, [])

    def walk_with_a_meetup_group(self, inp: Input):
        if (inp.time_available < TimeAvailable.all_day):
            return Result(Suitablility.no, [])

        return Result(Suitablility.i_guess_i_could_do, [])

    def surf_with_a_meetup_group(self, inp: Input):
        if (inp.time_available < TimeAvailable.all_day):
            return Result(Suitablility.no, [])

        return Result(Suitablility.i_guess_i_could_do, [])

    def nav_practice_in_brecons(self, inp: Input):
        if inp.legs >= TiredOrInjuredness.really_tired:
            return Result(Suitablility.no, ["tired"])

        return Result(Suitablility.i_guess_i_could_do, [])

    def big_run_or_walk_in_actual_mountains(self, inp: Input):
        if inp.time_available <= TimeAvailable.all_weekend:
            return Result(Suitablility.no, ["not enough time"])

        if inp.sun_and_rain == Weather.sunny:
            return Result(Suitablility.yeah, [])

        return Result(Suitablility.i_guess_i_could_do, [])

    def scrambling_in_the_mountains(self, inp: Input):
        if inp.time_available <= TimeAvailable.all_weekend:
            return Result(Suitablility.no, ["not enough time"])

        if its_cold_and_wet(inp):
            return Result(Suitablility.no, ["cold and wet"])

        if inp.sun_and_rain == Weather.sunny:
            return Result(Suitablility.yeah, [])

        return Result(Suitablility.i_guess_i_could_do, [])

    def bristol_con_vol(self, inp: Input):
        if inp.time_available < TimeAvailable.all_day:
            return Result(Suitablility.no, ["not enough time"])

        return Result(Suitablility.i_guess_i_could_do, [])

    def con_vol_holiday(self, inp: Input):
        if inp.time_available <= TimeAvailable.all_weekend:
            return Result(Suitablility.no, ["not enough time"])

        return Result(Suitablility.i_guess_i_could_do, [])

    def yoga_or_fitness_class(self, inp: Input):
        return Result(Suitablility.i_guess_i_could_do, [])

    def home_fitness_workout(self, inp: Input):
        return Result(Suitablility.i_guess_i_could_do, [])

    def short_local_walk(self, inp: Input):
        return Result(Suitablility.i_guess_i_could_do, [])

    def some_random_local_attraction(self, inp: Input):
        notes = ["E.g.: hire a mountain bike, go-karting, cinema, trampolining, museum, theatre, musical peformance, astronomy talk, science talk, poetry reading, read a book in a cafe, board game group"]
        return Result(
            suitability=Suitablility.i_guess_i_could_do,
            notes=notes
        )

    def visit_family(self, inp: Input):
        return Result(Suitablility.i_guess_i_could_do, [])



def remove_camelcase(name):
    return name.replace("_", " ")


def hello(
        time_available,
        how_far_ahead,
        day,
        month,
        budget,
        legs,
        arms,
):
    today = date.today()

    time_available = TimeAvailable[time_available]

    how_far_ahead = HowFarPlanningAhead[how_far_ahead]
    if how_far_ahead == HowFarPlanningAhead.today:
        day = today.weekday()
        month = today.month
    elif how_far_ahead == HowFarPlanningAhead.tomorrow:
        tomorrow = today + timedelta(days=1)
        day = tomorrow.weekday()
        month = tomorrow.month
    else:
        day = DayOfWeek[day]
        month = Month[month]

    loop = asyncio.get_event_loop()
    web_data = loop.run_until_complete(collect_web_data(time_available, how_far_ahead, day))

    results = [] # type: List[Tuple[str, Result]]

    a = Activities()
    input = Input(
        time_available=time_available,
        how_far_ahead=how_far_ahead,
        day=day,
        month=month,
        budget=Budget[budget],
        forecasts=web_data,
        legs=TiredOrInjuredness[legs],
        arms=TiredOrInjuredness[arms],
    )

    for name, method in Activities.__dict__.items():
        if callable(method):
            results.append((name, method(a, input)))

    print("Suggestions:")
    for (name, result) in sorted(
            results,
            key=lambda x: x[1].suitability,
            reverse=True):
        print(f"{remove_camelcase(name)}: {result.suitability.name} {result.notes}")


def usage():
    enums = [
        TimeAvailable,
        HowFarPlanningAhead,
        DayOfWeek,
        Month,
        Budget,
        TiredOrInjuredness]

    print(
"""If HowFarPlanningAhead is today or or tomorrow, then day of week and month are ignored and calculated automatically
    
    """)
    for e in enums:
        print(e)
        for v in e:
            print(v.name)
        print("")

if __name__ == '__main__':
  fire.Fire()