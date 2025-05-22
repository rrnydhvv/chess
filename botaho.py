import random
import time
import chess


def random_move(board: chess.Board) -> chess.Move:
    """Trả về một nước đi hợp lệ ngẫu nhiên sau khi chờ ngẫu nhiên."""
    time.sleep(random.uniform(0.3, 1.5))  # Chờ từ 0.3 đến 1.5 giây
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return None
    return random.choice(legal_moves)
