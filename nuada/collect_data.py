import asyncio
import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from itertools import groupby
from operator import attrgetter
from typing import Any, Callable, Dict, List

from aiohttp import ClientSession
from bs4 import BeautifulSoup

from nuada.domain_types import WindsurfForecast

PARSER = "html.parser"


class WebResult:
    pass


@dataclass
class MetOfficeResult(WebResult):
    forecast: Dict[date, Any]


@dataclass
class WindFinderResult(WebResult):
    forecast: Dict[date, Any]


@dataclass
class WindyAppResult(WebResult):
    forecast: Dict[date, Any]


@dataclass
class MagicSeaweedResult(WebResult):
    forecast: Dict[date, Any]


@dataclass
class BbcTidesResult(WebResult):
    forecast: Dict[date, Any]


@dataclass
class MwisResult(WebResult):
    forecast: Dict[date, Any]


@dataclass
class AxbridgeWeatherResult(WebResult):
    forecast: Dict[date, Any]


met_office_locations = {
    "bristol": "gcnhtnumz",
    # "porthcawl": "gcjkgequs",
    # "woolacombe": "gcj5079ep",
    "brecon": "gcjxdb9vh",
    # "llanberis": "gcmn4jg3d",
    # "keswick": "gcty8ey7h",
    # "fort william": "gfh75zeru",
    # "poole": "gcn8db1mu",
    # "truro": "gbumvn49q",
    # "newquay": "gbuqu9f0x",
    # "weymouth": "gbyrbjgrk",
    # "aviemore": "gfjm35bwe",
    # "pontypool": "gcjy4ghnx",
}

windfinder_locations = {
    "axbridge": "bristol_lulsgate",
    "poole": "sandbanks_poole",
    "llandegfedd": "llandegfedd",
    "weymouth": "isle_of_portland",
    # "weston": "weston-super-mare",
}

windy_app_locations = {
    "axbridge": "235578",
    "poole": "20365",
    "weymouth": "360502",
    # "weston": "17124",
}

bbc_tides_locations = {
    "clevedon": "12/525",
    "portland": "8/33",
    "poole": "8/36a",
    "porthcawl": "11/512",
    "weston": "12/527",
}

mwis_locations = {
    "brecon": "english-and-welsh/brecon-beacons",
    # "cairngorms": "scottish/cairngorms-np-and-monadhliath",
    # "snowdonia": "english-and-welsh/snowdonia-national-park",
    # "west highlands": "scottish/west-highlands",
}

magic_seaweed_locations = {
    "rest bay": "Porthcawl-Rest-Bay-Surf-Report/1449/",
    "woolacombe": "Woolacombe-Surf-Report/1352/",
    "towan": "Newquay-Towan-Surf-Report/6025/",
}


def parse_windfinder(text) -> WindFinderResult:
    def parse_period(period):
        speed, gusts = [x.text for x in period.select(".units-ws")]
        wind_direction_attr = period.select(".directionarrow")[0]["title"]
        wind_direction = re.match("\\d+", wind_direction_attr).group(0)
        # TODO tide height
        return speed, gusts, wind_direction

    def parse_day(day):
        title = day.find("h3").text.strip()

        periods = day.select("div.weathertable__row.row-clear")
        return (title, [parse_period(p) for p in periods])

    soup = BeautifulSoup(text)
    days = [parse_day(d) for d in soup.findAll("div", class_="forecast-day")]

    print("windfinder")
    print(days)

    return WindFinderResult({date(1950, 1, 1): (WindsurfForecast.almost_none,)})


def parse_metoffice(text) -> MetOfficeResult:
    def parse_period(period):
        pass

    def parse_day(day):
        the_date = datetime.strptime(day["id"], "%Y-%m-%d").date()

        times = day.select("tr.step-time > th:not(th.screen-reader-only)")
        symbols = [x["alt"] for x in day.select("tr.step-symbol > td img")]

        times_and_symbols = [f"{t.text.strip()}: {s}" for t, s in zip(times, symbols)]

        return the_date, times_and_symbols

    soup = BeautifulSoup(text, PARSER)
    days = soup.select(".forecast-day")

    return MetOfficeResult(dict(parse_day(d) for d in days))


def parse_windy_app(text) -> WindyAppResult:
    soup = BeautifulSoup(text, features=PARSER)

    return WindyAppResult({})


def parse_bbc_tide_times(text) -> BbcTidesResult:
    soup = BeautifulSoup(text, features=PARSER)

    def parse_tides(rows_for_day):
        for row in rows_for_day:
            type = row.find("th").text
            time = row.find("td", class_="wr-c-tide-extremes__time").text
            height = row.find("td", class_="wr-c-tide-extremes__height").text

            yield type, time, height

    days = soup.select("section.wr-c-tides-table__section")

    def parse_day(d):
        date = datetime.strptime(d["id"][len("section-") :], "%Y-%m-%d")
        tides = list(parse_tides(d.select(".wr-c-tide-extremes__row")))
        return date, tides

    return BbcTidesResult(dict(parse_day(day) for day in days))


def parse_mwis(text) -> MwisResult:
    soup = BeautifulSoup(text, features=PARSER)

    results = {}

    for i in range(3):
        # TODO parse the date instead, Saturday 10th July 2021
        date = datetime.today().date() + timedelta(days=i)
        results[date] = soup.find("div", {"id": f"Forecast{i}"}).text

    return MwisResult(results)


def parse_magic_seaweed(text) -> MagicSeaweedResult:
    soup = BeautifulSoup(text, features=PARSER)
    days = soup.select("table.table-forecast > tbody")

    def parse_day(tbody_for_day):
        # TODO assumes isn't the new year
        day, month = [
            int(x) for x in tbody_for_day.find("h6").find("small").text.split("/")
        ]

        the_date = date(datetime.today().year, month, day)
        rows = tbody_for_day.findAll("tr", {"data-timestamp": True})
        return the_date, [r.text for r in rows]

    return MagicSeaweedResult(dict(parse_day(d) for d in days))


def parse_axbridge_weather_station(text) -> AxbridgeWeatherResult:
    data = json.loads("{" + text + "}")
    print("Axbridge")
    print(data)

    return AxbridgeWeatherResult({})


@dataclass
class DataSource:
    name: str
    location_map: Dict[str, str]
    parse_func: Callable
    url_map: Callable[[str], str]


data_sources = [
    # DataSource(
    #     "met_office",
    #     met_office_locations,
    #     parse_metoffice,
    #     lambda code: f"https://www.metoffice.gov.uk/weather/forecast/{code}",
    # ),
    # DataSource(
    #     "windfinder",
    #     windfinder_locations,
    #     parse_windfinder,
    #     lambda code: "https://www.windfinder.com/forecast/{}".format(code),
    # ),
    # DataSource(
    #     "windy_app",
    #     windy_app_locations,
    #     parse_windy_app,
    #     lambda code: f"https://windy.app/forecast2/spot/{code}",
    # ),
    # DataSource(
    #     "bbc_tide_times",
    #     bbc_tides_locations,
    #     parse_bbc_tide_times,
    #     lambda code: f"https://www.bbc.co.uk/weather/coast-and-sea/tide-tables/{code}",
    # ),
    # DataSource(
    #     "mwis",
    #     mwis_locations,
    #     parse_mwis,
    #     lambda code: f"https://www.mwis.org.uk/forecasts/{code}",
    # ),
    DataSource(
        "magic_seaweed",
        magic_seaweed_locations,
        parse_magic_seaweed,
        lambda code: f"https://magicseaweed.com/{code}",
    ),
]


@dataclass
class PreFetch:
    location: str
    url: str
    parse_func: Callable


@dataclass
class PostFetch:
    location: str
    parse_func: Callable
    text: str


@dataclass
class ResultWithLocation:
    location: str
    result: WebResult


async def async_fetch(session: ClientSession, data: PreFetch):
    async with session.get(data.url) as resp:
        text = await resp.text()
    return PostFetch(data.location, data.parse_func, text)


async def collect_web_data() -> Dict[str, List[WebResult]]:
    task_data = []
    for source in data_sources:
        for name, code in source.location_map.items():
            task_data.append(PreFetch(name, source.url_map(code), source.parse_func))

    async with ClientSession(requote_redirect_url=False) as session:
        http_responses = await asyncio.gather(
            *[async_fetch(session, data) for data in task_data]
        )

    parsed = [
        ResultWithLocation(post_fetch.location, post_fetch.parse_func(post_fetch.text))
        for post_fetch in http_responses
    ]

    grouped = {
        location: list(x.result for x in result_with_name)
        for location, result_with_name in groupby(
            sorted(parsed, key=attrgetter("location")), key=attrgetter("location")
        )
    }

    return grouped
