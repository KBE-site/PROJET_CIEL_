import numbers

from web.websocket import socketio
from core.status import AppStatus, status_manager
from tracker.tarcker import Tracker

class Manager:
    def __init__(self):
        self._tracker = Tracker()
        self._tracking_target = None
    
    def idle(self):
        status_manager.set_status(AppStatus.IDLE)
        self._tracking_target = None

        socketio.emit(
                'status_update',
                status_manager.get_status()
        )

    def point_to(self, target: str, temperature, pressure, humidity) -> None:

        if not isinstance(target, str):
            raise ValueError("Target must be a string")

        target = target.strip()
        if not target:
            raise ValueError("Target must be a non-empty string")
        
        status_manager.set_status(AppStatus.POINTING, target)

        self.set_meteo(
            temperature,
            pressure,
            humidity
        )

        socketio.emit(
            'status_update',
            status_manager.get_status()
        )

        self._tracking_target = target
        socketio.start_background_task(self._track_loop, target)

    def set_meteo(self, temperature, pressure, humidity):
        for name, value in zip(("temperature", "pressure", "humidity"), (temperature, pressure, humidity)):
            if value is not None and not isinstance(value, numbers.Real):
                raise ValueError(f"{name} must be a real number or None")
            
        status_manager.set_temperature(temperature)
        status_manager.set_pressure(pressure)
        status_manager.set_humidity(humidity)
        
    def _track_loop(self, target: str):
        last_alt, last_az = None, None
        while status_manager.get_status()['status'] != AppStatus.IDLE and self._tracking_target == target:
            try:
                alt, az = self._tracker.get_object(target)

                if alt != last_alt or az != last_az:
                    socketio.emit(
                        'coord_update',
                        {'alt':alt, 'az': az}
                    )
                    last_alt, last_az = alt, az

                socketio.sleep(1)

            except Exception as e:
                print(f"Tracking error {e}")
                self.idle()
                break
                
            
    def stop_pointing(self):
        self.idle()

    def establish(self):
        status_manager.set_established(True)

        socketio.emit(
                'status_update',
                status_manager.get_status()
        )


