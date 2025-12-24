from enum import Enum
from threading import Lock
from typing import Optional

import numbers

class AppStatus(str, Enum):
    """
    Docstring for AppStatus

    Enumeration for application statuses.
    Attributes:
        IDLE (str): Represents the idle status.
        POINTING (str): Represents the pointing status.
    """
    IDLE = "IDLE"
    POINTING = "POINTING"


class StatusManager:
    """
    Docstring for StatusManager 


    Manages the status of the application, ensuring thread-safe access and updates.
        Attributes:
            _status (AppStatus): Current status of the application.
            _established (bool): Indicates if the pointing has been established.
            _target (Optional[str]): The target being pointed to, if any.
            _lock (Lock): A threading lock to ensure thread-safe operations.

    Methods:
        set_status(status: AppStatus, target: Optional[str] = None) -> None:
            Sets the current status of the application. If the status is POINTING,
            a target string must be provided. If the status is IDLE, no target should be provided.
        set_established(established: bool) -> None:
            Sets the established flag. This can only be set if the current status is POINTING.  
        get_status() -> dict:
            Returns the current status, target, and established flag as a dictionary.
    """ 
    def __init__(self) -> None:
        self._lock = Lock()

        self._status: AppStatus = AppStatus.IDLE
        self._target: Optional[str] = None
        self._established: bool = False

        self._temperature: Optional[numbers.Real] = None
        self._pressure: Optional[numbers.Real] = None
        self._humidity: Optional[numbers.Real] = None

    def set_status(self, status: AppStatus, target: Optional[str] = None) -> None:
        with self._lock:
            if status == AppStatus.POINTING:
                if not isinstance(target, str) or len(target) < 1:
                    raise ValueError("POINTING requires a target string")
                self._status = status
                self._established = False
                self._target = target

            elif status == AppStatus.IDLE:
                if target is not None:
                    raise ValueError("IDLE status cannot have a target")
                self._status = status
                self._established = False
                self._target = None
                self._temperature = None
                self._pressure = None
                self._humidity = None

    def set_established(self, established: bool) -> None:
        with self._lock:
            if not isinstance(established, bool):
                raise ValueError("'established' must be a bool")
            
            if self._status != AppStatus.POINTING:
                raise ValueError("Cannot set 'established' unless status is POINTING")
            self._established = established

    def set_temperature(self, temperature) -> None:
        with self._lock:
            if temperature is not None and not isinstance(temperature, numbers.Real):
                self.set_status(AppStatus.IDLE)
                raise ValueError('temperature must be a real number or null')

            self._temperature = temperature

    def set_pressure(self, pressure) -> None:
        with self._lock:
            if pressure is not None and not isinstance(pressure, numbers.Real):
                self.set_status(AppStatus.IDLE)
                raise ValueError('pressure must be a real number or null')

            self._pressure = pressure

    def set_humidity(self, humidity) -> None:
        with self._lock:
            if humidity is not None and not isinstance(humidity, numbers.Real):
                self.set_status(AppStatus.IDLE)
                raise ValueError('humidity must be a real number or null')

            self._humidity = humidity

    def get_status(self) -> dict:
        with self._lock:
            return {    
                "status": self._status.value,
                "target": self._target,
                "established": self._established,
                "meteorological": {
                    "temperature": self._temperature,
                    "pressure": self._pressure,
                    "humidity": self._humidity
                }
            }


        
status_manager = StatusManager()

def _debug(action: bool) -> None:
    if action:
        print(f"1 IDLE : {status_manager.get_status()}")

    status_manager.set_status(AppStatus.POINTING, "M42")
    if action:
        print(f"3 POINTING : {status_manager.get_status()}")

    status_manager.set_established(True)
    if action:
        print(f"3 POINTING established: {status_manager.get_status()}")

