import chess
import chess.engine


def move(board, time=2.0):
    # Stockfish suy nghĩ 2 giây
    return engine.play(board, chess.engine.Limit(time)).move


STOCKFISH_PATH = "stockfish-windows-x86-64-avx2/stockfish/stockfish-windows-x86-64-avx2.exe"
engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
