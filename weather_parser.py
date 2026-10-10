from collections import defaultdict
from dataclasses import dataclass
import json
import sys
from urllib.parse import quote
from urllib.request import urlopen


@dataclass
class WeatherData:
    city: str
    temp_celsius: int
    country: str

    def __str__(self) -> str:
        return f"{self.city}, {self.country}, {self.temp_celsius:+d}\u00B0C"

def get_cities(filename: str) -> list[str]:
    with open(filename, "r", encoding="utf-8-sig") as file:
        cities = {
            line.strip()
            for line in file
            if line.strip()
        }
    return sorted(cities)

def get_weather(city: str) -> WeatherData:
    url = f"https://wttr.in/{quote(city, safe='')}?format=j1"

    with urlopen(url, timeout=10) as response:
        city_data = json.loads(response.read())
    
    curr_temp = int(city_data["current_condition"][0]["temp_C"])
    country = city_data["nearest_area"][0]["country"][0]["value"]

    return WeatherData(
        city=city,
        temp_celsius=curr_temp,
        country=country,
    )

def get_cities_weather(cities_names: list[str]) -> list[WeatherData]:
    cities_weather: list[WeatherData] = []
    print("=================")
    for city in cities_names:
        try:
            city_weather = get_weather(city)
            cities_weather.append(city_weather)
            print(city_weather)
        except Exception as exc:
            print(f"Could not get weather for {city}: {exc}")
    return cities_weather

def sort_by_country(cities_weather: list[WeatherData]) -> None:
    country_dict: dict[str, list[WeatherData]] = defaultdict(list)
    for city in cities_weather:
        country_dict[city.country].append(city)

    print("=================")
    for country in sorted(country_dict):
        cities_list = country_dict[country]
        city_num = len(cities_list)
        city_num_arg = "cities" if city_num > 1 else "city"
        temperatures = [city.temp_celsius for city in cities_list]
        average_arg = f"{(sum(temperatures) / city_num):+.1f}".rstrip("0").rstrip(".")
        print(
            f"{country} - {city_num} {city_num_arg}, "
            f"avg: {average_arg}\u00B0C, "
            f"min: {min(temperatures):+d}\u00B0C, "
            f"max: {max(temperatures):+d}\u00B0C")
    print("=================")

def main() -> int:
    if len(sys.argv) != 2:
        print("Should launch with cities file")
        return 1
    try:
        cities_names = get_cities(sys.argv[1])
    except (OSError, UnicodeError) as exc:
        print(f"Failed to read and parse file {sys.argv[1]}: {exc}")
        return 1

    if not cities_names:
        print("Cities list is empty")
        return 0

    cities_weather = get_cities_weather(cities_names)
    sort_by_country(cities_weather)

    return 0


if __name__ == "__main__":
    sys.exit(main())