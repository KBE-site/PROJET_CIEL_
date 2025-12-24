import requests
from datetime import datetime, timezone
import dateutil.parser

from cachetools import TTLCache, cachedmethod

meteo_cache = TTLCache(maxsize=1, ttl=600)

class Meteo:
    def __init__(self) -> None:
        self._lat: float = 48.85341
        self._lon: float = 2.3488

    def _closest_timeseries(self, timeseries):
        if not timeseries:
            raise ValueError("No timeseries data available")

        now = datetime.now(timezone.utc)
        closest = min(timeseries, key=lambda x: abs(dateutil.parser.isoparse(x["time"]) - now))
        return closest


    def _get_metno(self, lat: float, lon:float) -> dict:
        url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}"
        headers = {
        "User-Agent": "projetCiel/1.0 bravo.adresse@gmail.com.com"
        }

        try:
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
        except Exception:
            raise ValueError('Met.no error')

        timeseries = data["properties"]["timeseries"]
        try:
            timeseries_match = self._closest_timeseries(timeseries)
        except Exception:
            raise ValueError("Timeseries error")
        
        details = timeseries_match["data"]["instant"]["details"]

        return {
            'temperature': details["air_temperature"],
            'pressure': details["air_pressure_at_sea_level"],
            'humidity': details["relative_humidity"]
        }
    
    @cachedmethod(lambda self: meteo_cache)
    def get_current_meteo(self) -> dict:
        try:
            data = self._get_metno(self._lat, self._lon)
        except Exception:
            ValueError('API meteo error')
            return {"temperature": 15, "pressure": 1013.25, "humidity": 0.5}
        
        return {
            'temperature': data['temperature'],
            'pressure': data['pressure'],
            'humidity': data['humidity']
        }
