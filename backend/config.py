from dataclasses import asdict, dataclass
from datetime import datetime
import json
import logging
import os
from status import Status

# DHT22 input.
DHT22_PIN = 4

# 12V master switch.
MASTER_SWITCH_PIN = 17

# 12V Up/Down actuator for door.
DOOR_SWITCH_PIN = 27

# 12V On/Off IR illuminator.
LIGHT_SWITCH_PIN = 22

# 5V input for opening/closing the door with button on site.
MANUAL_DOOR_BUTTON_PIN = 16

CFG_DIR=os.path.expanduser("~/.config/chickencoop")
CFG_NAME="cfg.json"

@dataclass
class Config:
    door: bool                         # True=door opened, False=door closed
    light: bool                        # True=on, False=off
    master: bool                       # True=on, False=off
    schedule_city: str = ""            # Closest city to the chicken coop to compute accurate sunrise/sunset times
    schedule_door_open: bool = False   # Is scheduled door opening enabled
    schedule_door_close: bool = False  # Is scheduled door closing enabled
    schedule_door_open_offset: int = 0  # Offset in opening the door on sunrise in minutes
    schedule_door_close_offset: int = 0 # Offset in closing the door on sunset in minutes

def default_cfg() -> Config:
    return Config(
        door=False,
        light=False,
        master=True,
        schedule_city="",
        schedule_door_open=False,
        schedule_door_close=False,
        schedule_door_open_offset=0,
        schedule_door_close_offset=0,
    )


def load_cfg() -> Config:
    path = os.path.join(CFG_DIR, CFG_NAME)
    if os.path.exists(path):
        f = open(path, "r")
        try:
            json_obj = json.load(f)
            f.close()
            return Config(**json_obj)
        except json.decoder.JSONDecodeError:
            logging.error('failed to load config from file. Using default')
            return default_cfg()

    return default_cfg()

def load_cfg_to_status() -> Status:
    cfg = load_cfg()
    return Status(
        door=cfg.door,
        light=cfg.light,
        master=cfg.master,
        temperature=0,
        humidity=0,
        current_datetime=datetime.min,
        last_manual_door_datetime=datetime.min,
        schedule_city=cfg.schedule_city,
        schedule_door_open=cfg.schedule_door_open,
        schedule_door_close=cfg.schedule_door_close,
        schedule_door_open_offset=cfg.schedule_door_open_offset,
        schedule_door_close_offset=cfg.schedule_door_close_offset,
    )


def save_cfg_from_status(status: Status):
    save_cfg(Config(
        door=status.door,
        light=status.light,
        master=status.master,
        schedule_city=status.schedule_city,
        schedule_door_open=status.schedule_door_open,
        schedule_door_close=status.schedule_door_close,
        schedule_door_open_offset=status.schedule_door_open_offset,
        schedule_door_close_offset=status.schedule_door_close_offset,
    ))


def save_cfg(cfg: Config):
    if not os.path.exists(CFG_DIR):
        os.mkdir(CFG_DIR)

    path = os.path.join(CFG_DIR, CFG_NAME)
    f = open(path, "w")
    f.write(json.dumps(asdict(cfg)))
    f.close()