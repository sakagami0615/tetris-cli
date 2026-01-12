from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class TetriminoMove:
    """テトリミノの移動を表すイミュータブルなデータクラス"""
    dr: int = 0
    dc: int = 0
    d_rotate: int = 0


class Command(ABC):
    """Command パターン: テトリミノへの操作を抽象化

    基本コマンド（移動・回転）と特殊コマンド（ハードドロップ）で
    異なるインターフェースを提供する
    """

    pass


class BasicCommand(Command):
    """基本的な移動・回転コマンド"""

    @abstractmethod
    def execute(self) -> TetriminoMove:
        """コマンドを実行し、移動情報を返す"""
        pass


class SpecialCommand(Command):
    """特殊なコマンド（ハードドロップなど）

    Gameオブジェクトに直接作用する必要があるコマンド
    """

    pass


class RotateCwCommand(BasicCommand):
    """時計回りに回転するコマンド"""

    def execute(self) -> TetriminoMove:
        return TetriminoMove(d_rotate=1)


class RotateCcwCommand(BasicCommand):
    """反時計回りに回転するコマンド"""

    def execute(self) -> TetriminoMove:
        return TetriminoMove(d_rotate=-1)


class MoveLeftCommand(BasicCommand):
    """左に移動するコマンド"""

    def execute(self) -> TetriminoMove:
        return TetriminoMove(dc=-1)


class MoveRightCommand(BasicCommand):
    """右に移動するコマンド"""

    def execute(self) -> TetriminoMove:
        return TetriminoMove(dc=1)


class MoveDownCommand(BasicCommand):
    """下に移動するコマンド"""

    def execute(self) -> TetriminoMove:
        return TetriminoMove(dr=1)


class MoveHardDropCommand(SpecialCommand):
    """ハードドロップするコマンド（着地するまで一気に落下）

    このコマンドはGameオブジェクトに直接作用するため、
    execute()メソッドを持たず、Game側で特別に処理される
    """

    pass


class NoOpTetriminoMoveCommand(BasicCommand):
    """何もしないコマンド"""

    def execute(self) -> TetriminoMove:
        return TetriminoMove()
