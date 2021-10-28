import threading
import time


# I don't have enough knowledge to read certain info from official
# Python nor Flask documents...
# This code comes from Qiita:
# https://qiita.com/juri-t/items/5cec3822e168215aff49
class PartyColor(threading.Thread):
    HUE_INC_UNIT = 5000
    COLOR_CHANGE_INTERVAL_SEC = 3.0

    def __init__(self, send_json_fn):
        super(PartyColor, self).__init__()
        self.send_json_fn = send_json_fn
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        # NOTE: default transition time is 400ms:
        # https://developers.meethue.com/develop/application-design-guidance/watch-that-transition-time/
        while True:
            if self.stop_event.is_set():
                break

            self.send_json_fn({"hue_inc": self.HUE_INC_UNIT})
            time.sleep(self.COLOR_CHANGE_INTERVAL_SEC)
