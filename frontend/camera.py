import io
import os
from libcamera import Transform, controls
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
from threading import Condition

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

output = StreamingOutput()

def init_camera():
    global output

    # XXX: Turn on HDR since picamera2/libcamera python bindings don't support this yet.
    os.system("v4l2-ctl --set-ctrl wide_dynamic_range=1 -d /dev/v4l-subdev0")

    picam2 = Picamera2()
    picam2.configure(picam2.create_video_configuration(
        main={"size": (1920, 1080)},
        transform=Transform(vflip=False, hflip=False), # No rotation.
        controls={"FrameDurationLimits": (1000000, 1000000), "AfMode": controls.AfModeEnum.Manual, "LensPosition": 0.0}
    ))
    picam2.start_recording(JpegEncoder(), FileOutput(output))
