from typing import Optional

from flask import request

from core.helpers import to_float_or_none

class PointingForm:
    def __init__(self) -> None:
        self.obj: str = request.form.get("obj", "").strip()
        if not self.obj:
            raise ValueError("'object' must have a value")
        
        self.temperature: Optional[float] = to_float_or_none(request.form.get('temperature'))
        self.pressure: Optional[float] = to_float_or_none(request.form.get('pressure'))
        self.humidity: Optional[float] = to_float_or_none(request.form.get('humidity'))