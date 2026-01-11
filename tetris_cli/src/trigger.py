import time


class TimeTrigger:
    last_unix_time: float = time.time()
    unix_time_interval: float

    def __init__(self, unix_time_interval: float):
        self.unix_time_interval = unix_time_interval

    def is_trigger(self) -> bool:
        curr_unix_time: float = time.time()
        if curr_unix_time - self.last_unix_time >= self.unix_time_interval:
            self.last_unix_time = curr_unix_time
            return True
        else:
            return False
