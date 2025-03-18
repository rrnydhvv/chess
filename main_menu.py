import pygame
import random
import chess

# Khởi tạo pygame
pygame.init()

# Kích thước cửa sổ
WIDTH, HEIGHT = 480, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Main Menu - Chess")

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
HOVER_COLOR = (170, 170, 170)
CLICK_COLOR = (150, 150, 150)

# Font chữ
font = pygame.font.Font(None, 30)

# Lớp Button


class Button:
    def __init__(self, text, y_offset, callback):
        self.text = text
        self.rect = pygame.Rect(WIDTH // 2 - 110, y_offset, 220, 50)
        self.callback = callback
        self.color = GRAY
        self.hovered = False
        self.clicked = False

    def draw(self, screen):
        color = CLICK_COLOR if self.clicked else (
            HOVER_COLOR if self.hovered else GRAY)
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, BLACK, self.rect, 2)  # Viền đen

        # Kiểm tra nếu text là hàm thì gọi hàm để lấy chuỗi
        text = self.text() if callable(self.text) else self.text
        text_surf = font.render(text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.clicked and self.rect.collidepoint(event.pos):
                return self.callback()
            self.clicked = False


# Trạng thái menu
bot_menu_visible = False
bot_type_menu_visible = False
mode = None
bot_type = None
bot_color = None

# Chức năng nút


def start_pvp():
    return "PvP", None, None


def start_bot():
    global bot_menu_visible
    bot_menu_visible = True
    return None  # Hiển thị menu con


def select_botngu():
    global bot_type_menu_visible, bot_type
    bot_type_menu_visible = True
    bot_type = "Botngu"
    return None


def select_stockfish():
    global bot_type_menu_visible, bot_type
    bot_type_menu_visible = True
    bot_type = "Stockfish"
    return None


def bot_white():
    return "Bot", bot_type, chess.WHITE


def bot_black():
    return "Bot", bot_type, chess.BLACK


def bot_random():
    return "Bot", bot_type, random.choice((chess.WHITE, chess.BLACK))


def main_menu():
    global bot_menu_visible, bot_type_menu_visible, mode, bot_type, bot_color
    bot_menu_visible = False
    bot_type_menu_visible = False
    mode = None
    bot_type = None
    bot_color = None

    # Button menu chính
    buttons = [
        Button("PvP", HEIGHT // 2 - 70, start_pvp),
        Button("Play with Bot", HEIGHT // 2, start_bot)
    ]

    # Menu chọn loại bot (Botngu hoặc Stockfish)
    bot_type_buttons = [
        Button("Play with Botngu", HEIGHT // 2 - 60, select_botngu),
        Button("Play with Stockfish", HEIGHT // 2, select_stockfish)
    ]

    # Menu chọn màu cho Bot
    bot_color_buttons = [
        Button(lambda: f"{bot_type} Play White" if bot_type else "Bot Play White",
               HEIGHT // 2 - 70, bot_white),
        Button(
            lambda: f"{bot_type} Play Black" if bot_type else "Bot Play Black", HEIGHT // 2, bot_black),
        Button("Random", HEIGHT // 2 + 70, bot_random)
    ]

    running = True
    while running:
        screen.fill(WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return None, None, None

            if bot_type_menu_visible:
                for button in bot_color_buttons:
                    result = button.check_event(event)
                    if result:
                        return result

            elif bot_menu_visible:
                for button in bot_type_buttons:
                    result = button.check_event(event)
                    if result:
                        bot_type_menu_visible = True  # Hiện menu tiếp theo
                        break

            else:
                for button in buttons:
                    result = button.check_event(event)
                    if result:
                        return result

        # Vẽ các nút lên màn hình
        if bot_type_menu_visible:
            for button in bot_color_buttons:
                button.draw(screen)
        elif bot_menu_visible:
            for button in bot_type_buttons:
                button.draw(screen)
        else:
            for button in buttons:
                button.draw(screen)

        pygame.display.flip()

    pygame.quit()
    return None, None, None


# Chạy menu nếu chạy file trực tiếp
if __name__ == "__main__":
    game_mode, bot_type, bot_side = main_menu()
    print("Selected Mode:", game_mode)
    if game_mode == "Bot":
        print("Bot Type:", bot_type)
        print("Bot Side:", "White" if bot_side == chess.WHITE else "Black")
