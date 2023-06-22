import json
import os
from dataclasses import dataclass
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
MANUAL_DOOR_BUTTON_PIN = 5

CFG_DIR="~/.config/chickencoop"
CFG_NAME="cfg.json"

@dataclass
class Config:
    door: bool # True=up, False=down
    light: bool # True=on, False=off
    master: bool # True=on, False=off

def default_cfg() -> Config:
    return Config(
        door=False,
        light=False,
        master=True,
    )


def load_cfg() -> Config:
    path = os.path.join(CFG_DIR, CFG_NAME)
    if os.path.exists(path):
        f = open(path, "r")
        json_obj = json.loads(f)
        f.close()
        return Config(**json_obj)

    return default_cfg()

def load_cfg_to_status() -> Status:
    cfg = load_cfg()
    return Status(
        door=cfg.door,
        light=cfg.light,
        master=cfg.master,
    )


def save_cfg_from_status(status: Status):
    save_cfg(Config(
        door=status.door,
        status=status.light,
        master=status.master,
    ))


def save_cfg(cfg: Config):
    if not os.path.exists(CFG_DIR):
        os.mkdir(CFG_DIR)

    path = os.path.join(CFG_DIR, CFG_NAME)
    f = open(path, "w")
    f.write(json.dumps(cfg))
    f.close()