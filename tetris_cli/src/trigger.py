import time
from dataclasses import dataclass, field


@dataclass
class TimeTrigger:
    """時間ベースのトリガークラス"""
    interval: float
    _last_time: float = field(default_factory=time.time, init=False)

    def is_trigger(self) -> bool:
        """指定間隔が経過したかチェック"""
        current_time = time.time()
        if current_time - self._last_time >= self.interval:
            self._last_time = current_time
            return True
        return False

    def reset(self) -> None:
        """トリガーをリセット"""
        self._last_time = time.time()
