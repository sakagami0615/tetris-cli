"""アプリケーションの初期設定"""
import sys
from colorama import init


INF = sys.maxsize

# coloramaを初期化（Windowsでも ANSIエスケープシーケンスが動作するようにする）
init(autoreset=False)
