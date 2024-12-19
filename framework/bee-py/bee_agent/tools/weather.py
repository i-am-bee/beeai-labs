# SPDX-License-Identifier: Apache-2.0

from typing import Literal, Optional, TypedDict
from urllib.parse import urlencode

import requests

from .tool import Tool


class WeatherLocation(TypedDict):
    name: Optional[str]
    country: Optional[str]
    language: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]


class WeatherInput(TypedDict):
    location: WeatherLocation
    start_date: Optional[str]
    end_data: Optional[str]
    temperature_unit: Optional[Literal["celsius", "fahrenheit"]] = "celsius"


class WeatherTool(Tool):
    name = "WeatherTool"
    description = "Retrieve current, past, or future weather forecasts for a location."

    def input_schema(self):
        # # TODO: remove hard code
        return '{"type":"object","properties":{"location":{"anyOf":[{"type":"object","properties":{"name":{"type":"string"},"country":{"type":"string"},"language":{"type":"string","default":"English"}},"required":["name"],"additionalProperties":false},{"type":"object","properties":{"latitude":{"type":"number"},"longitude":{"type":"number"}},"required":["latitude","longitude"],"additionalProperties":false}]},"start_date":{"type":"string","format":"date","description":"Start date for the weather forecast in the format YYYY-MM-DD (UTC)"},"end_date":{"type":"string","format":"date","description":"End date for the weather forecast in the format YYYY-MM-DD (UTC)"},"temperature_unit":{"type":"string","enum":["celsius","fahrenheit"],"default":"celsius"}},"required":["location","start_date"],"additionalProperties":false}'

    def _geocode(self, location):
        params = {"format": "json", "count": 1}
        if location.get("name"):
            params["name"] = location.get("name")
        if location.get("country"):
            params["country"] = location.get("country")
        if location.get("language"):
            params["language"] = location.get("language")
        params = urlencode(params, doseq=True)

        response = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?${params}",
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )

        response.raise_for_status()
        results = response.json()["results"]
        return results[0]

    def get_params(self, input: WeatherInput):
        params = {
            "forecast_days": 1,
            "current": [
                "temperature_2m",
                "rain",
                "relative_humidity_2m",
                "wind_speed_10m",
            ],
            "daily": ["temperature_2m_max", "temperature_2m_min", "rain_sum"],
            "hourly": ["temperature_2m", "relative_humidity_2m", "rain"],
            "timezone": "UTC",
        }

        if input.get("location", {}).get("name"):
            geocode = self._geocode(input.get("location"))
            params["latitude"] = geocode.get("latitude")
            params["longitude"] = geocode.get("longitude")
        else:
            params["latitude"] = input.get("location", {}).get("latitude")
            params["longitude"] = input.get("location", {}).get("longitude")

        return params

    def _run(self, input: WeatherInput, options=None):
        params = urlencode(self.get_params(input), doseq=True)
        response = requests.get(
            f"https://api.open-meteo.com/v1/forecast?${params}",
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        response.raise_for_status()
        return response.json()
