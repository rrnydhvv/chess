import chess
import math

# 1. Định nghĩa giá trị vật chất (đơn vị tính theo centipawn, 100 = 1 điểm)
piece_values = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0  # Vua không được tính vì mất vua là thua cuộc
}

# 2. Các bảng định vị (piece-square tables) cho các quân cờ (cho phía trắng)
# Các giá trị này được lấy theo một số nguồn tham khảo; bạn có thể điều chỉnh để phù hợp với chiến lược của mình.
pawn_table = [
    0,   0,   0,   0,   0,   0,   0,   0,
    5,  10,  10, -20, -20, 10,  10,   5,
    5,  -5, -10,   0,   0, -10,  -5,   5,
    0,   0,   0,  20,  20,  0,   0,   0,
    5,   5,  10,  25,  25, 10,   5,   5,
    10,  10,  20,  30,  30, 20,  10,  10,
    50,  50,  50,  50,  50, 50,  50,  50,
    0,   0,   0,   0,   0,  0,   0,   0
]

knight_table = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20,   0,   5,   5,   0, -20, -40,
    -30,   5,  10,  15,  15,  10,   5, -30,
    -30,   0,  15,  20,  20,  15,   0, -30,
    -30,   5,  15,  20,  20,  15,   5, -30,
    -30,   0,  10,  15,  15,  10,   0, -30,
    -40, -20,   0,   0,   0,   0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
]

bishop_table = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10,   5,   0,   0,   0,   0,   5, -10,
    -10,  10,  10,  10,  10,  10,  10, -10,
    -10,   0,  10,  10,  10,  10,   0, -10,
    -10,   5,   5,  10,  10,   5,   5, -10,
    -10,   0,   5,  10,  10,   5,   0, -10,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20
]

rook_table = [
    0,   0,   0,   5,   5,   0,   0,   0,
    -5,   0,   0,   0,   0,   0,   0,  -5,
    -5,   0,   0,   0,   0,   0,   0,  -5,
    -5,   0,   0,   0,   0,   0,   0,  -5,
    -5,   0,   0,   0,   0,   0,   0,  -5,
    -5,   0,   0,   0,   0,   0,   0,  -5,
    5,  10,  10,  10,  10,  10,  10,   5,
    0,   0,   0,   0,   0,   0,   0,   0
]

queen_table = [
    -20, -10, -10,  -5,  -5, -10, -10, -20,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -10,   0,   5,   5,   5,   5,   0, -10,
    -5,   0,   5,   5,   5,   5,   0,  -5,
    0,   0,   5,   5,   5,   5,   0,  -5,
    -10,   5,   5,   5,   5,   5,   0, -10,
    -10,   0,   5,   0,   0,   0,   0, -10,
    -20, -10, -10,  -5,  -5, -10, -10, -20
]

king_table = [
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20,   20,   0,    0,    0,    0,  20,  20,
    20,   30,  10,    0,    0,   10,  30,  20
]

# 3. Hàm đánh giá vật chất


def evaluate_material(board: chess.Board) -> int:
    material = 0
    for square, piece in board.piece_map().items():
        value = piece_values[piece.piece_type]
        material += value if piece.color == chess.WHITE else -value
    return material

# 4. Hàm đánh giá vị trí dựa trên piece-square tables


def evaluate_positional(board: chess.Board) -> int:
    positional = 0
    for square, piece in board.piece_map().items():
        if piece.piece_type == chess.PAWN:
            table = pawn_table
        elif piece.piece_type == chess.KNIGHT:
            table = knight_table
        elif piece.piece_type == chess.BISHOP:
            table = bishop_table
        elif piece.piece_type == chess.ROOK:
            table = rook_table
        elif piece.piece_type == chess.QUEEN:
            table = queen_table
        elif piece.piece_type == chess.KING:
            table = king_table
        # Với quân trắng, dùng trực tiếp giá trị tại square;
        # Với quân đen, "lật" bảng bằng chess.square_mirror
        table_value = table[square] if piece.color == chess.WHITE else table[chess.square_mirror(
            square)]
        positional += table_value if piece.color == chess.WHITE else -table_value
    return positional

# 5. Hàm đánh giá khả năng di chuyển (mobility)


def evaluate_mobility(board: chess.Board) -> float:
    # Tính số nước đi hợp lệ cho cả hai bên
    board_copy = board.copy()
    board_copy.turn = chess.WHITE
    white_moves = len(list(board_copy.legal_moves))
    board_copy.turn = chess.BLACK
    black_moves = len(list(board_copy.legal_moves))
    # Hệ số nhỏ để không "lấn át" đánh giá vật chất và vị trí
    return 10 * (white_moves - black_moves)

# 6. Hàm đánh giá an toàn của vua


def evaluate_king_safety(board: chess.Board) -> float:
    safety = 0
    # Đánh giá đơn giản: tính số "lá chắn" của tốt phía trước vua
    for color in [chess.WHITE, chess.BLACK]:
        king_square = board.king(color)
        if king_square is None:
            continue
        king_file = chess.square_file(king_square)
        king_rank = chess.square_rank(king_square)
        pawn_shield = 0
        # Với quân trắng, tốt phía trước nằm ở hàng tiếp theo; với đen thì ngược lại
        forward = 1 if color == chess.WHITE else -1
        for df in [-1, 0, 1]:
            file = king_file + df
            rank = king_rank + forward
            if 0 <= file <= 7 and 0 <= rank <= 7:
                square = chess.square(file, rank)
                piece = board.piece_at(square)
                if piece and piece.piece_type == chess.PAWN and piece.color == color:
                    pawn_shield += 1
        if color == chess.WHITE:
            safety += 15 * pawn_shield
        else:
            safety -= 15 * pawn_shield
    return safety

# 7. Hàm đánh giá cấu trúc tốt (doubled, isolated)


def evaluate_pawn_structure(board: chess.Board) -> float:
    white_penalty = 0
    black_penalty = 0
    for color in [chess.WHITE, chess.BLACK]:
        pawns = board.pieces(chess.PAWN, color)
        files = [chess.square_file(sq) for sq in pawns]
        penalty = 0
        # Phạt các tốt gấp đôi trên 1 cột
        for file in range(8):
            count = files.count(file)
            if count > 1:
                # phạt 20 centipawn cho mỗi tốt gấp đôi
                penalty += (count - 1) * 20
        # Phạt tốt đơn lẻ (isolated): nếu không có đồng minh ở cột kề
        for pawn in pawns:
            file = chess.square_file(pawn)
            if (file - 1 not in files) and (file + 1 not in files):
                penalty += 15  # phạt 15 centipawn
        if color == chess.WHITE:
            white_penalty = penalty
        else:
            black_penalty = penalty
    # Tính hiệu lệch, vì tốt kém làm giảm thế cho bên đó
    return -white_penalty + black_penalty

# 8. Hàm đánh giá tổng hợp


def evaluate_board(board: chess.Board) -> float:
    """
    Hàm đánh giá tổng hợp thế cờ.
    Giá trị dương cho thế cờ nghiêng về trắng,
    giá trị âm cho thế cờ nghiêng về đen.
    """
    eval_material = evaluate_material(board)
    eval_positional = evaluate_positional(board)
    eval_mobility = evaluate_mobility(board)
    eval_king_safety = evaluate_king_safety(board)
    eval_pawn_structure = evaluate_pawn_structure(board)

    # Tổng hợp với các hệ số trọng số có thể điều chỉnh
    total_evaluation = (eval_material +
                        eval_positional +
                        eval_mobility +
                        eval_king_safety +
                        eval_pawn_structure)
    return total_evaluation


def minimax(board: chess.Board, depth: int, alpha: float, beta: float, maximizing_player: bool) -> float:
    """
    Thuật toán minimax có cắt tỉa alpha-beta.
    Nếu depth = 0 hoặc trò chơi kết thúc, trả về điểm đánh giá.
    """
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximizing_player:
        max_eval = -math.inf
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # cắt tỉa beta
        return max_eval
    else:
        min_eval = math.inf
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # cắt tỉa alpha
        return min_eval


def find_best_move(board: chess.Board, depth: int = 3):
    """
    Hàm tìm nước đi tốt nhất dựa trên thuật toán minimax:
    - Nếu lượt đi là của quân trắng (maximizing player), ta chọn nước đi có điểm đánh giá cao nhất.
    - Nếu lượt đi là của quân đen (minimizing player), ta chọn nước đi có điểm đánh giá thấp nhất.

    Trả về một tuple (nước đi tốt nhất, điểm đánh giá của nước đi đó).
    """
    best_move = None

    if board.turn == chess.WHITE:
        best_eval = -math.inf
        for move in board.legal_moves:
            board.push(move)
            move_eval = minimax(board, depth - 1, -math.inf, math.inf, False)
            board.pop()
            if move_eval > best_eval:
                best_eval = move_eval
                best_move = move
    else:
        best_eval = math.inf
        for move in board.legal_moves:
            board.push(move)
            move_eval = minimax(board, depth - 1, -math.inf, math.inf, True)
            board.pop()
            if move_eval < best_eval:
                best_eval = move_eval
                best_move = move

    return best_move
