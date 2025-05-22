import chess
import math

# 1. Định nghĩa giá trị vật chất (đơn vị centipawn, 100 = 1 điểm)
piece_values = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0  # Không tính giá trị của vua vì mất vua tức là thua cuộc
}

# 2. Các bảng định vị (piece-square tables) cho từng quân cờ (cho phía trắng)
pawn_table = [
    0,   0,   0,   0,   0,   0,   0,   0,
    5,  10,  5, -20, -20, 5,  10,   5,
    5,  -5, 10,   0,   0, 10,  -5,   5,
    0,   0,   0,  20,  20,  0,   0,   0,
    5,   5,  10,  25,  25, 10,   5,   5,
    10,  10,  20,  30,  30, 20,  10,  10,
    50,  50,  50,  50,  50, 50,  50,  50,
    70,   70,   70,   70,   70,  70,   70,   70
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
        # Với quân trắng dùng giá trị trực tiếp, còn quân đen "lật" bảng
        table_value = table[square] if piece.color == chess.WHITE else table[chess.square_mirror(
            square)]
        positional += table_value if piece.color == chess.WHITE else -table_value
    return positional

# 5. Hàm đánh giá khả năng di chuyển (mobility)


def evaluate_mobility(board: chess.Board) -> float:
    board_copy = board.copy()
    board_copy.turn = chess.WHITE
    white_moves = len(list(board_copy.legal_moves))
    board_copy.turn = chess.BLACK
    black_moves = len(list(board_copy.legal_moves))
    return 10 * (white_moves - black_moves)

# 6. Hàm đánh giá an toàn của vua


def evaluate_king_safety(board: chess.Board) -> float:
    safety = 0
    for color in [chess.WHITE, chess.BLACK]:
        king_square = board.king(color)
        if king_square is None:
            continue
        king_file = chess.square_file(king_square)
        king_rank = chess.square_rank(king_square)
        pawn_shield = 0
        forward = 1 if color == chess.WHITE else -1
        for df in [-1, 0, 1]:
            file = king_file + df
            rank = king_rank + forward
            if 0 <= file <= 7 and 0 <= rank <= 7:
                square = chess.square(file, rank)
                piece = board.piece_at(square)
                if piece and piece.piece_type == chess.PAWN and piece.color == color:
                    pawn_shield += 1
        safety += 15 * pawn_shield if color == chess.WHITE else -15 * pawn_shield
    return safety

# 7. Hàm đánh giá cấu trúc tốt (đánh giá các tốt gấp đôi và tốt đơn lẻ)


def evaluate_pawn_structure(board: chess.Board) -> float:
    white_penalty = 0
    black_penalty = 0
    for color in [chess.WHITE, chess.BLACK]:
        pawns = board.pieces(chess.PAWN, color)
        files = [chess.square_file(sq) for sq in pawns]
        penalty = 0
        # Phạt các tốt gấp đôi
        for file in range(8):
            count = files.count(file)
            if count > 1:
                penalty += (count - 1) * 20
        # Phạt tốt đơn lẻ (isolated)
        for pawn in pawns:
            file = chess.square_file(pawn)
            if (file - 1 not in files) and (file + 1 not in files):
                penalty += 15
        if color == chess.WHITE:
            white_penalty = penalty
        else:
            black_penalty = penalty
    return -white_penalty + black_penalty

# 8. Hàm đánh giá tổng hợp, bổ sung yếu tố chiếu bí


def evaluate_board(board: chess.Board) -> float:
    # Nếu chiếu bí: trả về giá trị cực đại (nếu đối phương bị chiếu bí) hoặc cực tiểu
    if board.is_checkmate():
        # Ở trạng thái chiếu bí, bên nào có lượt đi hiện tại là bên bị thua
        return -100000 if board.turn == chess.WHITE else 100000
    # Nếu hòa hoặc không đủ lực đánh, trả về 0
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    eval_material = evaluate_material(board)
    eval_positional = evaluate_positional(board)
    eval_mobility = evaluate_mobility(board)
    eval_king_safety = evaluate_king_safety(board)
    eval_pawn_structure = evaluate_pawn_structure(board)

    total_evaluation = (eval_material +
                        eval_positional +
                        eval_mobility +
                        eval_king_safety +
                        eval_pawn_structure)
    return total_evaluation


def minimax(board: chess.Board, depth: int, alpha: float, beta: float, maximizing_player: bool) -> float:
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximizing_player:
        max_eval = -math.inf
        for move in board.legal_moves:
            # Nếu nước đi là phong cấp và không có loại quân được chỉ định, ta mặc định phong hậu
            if board.is_pseudo_legal(move) and board.piece_at(move.from_square).piece_type == chess.PAWN and \
               (chess.square_rank(move.to_square) == 7 or chess.square_rank(move.to_square) == 0) and move.promotion is None:
                move = chess.Move(move.from_square,
                                  move.to_square, promotion=chess.QUEEN)

            board.push(move)
            eval = minimax(board, depth - 1, alpha,
                           beta, not maximizing_player)
            board.pop()

            if maximizing_player:
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for move in board.legal_moves:
            if board.is_pseudo_legal(move) and board.piece_at(move.from_square).piece_type == chess.PAWN and \
               (chess.square_rank(move.to_square) == 7 or chess.square_rank(move.to_square) == 0) and move.promotion is None:
                move = chess.Move(move.from_square,
                                  move.to_square, promotion=chess.QUEEN)

            board.push(move)
            eval = minimax(board, depth - 1, alpha,
                           beta, not maximizing_player)
            board.pop()

            if not maximizing_player:
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval


def find_best_move(board: chess.Board, depth: int = 3):
    best_move = None

    if board.turn == chess.WHITE:
        best_eval = -math.inf
        for move in board.legal_moves:
            if board.is_pseudo_legal(move) and board.piece_at(move.from_square).piece_type == chess.PAWN and \
               (chess.square_rank(move.to_square) == 7 or chess.square_rank(move.to_square) == 0) and move.promotion is None:
                move = chess.Move(move.from_square,
                                  move.to_square, promotion=chess.QUEEN)

            board.push(move)
            move_eval = minimax(board, depth - 1, -math.inf, math.inf, False)
            board.pop()
            if move_eval > best_eval:
                best_eval = move_eval
                best_move = move
    else:
        best_eval = math.inf
        for move in board.legal_moves:
            if board.is_pseudo_legal(move) and board.piece_at(move.from_square).piece_type == chess.PAWN and \
               (chess.square_rank(move.to_square) == 7 or chess.square_rank(move.to_square) == 0) and move.promotion is None:
                move = chess.Move(move.from_square,
                                  move.to_square, promotion=chess.QUEEN)

            board.push(move)
            move_eval = minimax(board, depth - 1, -math.inf, math.inf, True)
            board.pop()
            if move_eval < best_eval:
                best_eval = move_eval
                best_move = move

    return best_move
