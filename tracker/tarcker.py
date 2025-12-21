import logging
from datetime import datetime, UTC
from typing import Union

from astropy.coordinates import get_body, EarthLocation, AltAz, SkyCoord
from astropy.time import Time

class Tracker:
    def __init__(self, lat: float=48.85341, lon: float=2.3488, height: float=42.0) -> None:
        self._location = EarthLocation(lat=lat, lon=lon, height=height)

    def _now(self) -> Time:
        return Time(datetime.now(UTC))

    def get_solar_system_object(self, name: str) -> SkyCoord:
        now = self._now()
        altaz_frame = AltAz(obstime=now, location=self._location)
        coord = get_body(name, now, self._location).transform_to(altaz_frame)
        return coord
