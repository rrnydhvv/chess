import chess
import chess.engine

# Giá trị điểm của từng quân cờ
PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0  # Vua không có giá trị cố định vì mất vua là thua
}

# Các ô trung tâm
CENTER_SQUARES = [chess.D4, chess.D5, chess.E4, chess.E5]


def evaluate_material(board):
    """ Tính toán tổng giá trị quân cờ của cả hai bên """
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = PIECE_VALUES[piece.piece_type]
            if piece.color == chess.WHITE:
                score += value
            else:
                score -= value
    return score


def evaluate_center_control(board):
    """ Đánh giá mức độ kiểm soát trung tâm """
    score = 0
    for square in CENTER_SQUARES:
        attackers_white = board.attackers(chess.WHITE, square)
        attackers_black = board.attackers(chess.BLACK, square)
        score += len(attackers_white) - len(attackers_black)
    return score


def evaluate_piece_development(board):
    """ Đánh giá mức độ phát triển quân cờ """
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
            if piece.color == chess.WHITE:
                score += 1
            else:
                score -= 1
    return score


def evaluate_king_safety(board):
    """ Kiểm tra độ an toàn của vua (nhập thành hay chưa) """
    score = 0
    if board.has_castling_rights(chess.WHITE):
        score += 2
    if board.has_castling_rights(chess.BLACK):
        score -= 2

       # Kiểm tra chiếu và chiếu bí
    if board.is_check():
        if board.turn == chess.WHITE:
            score -= 10  # Trừ điểm nếu trắng bị chiếu
        else:
            score += 10  # Cộng điểm nếu đen bị chiếu

    if board.is_checkmate():
        if board.turn == chess.WHITE:
            score -= 10000  # Trắng thua (chiếu bí) => điểm rất thấp
        else:
            score += 1000  # Đen thua (chiếu bí) => điểm rất cao

    return score


def evaluate_pawn_structure(board):
    """ Đánh giá cấu trúc tốt (tốt cô lập hoặc tốt chồng) """
    score = 0
    white_pawn_files = set()
    black_pawn_files = set()

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type == chess.PAWN:
            if piece.color == chess.WHITE:
                white_pawn_files.add(chess.square_file(square))
            else:
                black_pawn_files.add(chess.square_file(square))

    # Nếu tốt bị cô lập (chỉ có một mình trên cột)
    score += len(white_pawn_files) - len(black_pawn_files)
    return score


def evaluate_mobility(board):
    """ Đánh giá mức độ di chuyển của quân cờ """
    return len(list(board.legal_moves))


def evaluate_board(board):
    """ Tổng hợp tất cả các yếu tố để đánh giá vị trí hiện tại """
    material = evaluate_material(board)
    center_control = evaluate_center_control(board)
    development = evaluate_piece_development(board)
    king_safety = evaluate_king_safety(board)
    pawn_structure = evaluate_pawn_structure(board)
    mobility = evaluate_mobility(board)

    total_score = (material * 10 +
                   center_control * 5 +
                   development * 3 +
                   king_safety * 5 +
                   pawn_structure * 2 +
                   mobility * 1)

    return total_score


def minimax(board, depth, alpha, beta, is_maximizing):
    """ Thuật toán Minimax với Alpha-Beta Pruning """
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    legal_moves = list(board.legal_moves)

    if is_maximizing:
        max_eval = float('-inf')
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Cắt tỉa Beta
        return max_eval
    else:
        min_eval = float('inf')
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Cắt tỉa Alpha
        return min_eval


def find_best_move(board, depth=3):
    """ Tìm nước đi tối ưu dựa trên Minimax """
    best_move = None
    best_value = float('-inf')
    alpha = float('-inf')
    beta = float('inf')

    for move in board.legal_moves:
        board.push(move)
        board_value = minimax(board, depth - 1, alpha, beta, False)
        board.pop()

        if board_value > best_value:
            best_value = board_value
            best_move = move

    return best_move
