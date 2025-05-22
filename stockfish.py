import chess
import chess.engine
import subprocess


def move(board, time=1.5):
    return engine.play(board, chess.engine.Limit(time)).move


STOCKFISH_PATH = "stockfish-windows-x86-64-avx2/stockfish/stockfish-windows-x86-64-avx2.exe"
engine = chess.engine.SimpleEngine.popen_uci(
    STOCKFISH_PATH,
    creationflags=subprocess.CREATE_NO_WINDOW  # Ẩn cửa sổ console trên Windows
)
