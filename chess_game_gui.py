import time
import os
import subprocess
import sys
import botngu
import main_menu as m
# Hàm kiểm tra và cài đặt thư viện nếu chưa có


def install_and_import(package):
    try:
        __import__(package)
    except ImportError:
        print(f"{package} chưa được cài đặt. Đang tiến hành cài đặt...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package])
        print(f"{package} đã được cài đặt thành công!")


# Kiểm tra và cài đặt các thư viện cần thiết
install_and_import("pygame")
install_and_import("chess")


# Sau khi cài đặt xong, import bình thường
import pygame
import chess.engine
import chess

# Khởi tạo pygame
pygame.init()

# Cấu hình kích thước cửa sổ phù hợp với kích thước ảnh quân cờ 60x60
SQUARE_SIZE = 60
WIDTH, HEIGHT = SQUARE_SIZE * 8, SQUARE_SIZE * 8
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (240, 217, 181)
DARK_BROWN = (181, 136, 99)
GRAY = (200, 200, 200)
HOVER_COLOR = (170, 170, 170)  # Màu khi hover
CLICK_COLOR = (150, 150, 150)  # Màu khi click
HIGHLIGHT_COLOR = (100, 255, 100)  # Màu highlight khi chọn quân cờ
TARGET_COLOR = (255, 255, 100)  # Màu highlight cho ô có thể đi
CAPTURE_COLOR = (255, 100, 100)  # Màu highlight cho ô có thể ăn quân
PROMOTION_HOVER = (255, 255, 100)  # Màu nền khi hover button phong cấp
LAST_MOVE_COLOR = (173, 216, 230)  # Màu ô của nước đi cuối cùng

# Load hình ảnh quân cờ
piece_images = {}
piece_symbols = ['wp', 'wr', 'wn', 'wb', 'wq',
                 'wk', 'bp', 'br', 'bn', 'bb', 'bq', 'bk']
for piece in piece_symbols:
    piece_images[piece] = pygame.transform.scale(
        pygame.image.load(f"images/{piece}.png"), (SQUARE_SIZE, SQUARE_SIZE))

# Bàn cờ
board = chess.Board()
selected_square = None
highlighted_squares = []
last_move = None  # Lưu nước đi cuối cùng
mode = None  # Lưu chế độ chơi ('PVP' hoặc 'BOT')


def draw_board():
    flipped = bot_color == chess.WHITE  # Nếu bot chơi trắng, đảo ngược bàn cờ
    for row in range(8):
        for col in range(8):
            draw_row = 7 - row if flipped else row
            draw_col = 7 - col if flipped else col
            square = chess.square(draw_col, 7 - draw_row)
            color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN

            if last_move:
                if square == last_move.from_square or square == last_move.to_square:
                    color = LAST_MOVE_COLOR

            if square in highlighted_squares:
                if board.piece_at(square):
                    if board.piece_at(square).color != board.piece_at(selected_square).color:
                        color = CAPTURE_COLOR
                else:
                    if board.piece_at(selected_square).piece_type == chess.PAWN and chess.square_file(square) != chess.square_file(selected_square):
                        color = CAPTURE_COLOR
                    else:
                        color = TARGET_COLOR
            elif square == selected_square:
                color = HIGHLIGHT_COLOR
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE,
                             row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def draw_pieces():
    flipped = bot_color == chess.WHITE
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_color = 'w' if piece.color == chess.WHITE else 'b'
            piece_type = piece.symbol().lower()
            piece_image = piece_images[f"{piece_color}{piece_type}"]
            col, row = chess.square_file(square), chess.square_rank(square)
            if flipped:
                col, row = 7 - col, 7 - row
            screen.blit(piece_image, (col * SQUARE_SIZE,
                        (7 - row) * SQUARE_SIZE))


def get_square_from_pos(pos):
    x, y = pos
    flipped = bot_color == chess.WHITE
    col = x // SQUARE_SIZE
    row = y // SQUARE_SIZE
    if flipped:
        col, row = 7 - col, 7 - row
    return chess.square(col, 7 - row)


def pawn_promotion(color):
    promotion_pieces = ['q', 'r', 'b', 'n']  # Hậu, Xe, Tượng, Mã
    piece_images_display = [
        piece_images[f"{color}{p}"] for p in promotion_pieces]
    button_width, button_height = 60, 60
    x = WIDTH // 2 - 2 * button_width
    y = HEIGHT // 2 - button_height // 2

    while True:
        for i, img in enumerate(piece_images_display):
            button_rect = pygame.Rect(
                x + i * button_width, y, button_width, button_height)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if button_rect.collidepoint(mouse_x, mouse_y):
                pygame.draw.rect(screen, PROMOTION_HOVER, button_rect)
            else:
                pygame.draw.rect(screen, WHITE, button_rect)
            pygame.draw.rect(screen, BLACK, button_rect, 3)
            screen.blit(img, (x + i * button_width, y))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate([pygame.Rect(x + j * button_width, y, button_width, button_height) for j in range(4)]):
                    if rect.collidepoint(event.pos):
                        return promotion_pieces[i]


def display_game_over():
    global last_move
    if board.is_checkmate():
        background_color = WHITE if board.turn == chess.BLACK else BLACK
        text_color = BLACK if board.turn == chess.BLACK else WHITE
        text = "Victory: " + ("White" if board.turn ==
                              chess.BLACK else "Black")
    elif board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves() or board.is_fivefold_repetition():
        screen.fill(BLACK, (0, 0, WIDTH, HEIGHT // 2))
        screen.fill(WHITE, (0, HEIGHT // 2, WIDTH, HEIGHT // 2))
        text_color = WHITE
        text = "Draw!"
    else:
        text_color = BLACK
        background_color = WHITE
        text = "Game Over!"

    if not (board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves() or board.is_fivefold_repetition()):
        screen.fill(background_color)

    font = pygame.font.Font(None, 36)
    text_surface = font.render(text, True, text_color)
    screen.blit(text_surface, (WIDTH//2 -
                text_surface.get_width()//2, HEIGHT//3))

    button_font = pygame.font.Font(None, 32)
    button_width, button_height = 150, 50
    button_spacing = 20

    new_game_x = (WIDTH - (2 * button_width + button_spacing)) // 2
    exit_x = new_game_x + button_width + button_spacing
    button_y = HEIGHT // 2 + 50

    new_game_button = pygame.Rect(
        new_game_x, button_y, button_width, button_height)
    exit_button = pygame.Rect(exit_x, button_y, button_width, button_height)

    if board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves() or board.is_fivefold_repetition():
        pygame.draw.rect(screen, BLACK, new_game_button, 3)
        pygame.draw.rect(screen, BLACK, exit_button, 3)
        new_game_text_color = BLACK
        exit_text_color = BLACK
    else:
        pygame.draw.rect(screen, text_color, new_game_button, 3)
        pygame.draw.rect(screen, text_color, exit_button, 3)
        new_game_text_color = text_color
        exit_text_color = text_color

    new_game_text = button_font.render("New Game", True, new_game_text_color)
    exit_text = button_font.render("Exit", True, exit_text_color)

    screen.blit(new_game_text, (new_game_button.x + (button_width - new_game_text.get_width()
                                                     ) // 2, new_game_button.y + (button_height - new_game_text.get_height()) // 2))
    screen.blit(exit_text, (exit_button.x + (button_width - exit_text.get_width()) //
                2, exit_button.y + (button_height - exit_text.get_height()) // 2))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                os._exit(0)  # Thoát hoàn toàn chương trình và kill terminal
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if new_game_button.collidepoint(event.pos):
                    board.reset()
                    last_move = None
                    waiting = False
                elif exit_button.collidepoint(event.pos):
                    pygame.quit()
                    os._exit(0)  # Kill terminal khi nhấn Exit


def main():
    global selected_square, highlighted_squares, last_move, mode, bot_type, bot_color
    mode, bot_type, bot_color = m.main_menu()
    running = True
    if mode is None and bot_type is None and bot_color is None:
        running = False
        return
    if bot_type == "Stockfish":
        STOCKFISH_PATH = "stockfish-windows-x86-64-avx2/stockfish/stockfish-windows-x86-64-avx2.exe"
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    while running:
        screen.fill(WHITE)
        if board.is_game_over():
            draw_board()
            draw_pieces()
            pygame.display.flip()
            time.sleep(2)
            display_game_over()
        draw_board()
        draw_pieces()
        pygame.display.flip()
        # Nếu đến lượt bot, thực hiện nước đi tự động
        if mode == "Bot" and board.turn == bot_color:
            if bot_type == "Botngu":
                move = botngu.find_best_move(board, 3)
            else:
                result = engine.play(board, chess.engine.Limit(
                    time=2.0))  # Stockfish suy nghĩ 2 giây
                move = result.move
            if move:
                board.push(move)
                last_move = move
            continue  # Bỏ qua xử lý sự kiện người chơi vì là lượt của bot
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                square = get_square_from_pos(event.pos)
                if selected_square is None:
                    if board.piece_at(square):
                        selected_square = square
                        highlighted_squares = [
                            move.to_square for move in board.legal_moves if move.from_square == selected_square]
                else:
                    move = chess.Move(selected_square, square)
                    if board.piece_at(selected_square) and board.piece_at(selected_square).piece_type == chess.PAWN:
                        if chess.square_rank(square) == 0 or chess.square_rank(square) == 7:
                            move = chess.Move(
                                selected_square, square, promotion=chess.QUEEN)
                            if move in board.legal_moves:
                                promoted_piece = pawn_promotion('w' if board.piece_at(
                                    selected_square).color == chess.WHITE else 'b')
                                move = chess.Move(
                                    selected_square, square, promotion=chess.PIECE_SYMBOLS.index(promoted_piece))
                    if move in board.legal_moves:
                        board.push(move)
                        last_move = move  # Cập nhật nước đi cuối cùng
                    selected_square = None
                    highlighted_squares = []
    pygame.quit()


if __name__ == "__main__":
    main()
