import chess
import pygame
import os


# create a(n) list/array to save Themes[i], supported to initialize a themes


class Themes:
    # Base Colors
    BASE_COLORS = {
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "light_brown": (240, 217, 181),
        "dark_brown": (181, 136, 99),
        "light_gray": (211, 211, 211),
        "gray": (169, 169, 169),
        "cyan": (0, 255, 255),
        "sky_blue": (51, 153, 255),
        "green": (0, 255, 0),
        "yellow": (255, 255, 0),
        "red": (255, 0, 0)
    }

    # Các theme mặc định và cơ bản
    THEMES = {
        "default": {
            "light_bg": BASE_COLORS["white"],
            "dark_bg": BASE_COLORS["black"],
            "light_square": BASE_COLORS["light_brown"],
            "dark_square": BASE_COLORS["dark_brown"],
            "highlighted_square": BASE_COLORS["green"],
            "target_square": BASE_COLORS["yellow"],
            "capture_square": BASE_COLORS["red"],
            "king_checked": BASE_COLORS["red"],
            "last_move_square": BASE_COLORS["cyan"],
            "button_bg": BASE_COLORS["white"],
            "button_hover": BASE_COLORS["light_gray"],
            "button_click": BASE_COLORS["gray"],
            "button_select": BASE_COLORS["gray"],
            "text_color": BASE_COLORS["black"],
            "title_text_color": BASE_COLORS["sky_blue"],
            "button_border": BASE_COLORS["black"],
            "grid_color": BASE_COLORS["gray"],
            "bg_screenfill": BASE_COLORS["white"],
            "board_bg": BASE_COLORS["light_gray"],
            "side_bg": BASE_COLORS["light_brown"],
        },
    }

    def __init__(self, theme_name="default"):
        self.apply_theme(theme_name)

    def apply_theme(self, theme_name):
        """Áp dụng theme cho đối tượng"""
        theme = self.THEMES.get(theme_name, self.THEMES["default"])
        self.light_bg = theme["light_bg"]
        self.dark_bg = theme["dark_bg"]
        self.light_square_bg = theme["light_square"]
        self.dark_square_bg = theme["dark_square"]
        self.highlighted_square = theme["highlighted_square"]
        self.target_square = theme["target_square"]
        self.capture_square = theme["capture_square"]
        self.king_checked = theme["king_checked"]
        self.last_move_square = theme["last_move_square"]
        self.button_bg = theme["button_bg"]
        self.button_hovered = theme["button_hover"]
        self.button_clicked = theme["button_click"]
        self.button_selected = theme["button_select"]
        self.button_border = theme["button_border"]
        self.text = theme["text_color"]
        self.title_text = theme["title_text_color"]
        self.bg_screenfill = theme["bg_screenfill"]
        self.board_bg = theme["board_bg"]
        self.side_bg = theme["side_bg"]

    def add_theme(self, theme_name, theme_colors):
        """Thêm theme mới vào danh sách"""
        if theme_name in self.THEMES:
            print(f"Theme '{theme_name}' đã tồn tại.")
        else:
            self.THEMES[theme_name] = theme_colors
            print(f"Theme '{theme_name}' đã được thêm thành công.")

    def edit_theme(self, theme_name, updated_colors):
        """Chỉnh sửa theme đã có"""
        if theme_name in self.THEMES:
            self.THEMES[theme_name].update(updated_colors)
            print(f"Theme '{theme_name}' đã được cập nhật.")
        else:
            print(f"Theme '{theme_name}' không tồn tại.")


class Buttons:
    # x,y offset
    # width, height
    # text
    # clicked_color form theme_used
    # hovered_color form theme_used
    # callback_function
    # draw()
    # check_event()

    def __init__(self, x, y, width, height, text, theme, callback_function, image=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.theme = theme  # Passing the theme to use its properties
        self.callback_function = callback_function
        self.is_hovered = False  # Track if the button is being hovered over
        self.is_clicked = False  # Track if the button is clicked
        self.is_selected = False
        self.image = image

    def draw(self, screen):
        # Check if the button is hovered
        mouse_pos = pygame.mouse.get_pos()
        if self.x <= mouse_pos[0] <= self.x + self.width and self.y <= mouse_pos[1] <= self.y + self.height:
            self.is_hovered = True
        else:
            self.is_hovered = False

        # Set the button background color based on hover or click state
        if self.is_selected:
            button_color = self.theme.button_selected  # Màu nền khi nút được chọn
        elif self.is_hovered:
            button_color = self.theme.button_hovered
        else:
            button_color = self.theme.button_bg

        # Draw the button background
        pygame.draw.rect(screen, button_color,
                         (self.x, self.y, self.width, self.height))

        # Draw the button border (using theme's button border color, which is black)
        border_thickness = 2  # You can adjust the border thickness here
        pygame.draw.rect(screen, self.theme.button_border,
                         (self.x, self.y, self.width, self.height), border_thickness)

        # Draw the button text
        font = pygame.font.Font(None, 36)
        text_surface = font.render(
            self.text, True, self.theme.text)
        screen.blit(text_surface, (self.x + (self.width - text_surface.get_width()) // 2,
                                   self.y + (self.height - text_surface.get_height()) // 2))

    def check_event(self, event):
        button_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                # Call the callback function when the button is clicked
                self.is_clicked = True
                return self.callback_function()
        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_clicked = False  # Reset the clicked state when the mouse button is released


def welcome_screen(screen, theme):
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
    BUTTON_WIDTH, BUTTON_HEIGHT = 260, 60
    TITLE_Y = 100
    BUTTON_START_Y = 230
    BUTTON_SPACING = 80

    play_button = Buttons(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, BUTTON_START_Y,
                          BUTTON_WIDTH, BUTTON_HEIGHT, "Play Chess!", theme, lambda: "play")
    quit_button = Buttons(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, BUTTON_START_Y + BUTTON_SPACING,
                          BUTTON_WIDTH, BUTTON_HEIGHT, "Quit :<", theme, lambda: "quit")

    font = pygame.font.Font(None, 48)
    title_text = font.render("Welcome to Chess!", True, theme.title_text)

    running = True
    while running:
        screen.fill(theme.bg_screenfill)
        screen.blit(title_text, (SCREEN_WIDTH // 2 -
                    title_text.get_width() // 2, TITLE_Y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, None, None
            play_button.check_event(event)
            quit_button.check_event(event)
            if play_button.is_clicked:
                return select_game_mode(screen, theme)
            elif quit_button.is_clicked:
                return None, None, None

        play_button.draw(screen)
        quit_button.draw(screen)
        pygame.display.flip()


def select_game_mode(screen, theme):
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
    BUTTON_WIDTH, BUTTON_HEIGHT = 260, 60
    TITLE_Y = 100
    BUTTON_START_Y = 230
    BUTTON_SPACING = 80

    back_button = Buttons(20, 20, 50, 50, "<---", theme, lambda: "back")
    pvp_button = Buttons(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, BUTTON_START_Y,
                         BUTTON_WIDTH, BUTTON_HEIGHT, "Player vs Player", theme, lambda: "pvp")
    bot_button = Buttons(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, BUTTON_START_Y + BUTTON_SPACING,
                         BUTTON_WIDTH, BUTTON_HEIGHT, "Player vs Bot", theme, lambda: "bot")
    bvb_button = Buttons(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, BUTTON_START_Y + 2 * BUTTON_SPACING,
                         BUTTON_WIDTH, BUTTON_HEIGHT, "Bot vs Bot", theme, lambda: "bvb")

    font = pygame.font.Font(None, 48)
    mode_text = font.render("Select Game Mode", True, theme.title_text)

    running = True
    while running:
        screen.fill(theme.bg_screenfill)
        screen.blit(mode_text, (SCREEN_WIDTH // 2 -
                    mode_text.get_width() // 2, TITLE_Y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, None, None
            back_button.check_event(event)
            pvp_button.check_event(event)
            bot_button.check_event(event)
            bvb_button.check_event(event)
            if back_button.is_clicked:
                return welcome_screen(screen, theme)
            if pvp_button.is_clicked:
                return "pvp", None, None
            elif bot_button.is_clicked:
                return select_bot_type(screen, theme)
            elif bvb_button.is_clicked:
                return select_bvb(screen, theme)

        back_button.draw(screen)
        pvp_button.draw(screen)
        bot_button.draw(screen)
        bvb_button.draw(screen)
        pygame.display.flip()


def select_bot_type(screen, theme):
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
    BUTTON_WIDTH, BUTTON_HEIGHT = 260, 60
    TITLE_Y = 100
    BUTTON_START_Y = 230
    BUTTON_SPACING = 80

    back_button = Buttons(20, 20, 50, 50, "<---", theme, lambda: "back")
    baka_button = Buttons(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, BUTTON_START_Y,
                          BUTTON_WIDTH, BUTTON_HEIGHT, "Play with BotBaka", theme, lambda: "baka")
    aho_button = Buttons(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, BUTTON_START_Y + BUTTON_SPACING,
                         BUTTON_WIDTH, BUTTON_HEIGHT, "Play with BotAho", theme, lambda: "aho")
    stockfish_button = Buttons(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, BUTTON_START_Y + 2 * BUTTON_SPACING,
                               BUTTON_WIDTH, BUTTON_HEIGHT, "Play with Stockfish", theme, lambda: "stockfish")

    font = pygame.font.Font(None, 48)
    bot_text = font.render("Select Bot Type", True, theme.title_text)

    running = True
    while running:
        screen.fill(theme.bg_screenfill)
        screen.blit(bot_text, (SCREEN_WIDTH // 2 -
                    bot_text.get_width() // 2, TITLE_Y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, None, None
            back_button.check_event(event)
            baka_button.check_event(event)
            aho_button.check_event(event)
            stockfish_button.check_event(event)

            if back_button.is_clicked:
                return select_game_mode(screen, theme)
            if baka_button.is_clicked:
                return select_bot_color(screen, theme, "BotBaka")
            elif aho_button.is_clicked:
                return select_bot_color(screen, theme, "BotAho")
            elif stockfish_button.is_clicked:
                return select_bot_color(screen, theme, "Stockfish")

        back_button.draw(screen)
        baka_button.draw(screen)
        aho_button.draw(screen)
        stockfish_button.draw(screen)
        pygame.display.flip()


def select_bot_color(screen, theme, bot_type):
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
    BUTTON_WIDTH, BUTTON_HEIGHT = 260, 60
    TITLE_Y = 100
    BUTTON_START_Y = 230
    BUTTON_SPACING = 80

    back_button = Buttons(20, 20, 50, 50, "<---", theme, lambda: "back")
    white_button = Buttons(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, BUTTON_START_Y,
                           BUTTON_WIDTH, BUTTON_HEIGHT, f"{bot_type} play White", theme, lambda: "white")
    black_button = Buttons(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, BUTTON_START_Y + BUTTON_SPACING,
                           BUTTON_WIDTH, BUTTON_HEIGHT, f"{bot_type} play Black", theme, lambda: "black")

    font = pygame.font.Font(None, 48)
    color_text = font.render(
        f"Select {bot_type} Color", True, theme.title_text)

    running = True
    while running:
        screen.fill(theme.bg_screenfill)
        screen.blit(color_text, (SCREEN_WIDTH // 2 -
                    color_text.get_width() // 2, TITLE_Y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, None, None
            back_button.check_event(event)
            white_button.check_event(event)
            black_button.check_event(event)

            if back_button.is_clicked:
                return select_bot_type(screen, theme)
            if white_button.is_clicked:
                return "bot", bot_type, chess.WHITE
            elif black_button.is_clicked:
                return "bot", bot_type, chess.BLACK

        back_button.draw(screen)
        white_button.draw(screen)
        black_button.draw(screen)
        pygame.display.flip()


def select_bvb(screen, theme):
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
    BUTTON_WIDTH, BUTTON_HEIGHT = 260, 60
    TITLE_Y = 100
    BUTTON_START_Y = 150
    BUTTON_SPACING = 60

    white_bot = None
    black_bot = None

    font = pygame.font.Font(None, 48)
    text_white = font.render("Select White Bot", True, theme.title_text)
    text_black = font.render("Select Black Bot", True, theme.title_text)

    back_button = Buttons(20, 20, 50, 50, "<---", theme, lambda: "back")

    white_buttons = [
        Buttons(SCREEN_WIDTH // 2 - 1.5 * BUTTON_WIDTH, BUTTON_START_Y,
                BUTTON_WIDTH, BUTTON_HEIGHT, "BotBaka", theme, lambda: "BotBaka"),
        Buttons(SCREEN_WIDTH // 2 - 0.5 * BUTTON_WIDTH, BUTTON_START_Y,
                BUTTON_WIDTH, BUTTON_HEIGHT, "BotAho", theme, lambda: "BotAho"),
        Buttons(SCREEN_WIDTH // 2 + 0.5 * BUTTON_WIDTH, BUTTON_START_Y,
                BUTTON_WIDTH, BUTTON_HEIGHT, "Stockfish", theme, lambda: "Stockfish")
    ]

    black_buttons = [
        Buttons(SCREEN_WIDTH // 2 - 1.5 * BUTTON_WIDTH, BUTTON_START_Y * 2 + BUTTON_SPACING,
                BUTTON_WIDTH, BUTTON_HEIGHT, "BotBaka", theme, lambda: "BotBaka"),
        Buttons(SCREEN_WIDTH // 2 - 0.5 * BUTTON_WIDTH, BUTTON_START_Y * 2 + BUTTON_SPACING,
                BUTTON_WIDTH, BUTTON_HEIGHT, "BotAho", theme, lambda: "BotAho"),
        Buttons(SCREEN_WIDTH // 2 + 0.5 * BUTTON_WIDTH, BUTTON_START_Y * 2 + BUTTON_SPACING,
                BUTTON_WIDTH, BUTTON_HEIGHT, "Stockfish", theme, lambda: "Stockfish")
    ]

    running = True
    while running:
        screen.fill(theme.bg_screenfill)
        screen.blit(text_white, (SCREEN_WIDTH // 2 -
                    text_white.get_width() // 2, TITLE_Y))
        screen.blit(text_black, (SCREEN_WIDTH // 2 -
                    text_black.get_width() // 2, TITLE_Y * 2 + BUTTON_SPACING * 2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, None, None

            back_button.check_event(event)

            for btn in white_buttons:
                btn.check_event(event)
                if btn.is_clicked:
                    btn.is_selected = True
                    white_bot = btn.text
                    for other_btn in white_buttons:
                        other_btn.is_selected = (other_btn == btn)

            for btn in black_buttons:
                btn.check_event(event)
                if btn.is_clicked:
                    black_bot = btn.text
                    btn.is_selected = True
                    for other_btn in black_buttons:
                        other_btn.is_selected = (other_btn == btn)

            if back_button.is_clicked:
                return select_game_mode(screen, theme)

            if white_bot and black_bot:
                return "bvb", white_bot, black_bot

        back_button.draw(screen)
        for btn in white_buttons:
            btn.draw(screen)
        for btn in black_buttons:
            btn.draw(screen)
        pygame.display.flip()


def main_menu(screen, theme=Themes("default")):
    return welcome_screen(screen, theme)


def esc_menu(screen, theme):
    """
    Display the ESC menu with options to resume, change game options, or exit.
    """
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
    BUTTON_WIDTH, BUTTON_HEIGHT = 260, 60
    TITLE_Y = 100
    BUTTON_START_Y = 230
    BUTTON_SPACING = 80

    resume_button = Buttons(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, BUTTON_START_Y,
                            BUTTON_WIDTH, BUTTON_HEIGHT, "Resume Game", theme, lambda: "resume")
    change_option_button = Buttons(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, BUTTON_START_Y + BUTTON_SPACING,
                                   BUTTON_WIDTH, BUTTON_HEIGHT, "Change Option", theme, lambda: "change_option")
    exit_button = Buttons(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, BUTTON_START_Y + 2 * BUTTON_SPACING,
                          BUTTON_WIDTH, BUTTON_HEIGHT, "Exit", theme, lambda: "exit")

    font = pygame.font.Font(None, 48)
    title_text = font.render("Game Paused", True, theme.title_text)

    running = True
    while running:
        screen.fill(theme.bg_screenfill)
        screen.blit(title_text, (SCREEN_WIDTH // 2 -
                    title_text.get_width() // 2, TITLE_Y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            resume_button.check_event(event)
            change_option_button.check_event(event)
            exit_button.check_event(event)

            if resume_button.is_clicked:
                return "resume"
            elif change_option_button.is_clicked:
                return "change_option"
            elif exit_button.is_clicked:
                return "exit"

        resume_button.draw(screen)
        change_option_button.draw(screen)
        exit_button.draw(screen)
        pygame.display.flip()


def game_over_menu(screen, game, winner=None):
    """
    Display the game over menu with the result and options to restart, change game options, or exit.
    """
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
    BUTTON_WIDTH, BUTTON_HEIGHT = 260, 60
    TITLE_Y = 100
    BUTTON_START_Y = 230
    BUTTON_SPACING = 80

    # Determine the result message
    if game.board.is_checkmate():
        result_text = f"{'White' if winner == chess.WHITE else 'Black'} wins!"
        if game.opt1 == "bvb":
            result_text += f" ({game.opt2 if winner == chess.WHITE else game.opt3})"
        elif game.opt1 == "bot":
            result_text += f" ({game.opt2})" if game.opt3 == winner else f" (Player)"
    elif game.board.is_stalemate():
        result_text = "Stalemate!"
    elif game.board.is_insufficient_material():
        result_text = "Draw (Insufficient Material)!"
    elif game.board.is_seventyfive_moves():
        result_text = "Draw (75-move Rule)!"
    elif game.board.is_fivefold_repetition():
        result_text = "Draw (Fivefold Repetition)!"
    else:
        result_text = "Game Over!"

    # Buttons for the menu
    new_game_button = Buttons(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, BUTTON_START_Y,
                              BUTTON_WIDTH, BUTTON_HEIGHT, "New Game", game.theme, lambda: "new_game")
    change_option_button = Buttons(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, BUTTON_START_Y + BUTTON_SPACING,
                                   BUTTON_WIDTH, BUTTON_HEIGHT, "Change Option", game.theme, lambda: "change_option")
    exit_button = Buttons(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, BUTTON_START_Y + 2 * BUTTON_SPACING,
                          BUTTON_WIDTH, BUTTON_HEIGHT, "Exit", game.theme, lambda: "exit")

    font = pygame.font.Font(None, 48)
    result_surface = font.render(result_text, True, game.theme.title_text)

    running = True
    while running:
        screen.fill(game.theme.bg_screenfill)
        screen.blit(result_surface, (SCREEN_WIDTH // 2 -
                    result_surface.get_width() // 2, TITLE_Y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            new_game_button.check_event(event)
            change_option_button.check_event(event)
            exit_button.check_event(event)

            if new_game_button.is_clicked:
                return "new_game"
            elif change_option_button.is_clicked:
                return "change_option"
            elif exit_button.is_clicked:
                return "exit"

        new_game_button.draw(screen)
        change_option_button.draw(screen)
        exit_button.draw(screen)
        pygame.display.flip()


if __name__ == "__main__":
    pygame.init()
    # Set up the screen and theme
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Test GUI Chess Game")
    opt1, opt2, opt3 = main_menu(screen,)
    print(opt1, opt2, opt3)
    pygame.quit()
