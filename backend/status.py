from dataclasses import dataclass
from datetime import datetime


@dataclass
class Status:
    temperature: float
    humidity: float
    door: bool  # true: door up, false: door down
    light: bool
    master: bool
    current_datetime: datetime
    last_manual_door_datetime: datetime
