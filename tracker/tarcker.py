from datetime import datetime, UTC
from functools import lru_cache

import astropy.units as u
from astropy.coordinates import get_body, EarthLocation, AltAz, SkyCoord
from astropy.time import Time
from astroquery.simbad import Simbad

from core.status import status_manager
from api.meteo import Meteo

class Tracker:
    """    
    A tracker for calculating the altitude and azimuth coordinates of celestial bodies.
    This class provides functionality to determine the position of space objects 
    (celestial bodies) in local Alt-Az (Altitude-Azimuth) coordinates from a specified 
    Earth location.
    Attributes:
        _location (EarthLocation): The observer's location on Earth, defined by latitude, 
                                   longitude, and height above sea level.
    Parameters:
        lat (float, optional): The latitude of the observer in degrees. Defaults to 48.85341 
                               (Paris, France).
        lon (float, optional): The longitude of the observer in degrees. Defaults to 2.3488 
                               (Paris, France).
        height (float, optional): The height of the observer above sea level in meters. 
                                  Defaults to 42.0.
    Example:
        >>> tracker = Tracker(lat=48.85341, lon=2.3488, height=42.0)
        >>> alt, az = tracker.get_alt_az('sun')
        >>> print(f"Sun altitude: {alt}°, azimuth: {az}°")
        
    """
    def __init__(self, lat: float=48.85341, lon: float=2.3488, height: float=42.0) -> None: # Position de Paris ouest
        self._location = EarthLocation(lat=lat, lon=lon, height=height)

    def _get_meteo(self):
        user = status_manager.get_status()["meteorological"]
        api = Meteo().get_current_meteo()

        temperature = (
            user["temperature"] 
            if user["temperature"] is not None 
            else api.get("temperature", 15)
        )

        pressure = (user["pressure"] 
            if user["pressure"] is not None 
            else api.get("pressure", 1013.25)
        )

        humidity = (user["humidity"] 
            if user["humidity"] is not None
            else api.get("humidity", 0.5)
        )

        import astropy.units as u
        return {
            "temperature": temperature * u.deg_C,
            "pressure": pressure * u.hPa,
            "humidity": humidity
        }

    def _altaz(self) -> tuple[AltAz, Time]:
        """
        Calculate the current altitude and azimuth coordinates.

        Returns
        -------
        tuple[AltAz, Time]
            A tuple containing:
            - AltAz: The altitude and azimuth coordinates for the current observation time and location
            - Time: The current UTC time of the observation
        """
        now = Time(datetime.now(UTC))
        meteo = self._get_meteo()

        return AltAz(
            obstime=now,
            location=self._location,
            temperature=meteo['temperature'],
            pressure=meteo['pressure'],
            relative_humidity=meteo['humidity']
        ), now

    def _get_solar_space_object(self, name: str) -> SkyCoord:
        """
        Get the current position of a celestial body in Alt-Az coordinates.
        
        This method retrieves the position of a specified celestial body 
        at the current time and transforms it to the local Alt-Az (Altitude-Azimuth) 
        coordinate frame based on the observer's location.
        
        Args:
            name (str): The name of the celestial body (e.g., 'sun', 'moon', 'mars').
        
        Returns:
            SkyCoord: The position of the celestial body in Alt-Az coordinates.
        """
        altaz_frame, now = self._altaz()
        coord = get_body(name, now, self._location).transform_to(altaz_frame)
        return coord
    
    @lru_cache(maxsize=128)    
    def _resolve_simbad(self, name: str) -> SkyCoord:
        coord = Simbad.query_object(name)
        if coord is None:
            raise ValueError(f"Object '{name}' not found in SIMBAD")

        ra, dec = coord["ra"][0], coord["dec"][0]
        return SkyCoord(ra, dec, unit=("hourangle", "deg"))

    def _get_deep_space_object(self, name: str):
        altaz_frame, _ = self._altaz()
        coord = self._resolve_simbad(name.strip().lower())
        return coord.transform_to(altaz_frame)
    
    def get_object(self, name: str) -> tuple[float, float]:
        """
        Get the altitude and azimuth coordinates of a space object.
        
        Args:
            name (str): The name of the space object.
        
        Returns:
            tuple[float, float]: A tuple containing:
                - altitude (float): The altitude angle in degrees.
                - azimuth (float): The azimuth angle in degrees.
        """
        name = name.strip().lower()
        try:
            coord = self._get_solar_space_object(name)
        except Exception:
            coord = self._get_deep_space_object(name)

        return float(coord.alt.degree), float(coord.az.degree) # type: ignore