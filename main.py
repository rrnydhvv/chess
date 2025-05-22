from menu_gui import main_menu, esc_menu, game_over_menu, select_game_mode, Buttons, Themes
import pygame
import chess
import stockfish
import botbaka
import os
import botaho
import threading

SQUARE_SIZE = 60
WIDTH, HEIGHT = SQUARE_SIZE * 8, SQUARE_SIZE * 8


class Bot:
    def __init__(self, bot_type):
        self.bot_type = bot_type

    def make_move(self, board):
        if self.bot_type == "BotBaka":
            return botbaka.find_best_move(board, 3)
        elif self.bot_type == "Stockfish":
            return stockfish.move(board)
        elif self.bot_type == "BotAho":
            return botaho.random_move(board)


class BotWorker(threading.Thread):
    def __init__(self, bot, board, callback):
        super().__init__()
        self.bot = bot
        self.board = board.copy()
        self.callback = callback

    def run(self):
        move = self.bot.make_move(self.board)
        self.callback(move)


class Chess_Game:
    def __init__(self, opt1=None, opt2=None, opt3=None, theme=Themes("default")):
        self.board = chess.Board()
        self.opt1 = opt1  # Chế độ chơi (PvP hoặc Bot)
        self.opt2 = opt2  # Loại bot (BotBaka, BotAho, Stockfish)
        self.opt3 = opt3  # Màu của bot (chess.WHITE hoặc chess.BLACK)
        self.theme = theme

        self.piece_images = {}
        self.piece_symbols = ['wp', 'wr', 'wn', 'wb', 'wq', 'wk',
                              'bp', 'br', 'bn', 'bb', 'bq', 'bk']

        self.load_images()

    def new_Game(self):
        self.board.reset()

    def undo(self):
        """Undo the last move if the move stack is not empty."""
        if self.board.move_stack:
            self.board.pop()
        else:
            print("No moves to undo!")

    def undo_move(self):
        """Undo the last move and handle bot moves in bot mode."""
        self.undo()
        if self.opt1 == "bot":
            # If it's the bot's turn after undoing, undo one more move
            if self.opt3 == self.board.turn:
                self.undo()

    def display_move_history(self):
        pass

    def load_images(self):
        """Tải ảnh quân cờ vào bộ nhớ."""
        for piece in self.piece_symbols:
            images_path = f"images/pieces/{piece}.png"
            try:
                self.piece_images[piece] = pygame.transform.scale(
                    pygame.image.load(images_path), (SQUARE_SIZE, SQUARE_SIZE)
                )
            except pygame.error as e:
                print(f"Lỗi khi tải ảnh {piece}: {e}")

    def pawn_promotion(self, color, screen):
        promotion_pieces = ['q', 'r', 'b', 'n']  # Hậu, Xe, Tượng, Mã
        piece_images_display = [
            self.piece_images[f"{color}{p}"] for p in promotion_pieces]
        button_width, button_height = 60, 60
        x = 10 + WIDTH // 2 - 2 * button_width
        y = 60 + HEIGHT // 2 - button_height // 2

        while True:
            for i, img in enumerate(piece_images_display):
                button_rect = pygame.Rect(
                    x + i * button_width, y, button_width, button_height)
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if button_rect.collidepoint(mouse_x, mouse_y):
                    pygame.draw.rect(
                        screen, self.theme.button_hovered, button_rect)
                else:
                    pygame.draw.rect(screen, self.theme.light_bg, button_rect)
                pygame.draw.rect(screen, self.theme.dark_bg, button_rect, 3)
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

    def get_square_from_pos(self, pos, offset_x=10, offset_y=60):
        """Chuyển tọa độ chuột thành vị trí ô cờ trên bàn cờ, có hỗ trợ offset và chế độ flipped."""
        x, y = pos
        # Điều chỉnh vị trí bằng offset
        x -= offset_x
        y -= offset_y
        # Kiểm tra nếu ngoài phạm vi bàn cờ
        if x < 0 or y < 0 or x >= SQUARE_SIZE * 8 or y >= SQUARE_SIZE * 8:
            return None  # Trả về None nếu click ngoài bàn cờ

        col = x // SQUARE_SIZE
        row = y // SQUARE_SIZE
        flipped = self.opt3 == chess.WHITE
        if flipped:
            col, row = 7 - col, 7 - row  # Lật bàn cờ nếu bot cầm quân trắng
        return chess.square(col, 7 - row)

    def draw_pieces(self, screen, offset_x=10, offset_y=60):
        flipped = self.opt3 == chess.WHITE
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                piece_color = 'w' if piece.color == chess.WHITE else 'b'
                piece_type = piece.symbol().lower()
                piece_image = self.piece_images[f"{piece_color}{piece_type}"]
                col, row = chess.square_file(square), chess.square_rank(square)
                if flipped:
                    col, row = 7 - col, 7 - row
                screen.blit(piece_image, (offset_x + col * SQUARE_SIZE,
                            (7 - row) * SQUARE_SIZE + offset_y))

    def draw_board(self, screen, highlighted_squares=None, selected_square=None, offset_x=10, offset_y=60):
        """Vẽ bàn cờ với màu sắc từ theme và thêm offset."""
        if highlighted_squares is None:
            highlighted_squares = []
        flipped = self.opt3 == chess.WHITE  # Nếu bot chơi trắng, đảo ngược bàn cờ
        king_square = None

        # Kiểm tra nước đi cuối cùng
        last_move = None
        if self.board.move_stack:
            last_move = self.board.move_stack[-1]

        # Kiểm tra nếu vua bị chiếu
        if self.board.is_check():
            king_square = self.board.king(self.board.turn)

        for row in range(8):
            for col in range(8):
                draw_row = 7 - row if flipped else row
                draw_col = 7 - col if flipped else col
                square = chess.square(draw_col, 7 - draw_row)
                square = chess.square(draw_col, 7 - draw_row)

                # Màu sắc các ô trắng và đen từ theme
                if (row + col) % 2 == 0:
                    color = self.theme.light_square_bg
                else:
                    color = self.theme.dark_square_bg

                # Tô màu nước đi cuối cùng
                if last_move and (square == last_move.from_square or square == last_move.to_square):
                    color = self.theme.last_move_square

                # Tô màu các ô được chọn
                if square in highlighted_squares:
                    if self.board.piece_at(square):
                        if self.board.piece_at(square).color != self.board.piece_at(selected_square).color:
                            color = self.theme.capture_square
                    else:
                        if self.board.piece_at(selected_square) and self.board.piece_at(selected_square).piece_type == chess.PAWN and chess.square_file(square) != chess.square_file(selected_square):
                            color = self.theme.capture_square
                        else:
                            color = self.theme.target_square
                elif square == selected_square:
                    color = self.theme.highlighted_square

                # Tô màu vua bị chiếu
                if square == king_square:
                    color = self.theme.king_checked

                # Vẽ ô cờ với offset
                pygame.draw.rect(screen, color, (
                    offset_x + col * SQUARE_SIZE, offset_y + row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def main():
    selected_square = None
    highlighted_squares = []
    waiting_for_bot = False
    bot_thread = None

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Chess Game")

    bot1, bot2 = None, None
    opt1, opt2, opt3 = main_menu(screen, theme=Themes("default"))
    game = Chess_Game(opt1, opt2, opt3)

    bot1 = Bot(opt2) if opt1 in ["bot", "bvb"] else None
    bot2 = Bot(opt3) if opt1 == "bvb" else None

    running = opt1 is not None

   # Calculate the y-coordinates for the buttons
    BUTTON_WIDTH, BUTTON_HEIGHT = 150, 50
    undo_button_x = 500 + (300 - BUTTON_WIDTH) // 2
    undo_button_y = (600 - BUTTON_HEIGHT) // 2 - 60  # Position above center
    esc_button_y = undo_button_y + BUTTON_HEIGHT + 20  # Position below Undo button
    resign_button_y = esc_button_y + BUTTON_HEIGHT + \
        20  # Position below ESC Menu button

    # Create the Undo, ESC, and Resign buttons
    undo_button = Buttons(undo_button_x, undo_button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Undo Move",
                          game.theme, lambda: game.undo_move())
    esc_button = Buttons(undo_button_x, esc_button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "ESC Menu",
                         game.theme, lambda: "esc_menu")
    resign_button = Buttons(undo_button_x, resign_button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Resign",
                            game.theme, lambda: "resign")

    def handle_bot_move(move):
        nonlocal waiting_for_bot
        game.board.push(move)
        waiting_for_bot = False

    def get_player_name(game):
        if game.opt1 == "pvp":
            return "Player 1", "Player 2"
        elif game.opt1 == "bot":
            return "Player 1", game.opt2
        elif game.opt1 == "bvb":
            return game.opt2+" White", game.opt3 + " Black"
        return "Unknown", "Unknown"

    def print_player_name(player1_name, player2_name):
        font = pygame.font.Font(None, 36)
        text1 = font.render(player1_name, True, Themes("default").title_text)
        text2 = font.render(player2_name, True, Themes("default").title_text)
        screen.blit(text1, (15, 555))
        screen.blit(text2, (15, 15))
    clock = pygame.time.Clock()
    while running:
        clock.tick(60)
        # Draw the background themes
        screen.fill(game.theme.board_bg)
        pygame.draw.rect(screen, game.theme.side_bg, (500, 0, 300, 600))

        # Draw the game board and chess pieces
        game.draw_board(screen, highlighted_squares, selected_square)
        game.draw_pieces(screen)
        player1_name, player2_name = get_player_name(game)
        print_player_name(player1_name, player2_name)
        # Draw the Undo and ESC buttons
        if game.opt1 != "bvb":
            undo_button.draw(screen)
            resign_button.draw(screen)
        esc_button.draw(screen)
        pygame.display.flip()

        if game.board.is_game_over():
            # Add a 2-second delay to display the final move
            game.draw_board(screen, highlighted_squares, selected_square)
            game.draw_pieces(screen)
            player1_name, player2_name = get_player_name(game)
            print_player_name(player1_name, player2_name)
            pygame.display.flip()
            pygame.time.wait(3000)
            winner = chess.WHITE if game.board.is_checkmate(
            ) and not game.board.turn else chess.BLACK
            action = game_over_menu(screen, game, winner)
            if action == "new_game":
                game.new_Game()
                selected_square = None
                highlighted_squares = []
                waiting_for_bot = False
                bot_thread = None
            elif action == "change_option":
                selected_square = None
                highlighted_squares = []
                opt1, opt2, opt3 = select_game_mode(
                    screen, theme=Themes("default"))
                game = Chess_Game(opt1, opt2, opt3)
                bot1 = Bot(opt2) if opt1 in ["bot", "bvb"] else None
                bot2 = Bot(opt3) if opt1 == "bvb" else None
                running = opt1 is not None
            elif action == "exit":
                running = False
                break
            continue

        if not waiting_for_bot and (bot_thread is None or (bot_thread is not None and not bot_thread.is_alive())):
            if game.opt1 == "bvb":
                current_bot = bot1 if game.board.turn == chess.WHITE else bot2
                if current_bot:
                    waiting_for_bot = True
                    bot_thread = BotWorker(
                        current_bot, game.board, handle_bot_move)
                    bot_thread.start()

            elif game.opt1 == "bot":
                if bot1 and game.board.turn == game.opt3:
                    if bot_thread is None or not bot_thread.is_alive():
                        waiting_for_bot = True
                        bot_thread = BotWorker(
                            bot1, game.board, handle_bot_move)
                        bot_thread.start()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                action = esc_menu(screen, game.theme)
                if action == "resume":
                    continue
                elif action == "change_option":
                    opt1, opt2, opt3 = select_game_mode(
                        screen, theme=Themes("default"))
                    game = Chess_Game(opt1, opt2, opt3)
                    bot1 = Bot(opt2) if opt1 in ["bot", "bvb"] else None
                    bot2 = Bot(opt3) if opt1 == "bvb" else None
                    running = opt1 is not None
                elif action == "exit":
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if resign_button.check_event(event) == "resign":
                    winner = chess.BLACK if game.board.turn == chess.WHITE else chess.WHITE
                    action = game_over_menu(screen, game, winner)
                    if action == "new_game":
                        game.new_Game()
                        selected_square = None
                        highlighted_squares = []
                        waiting_for_bot = False
                        bot_thread = None
                    elif action == "change_option":
                        opt1, opt2, opt3 = select_game_mode(
                            screen, theme=Themes("default"))
                        game = Chess_Game(opt1, opt2, opt3)
                        bot1 = Bot(opt2) if opt1 in ["bot", "bvb"] else None
                        bot2 = Bot(opt3) if opt1 == "bvb" else None
                        running = opt1 is not None
                    elif action == "exit":
                        running = False
                esc_button.check_event(event)
                if esc_button.is_clicked:
                    esc_button.is_clicked = False
                    action = esc_menu(screen, game.theme)
                    if action == "resume":
                        continue
                    elif action == "change_option":
                        opt1, opt2, opt3 = select_game_mode(
                            screen, theme=Themes("default"))
                        game = Chess_Game(opt1, opt2, opt3)
                        bot1 = Bot(opt2) if opt1 in ["bot", "bvb"] else None
                        bot2 = Bot(opt3) if opt1 == "bvb" else None
                        running = opt1 is not None
                    elif action == "exit":
                        running = False
                if waiting_for_bot:
                    continue
                undo_button.check_event(event)
                # Xử lý sự kiện click chuột trên bàn cờ
                if game.opt1 == "bot" and game.board.turn == game.opt3:
                    continue
                square = game.get_square_from_pos(event.pos)
                if square is None:
                    continue
                if selected_square is None:
                    if game.board.piece_at(square):
                        selected_square = square
                        highlighted_squares = [
                            move.to_square for move in game.board.legal_moves if move.from_square == selected_square]
                else:
                    move = chess.Move(selected_square, square)
                    if game.board.piece_at(selected_square) and game.board.piece_at(selected_square).piece_type == chess.PAWN and chess.square_rank(square) in [0, 7]:
                        move = chess.Move(
                            selected_square, square, promotion=chess.QUEEN)
                        if move in game.board.legal_moves:
                            promoted_piece = game.pawn_promotion('w' if game.board.piece_at(
                                selected_square).color == chess.WHITE else 'b', screen)
                            move = chess.Move(
                                selected_square, square, promotion=chess.PIECE_SYMBOLS.index(promoted_piece))
                    if move in game.board.legal_moves:
                        game.board.push(move)
                    selected_square = None
                    highlighted_squares = []

    pygame.quit()


if __name__ == "__main__":
    main()
    os._exit(0)
