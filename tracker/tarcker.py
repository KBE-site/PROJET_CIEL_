from datetime import datetime, UTC

from astropy.coordinates import get_body, EarthLocation, AltAz, SkyCoord
from astropy.time import Time

class Tracker:
    def __init__(self, lat: float=48.85341, lon: float=2.3488, height: float=42.0) -> None:
        self._location = EarthLocation(lat=lat, lon=lon, height=height)

    def _altaz(self) -> tuple[AltAz, Time]:
        now = Time(datetime.now(UTC))
        return AltAz(obstime=now, location=self._location), now

    def get_solar_system_object(self, name: str) -> SkyCoord:
        altaz_frame, now = self._altaz()
        coord = get_body(name, now, self._location).transform_to(altaz_frame)
        return coord
    
    
    def get_alt_az(self, name: str) -> tuple[float, float]:
        coord = self.get_solar_system_object(name)
        return float(coord.alt.degree), float(coord.az.degree) # type: ignore