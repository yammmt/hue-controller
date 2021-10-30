import threading
import time


# I don't have enough knowledge to read certain info from official
# Python nor Flask documents...
# This code comes from Qiita:
# https://qiita.com/juri-t/items/5cec3822e168215aff49
class PartyColor(threading.Thread):
    def __init__(
        self,
        send_json_fn,
        hue_unit,
        interval_s
    ):
        super(PartyColor, self).__init__()
        self.send_json_fn = send_json_fn
        self.hue_unit = hue_unit
        self.interval_s = interval_s
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        # NOTE: default transition time is 400ms:
        # https://developers.meethue.com/develop/application-design-guidance/watch-that-transition-time/
        while True:
            if self.stop_event.is_set():
                break

            self.send_json_fn({"hue_inc": self.hue_unit})
            time.sleep(self.interval_s)
