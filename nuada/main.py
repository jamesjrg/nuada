import asyncio

import fire
from rich.console import Console

from nuada.collect_data import collect_web_data
from nuada.domain_types import Activity
from nuada.domain_types import Requirements as req

# from domain_types import (
#     Weather,
#     Budget,
# )


activities = [
    Activity("swim indoors", req([]), req([]), 5, 5, []),
    Activity(
        "swim in marine lake",
        req(["warmish water", "no rain"]),
        req(["not freezing water", "not torrential rain"]),
        6,
        5,
        ["Could get lessons"],
    ),
    Activity(
        "swim in sea",
        req(["warmish water", "no rain", "tide"]),
        req(["not freezing water", "not torrential rain"]),
        7,
        5,
        ["Could get lessons"],
    ),
    Activity(
        "indoor bouldering or autobelay", req(["GPS is on"]), req(["?"]), 6, 5, []
    ),
    Activity(
        "climb outside",
        req(["I can find a partner", "sunny", "dry"]),
        req(["dry"]),
        7,
        5,
        [],
    ),
    Activity("slackline", req(["?"]), req(["?"]), 99, 99, []),
    Activity("sail", req(["?"]), req(["?"]), 99, 99, []),
    Activity("kayak on marine lake", req(["?"]), req(["?"]), 99, 99, []),
    Activity(
        "kayak in the sea",
        req(["?"]),
        req(["?"]),
        99,
        99,
        ["book a multi day trip, course or rolling clinic"],
    ),
    Activity("surf", req(["?"]), req(["?"]), 99, 99, []),
    Activity(
        "road bike",
        req(["?"]),
        req(["?"]),
        99,
        99,
        ["Could also consider going bike packing or credit card touring"],
    ),
    Activity("orienteering", req(["an event is on"]), req(["?"]), 99, 99, []),
    Activity(
        "run",
        req(["a club is meeting"]),
        req(["?"]),
        99,
        99,
        [
            "Anything from 2k up the road, to multi day run in the mountains",
            "Could organise a micro TACH run",
        ],
    ),
    Activity("nav practice", req(["a club is meeting"]), req(["?"]), 99, 99, []),
    Activity(
        "easy mountaineering or scrambling",
        req(["a club is meeting"]),
        req(["?"]),
        99,
        99,
        [],
    ),
]


# class Activities:
#     def study_first_aid_or_ropework(self, inp: Input):
#         return Result(Suitablility.i_guess_i_could_do, [])

#     def read_a_book_or_watch_tv(self, inp: Input):
#         if inp.time_available > TimeAvailable.two_hours:
#             return Result(Suitablility.no, [])

#         return Result(Suitablility.i_guess_i_could_do, [])

#     def practice_guitar(self, inp: Input):
#         return Result(Suitablility.i_guess_i_could_do, [])

#     def learn_to_cook(self, inp: Input):
#         return Result(Suitablility.i_guess_i_could_do, [])

#     def surf_with_a_meetup_group(self, inp: Input):
#         if inp.time_available < TimeAvailable.all_day:
#             return Result(Suitablility.no, [])

#         return Result(Suitablility.i_guess_i_could_do, [])

#     def bristol_con_vol(self, inp: Input):
#         if inp.time_available < TimeAvailable.all_day:
#             return Result(Suitablility.no, ["not enough time"])

#         return Result(Suitablility.i_guess_i_could_do, [])

#     def con_vol_holiday(self, inp: Input):
#         if inp.time_available <= TimeAvailable.all_weekend:
#             return Result(Suitablility.no, ["not enough time"])

#         return Result(Suitablility.i_guess_i_could_do, [])

#     def yoga_or_fitness_class(self, inp: Input):
#         return Result(Suitablility.i_guess_i_could_do, [])

#     def home_fitness_workout(self, inp: Input):
#         return Result(Suitablility.i_guess_i_could_do, [])

#     def some_random_local_attraction(self, inp: Input):
#         notes = [
#             "E.g.: hire a mountain bike, go-karting, cinema, trampolining, museum, theatre, musical peformance, astronomy talk, science talk, poetry reading, read a book in a cafe, board game group"
#         ]
#         return Result(suitability=Suitablility.i_guess_i_could_do, notes=notes)


def hello():
    loop = asyncio.get_event_loop()
    data = loop.run_until_complete(collect_web_data())

    console = Console()

    for location, location_results in data.items():
        console.print(location)
        for res in location_results:
            console.print(res)

    # for activity in activities:
    #     result = assess_activity(activity, )

    # print("Suggestions:")
    # for (name, result) in sorted(results, key=lambda x: x[1].suitability, reverse=True):
    #     print(f"{remove_camelcase(name)}: {result.suitability.name} {result.notes}")


if __name__ == "__main__":
    fire.Fire(hello)
