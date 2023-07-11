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
    schedule_city: str
    schedule_door_open: bool
    schedule_door_close: bool
    schedule_door_open_offset: int
    schedule_door_close_offset: int
    schedule_sunrise: datetime = datetime.min
    schedule_sunset: datetime = datetime.min
