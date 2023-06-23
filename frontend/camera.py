import io
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

    picam2 = Picamera2()
    picam2.configure(picam2.create_video_configuration(main={"size": (1920, 1080)},controls={"FrameDurationLimits": (1000000, 1000000)}))
    picam2.start_recording(JpegEncoder(), FileOutput(output))
