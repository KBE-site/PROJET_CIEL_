from core.websocket import socketio
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

    def point_to(self, target: str) -> None:
        if not isinstance(target, str):
            raise ValueError("Target must be a string")

        target = target.strip()
        if not target:
            raise ValueError("Target must be a non-empty string")
        
        status_manager.set_status(AppStatus.POINTING, target)
        socketio.emit(
            'status_update',
            status_manager.get_status()
        )

        self._tracking_target = target
        socketio.start_background_task(self._track_loop, target)
        
    def _track_loop(self, target: str):
        last_alt, last_az = None, None
        while status_manager.get_status()['status'] != AppStatus.IDLE and self._tracking_target == target:
            try:
                alt, az = self._tracker.get_alt_az(target)

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

