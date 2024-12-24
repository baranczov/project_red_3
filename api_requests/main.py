import json
import sys
import os
import requests

sys.path.append(os.getcwd())
from config import API_KEY


def get_location(location):
    """Получает ключ и название местоположения по запросу."""
    try:
        response = requests.get(
            "https://dataservice.accuweather.com/locations/v1/cities/translate.json",
            params={
                "apikey": API_KEY,
                "q": location.lower(),
                "language": "ru-ru",
                "details": "true",
            },
        )
        response.raise_for_status()

        data = response.json()
        if data:
            return data[0]["Key"], data[0]["LocalizedName"]
        return None

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении местоположения: {e}")
        return None


def get_weather_by_location(location_key):
    """Получает данные о погоде по ключу местоположения."""
    try:
        response = requests.get(
            f"https://dataservice.accuweather.com/forecasts/v1/daily/5days/{location_key}",
            params={
                "apikey": API_KEY,
                "language": "ru-ru",
                "details": "true",
                "metric": "true",
            },
        )
        response.raise_for_status()

        data = response.json()
        temperature = data["DailyForecasts"][0]["Temperature"]["Maximum"]["Value"]
        humidity = data["DailyForecasts"][0]["Day"]["RelativeHumidity"]["Average"]
        wind_speed = data["DailyForecasts"][0]["Day"]["Wind"]["Speed"]["Value"]
        rain_probability = data["DailyForecasts"][0]["Day"]["RainProbability"]

        return {
            "temperature": ("Температура (°C)", temperature),
            "humidity": ("Влажность (%)", humidity),
            "wind_speed": ("Скорость ветра (км/ч)", wind_speed),
            "rain_prob": ("Вероятность дождя (%)", rain_probability),
        }

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении погоды: {e}")
        return None


def get_coordinates(city):
    """Получает координаты города по его названию."""
    try:
        search_url = "http://dataservice.accuweather.com/locations/v1/cities/search"
        params = {"apikey": API_KEY, "q": city, "language": "ru-ru"}

        response = requests.get(search_url, params=params)
        response.raise_for_status()

        city_data = response.json()[0]
        return {
            "lat": city_data["GeoPosition"]["Latitude"],
            "lon": city_data["GeoPosition"]["Longitude"],
        }

    except (requests.RequestException, IndexError, KeyError) as e:
        print(f"Ошибка при получении координат для города {city}: {str(e)}")
        return None


def main():
    """Основная функция для получения и отображения погоды."""
    location_key, localized_name = get_location("Москва")
    if location_key:
        data = get_weather_by_location(location_key)

        print(f"Погода в городе {localized_name}:\n")
        to_len = max(len(name) for name, _ in data.values()) + 3
        answer = "\n".join(f"{name}{' ' * (to_len - len(name))}| {value}" for name, value in data.values())
        print(answer)

        with open("weather_data.json", "w") as file:
            json.dump(data, file)


if __name__ == "__main__":
    main()
