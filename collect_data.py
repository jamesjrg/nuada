from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import DefaultDict, Dict, Any

import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re

from domain_types import WindsurfForecast, SurfForecast, Weather, Snowiness, TimeAvailable, DayOfWeek, \
    HowFarPlanningAhead, \
    WebData, Forecast, Temperature


@dataclass
class MetOfficeResult:
    weather: Weather
    snowiness: Snowiness
    temperature: Temperature

@dataclass
class WindFinderResult:
    forecast: WindsurfForecast


@dataclass
class WindyAppResult:
    forecast: WindsurfForecast

@dataclass
class MagicSeaweedResult:
    forecast: SurfForecast

@dataclass
class BbcTidesResult:
    pass

@dataclass
class MwisResult:
    pass


@dataclass
class AxbridgeWeatherResult:
    forecast: WindsurfForecast


met_office_locations = {
    "bristol": "gcnhtnumz",
    "porthcawl": "gcjkgequs",
    "woolacombe": "gcj5079ep",
    "brecon": "gcjxdb9vh",
    "llanberis": "gcmn4jg3d",
    "keswick": "gcty8ey7h",
    "fort william": "gfh75zeru",
    "poole": "gcn8db1mu",
    "truro": "gbumvn49q",
    "newquay": "gbuqu9f0x",
    "weymouth": "gbyrbjgrk",
    "aviemore": "gfjm35bwe",
    "pontypool": "gcjy4ghnx",
}

windfinder_locations = {
    "axebridge": "bristol_lulsgate",
    "poole": "sandbanks_poole",
    "llandegfedd": "llandegfedd",
    "weymouth": "isle_of_portland",
    "westom": "weston-super-mare",
}

windy_app_locations = {
    "axebridge": "235578",
    "poole": "20365",
    "weymouth": "360502",
    "weston": "17124",
}

bbc_tides_locations = {
    "clevedon": "12/525",
    "portland": "8/33",
    "poole": "8/36a",
    "porthcawl": "11/512",
    "weston": "12/527",
}

mwis_locations = {
    "brecon beacons": "english-and-welsh/brecon-beacons",
    "cairngorms": "scottish/cairngorms-np-and-monadhliath",
    "snowdonia": "english-and-welsh/snowdonia-national-park",
    "west highlands": "scottish/west-highlands",
}

magic_seaweed_locations = {
    "rest bay": "Porthcawl-Rest-Bay-Surf-Report/1449/",
    "woolacombe": "Woolacombe-Surf-Report/1352/",
    "towan": "Newquay-Towan-Surf-Report/6025/",
}


async def windfinder(session, spot):
    def parse_period(period):
        speed, gusts = [x.text for x in period.select(".units-ws")]
        wind_direction_attr = period.select(".directionarrow")[0]["title"]
        wind_direction = re.match("\d+", wind_direction_attr).group(0)
        # TODO tide height
        return speed, gusts, wind_direction

    def parse_day(day):
        title = day.find('h3').text.strip()

        periods = day.select("div.weathertable__row.row-clear")
        return (title, [parse_period(p) for p in periods])

    code = windfinder_locations[spot]
    async with session.get("https://www.windfinder.com/forecast/{}".format(code)) as resp:
        text = await resp.text()

    soup = BeautifulSoup(text)
    days = [parse_day(d) for d in soup.findAll('div', class_='forecast-day')]

    return spot, WindsurfForecast(forecast=None)


async def metoffice(session, spot) -> Dict[]:

    def parse_period(period):
        pass

    def parse_day(day):
        title = day["id"]

        times = day.select("tr.step-time > th:not(th.screen-reader-only)")
        symbols = [x["alt"] for x in day.select("tr.step-symbol > td img")]

    code = met_office_locations[spot]
    async with session.get(f"https://www.metoffice.gov.uk/weather/forecast/{code}") as resp:
        text = await resp.text()

    soup = BeautifulSoup(text)
    days = soup.select(".forecast-day")

    return spot, MetOfficeResult(
        weather=,
        snowiness=,
        temperature=,
    )

async def windy_app(session, spot):
    code = windy_app_locations[spot]
    async with session.get(f"https://windy.app/forecast2/spot/{code}") as resp:
        text = await resp.text()

    soup = BeautifulSoup(text)

    return spot, WindyAppResult(forecast=None)

async def bbc_tide_times(session, spot):
    code = windy_app_locations[spot]
    async with session.get(f"https://www.bbc.co.uk/weather/coast-and-sea/tide-tables/{code}") as resp:
        text = await resp.text()

    soup = BeautifulSoup(text)
    rows = soup.select(".wr-c-tide-extremes__row")
    return spot, BbcTidesResult()


async def mwis(session, spot):
    code = windy_app_locations[spot]
    async with session.get(f"https://www.bbc.co.uk/weather/coast-and-sea/tide-tables/{code}") as resp:
        text = await resp.text()

    soup = BeautifulSoup(text)

    return spot, MwisResult()

async def magic_seaweed(session, spot):
    code = magic_seaweed_locations[spot]
    async with session.get(f"https://magicseaweed.com/{code}") as resp:
        text = await resp.text()

    return spot, MagicSeaweedResult(forecast=None)

async def axbridge_weather_station(session):
    async with session.get("https://roddickinson.net/cheddar/sse-json.php") as resp:
        text = await resp.text()

    return spot, AxbridgeWeatherResult(forecast=None)


async def collect_web_data(time_available: TimeAvailable, how_far_ahead: HowFarPlanningAhead, day: DayOfWeek):
    tasks = []
    for loc in met_office_locations:
        tasks.append((metoffice, [loc]))
    # for loc in windfinder_locations:
    #     tasks.append((windfinder, [loc]))
    # for loc in windy_app_locations:
    #     tasks.append((windy_app, [loc]))
    for loc in bbc_tides_locations:
        tasks.append((bbc_tide_times, [loc]))
    # for loc in magic_seaweed_locations:
    #     tasks.append((magic_seaweed, [loc]))
    tasks.append((axbridge_weather_station, []]))

    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*[t[0](session, *t[1])for t in tasks])

    met_office_results: Dict[str, MetOfficeResult] = {}

    other_results: DefaultDict[type, Dict[str, Any]] = defaultdict(dict)
    for spot, res in results:
        if type(res) == MetOfficeResult:
            met_office_results[spot] = res
        else:
            other_results[type(res)][spot] = res

    def map_forecast(metoffice_spot):
        return Forecast(
            wind=WindsurfForecast.almost_none,
            surf=SurfForecast.no_surf,
            sun_and_rain=met_office_results[metoffice_spot].weather,
            temperature=met_office_results[metoffice_spot].temperature,
            snowiness=met_office_results[metoffice_spot].snowiness,
        )

    return WebData(
        bristol=map_forecast("bristol"),
        porthcawl=map_forecast("porthcawl"),
        woolacombe=map_forecast("woolacombe"),
        brecon=map_forecast("brecon"),
        llanberis=map_forecast("llanberis"),
        keswick=map_forecast("keswick"),
        fort_william=map_forecast("fort william"),
        poole=map_forecast("poole"),
        truro=map_forecast("truro"),
        newquay=map_forecast("newquay"),
        weymouth=map_forecast("weymouth"),
        aviemore=map_forecast("aviemore"),
        axbridge=map_forecast("axbridge"),
        llandegfedd=map_forecast("pontypool"),
        weston=map_forecast("weston"),
    )


