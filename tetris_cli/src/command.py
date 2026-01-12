from abc import ABC, abstractmethod
from dataclasses import dataclass

from tetris_cli.src.tetrimino import ActiveTetrimino


@dataclass(frozen=True)
class TetriminoMove:
    """テトリミノの移動を表すイミュータブルなデータクラス"""
    dr: int = 0
    dc: int = 0
    d_rotate: int = 0


class Command(ABC):
    """Command パターン: テトリミノへの操作を抽象化"""

    @abstractmethod
    def execute(self) -> TetriminoMove:
        """コマンドを実行し、移動情報を返す"""
        pass


class RotateCommand(Command):
    """時計回りに回転するコマンド"""

    def execute(self) -> TetriminoMove:
        return TetriminoMove(d_rotate=1)


class MoveLeftCommand(Command):
    """左に移動するコマンド"""

    def execute(self) -> TetriminoMove:
        return TetriminoMove(dc=-1)


class MoveRightCommand(Command):
    """右に移動するコマンド"""

    def execute(self) -> TetriminoMove:
        return TetriminoMove(dc=1)


class MoveDownCommand(Command):
    """下に移動するコマンド"""

    def execute(self) -> TetriminoMove:
        return TetriminoMove(dr=1)


class NoOpTetriminoMoveCommand(Command):
    """何もしないコマンド"""

    def execute(self) -> TetriminoMove:
        return TetriminoMove()
