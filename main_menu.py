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
font = pygame.font.Font(None, 36)

# Lớp Button


class Button:
    def __init__(self, text, x, y, width, height, callback):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.callback = callback
        self.color = GRAY
        self.hovered = False
        self.clicked = False

    def draw(self, screen):
        color = CLICK_COLOR if self.clicked else (
            HOVER_COLOR if self.hovered else GRAY)
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, BLACK, self.rect, 2)  # Viền đen
        text_surf = font.render(self.text, True, BLACK)
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
bot_options_visible = False
mode = None
bot_color = None


def start_pvp():
    global mode
    mode = "PvP"
    return mode


def start_bot():
    global bot_options_visible, mode
    bot_options_visible = True
    mode = "Bot"


def bot_white():
    global bot_color
    bot_color = chess.WHITE
    return "Bot", bot_color


def bot_black():
    global bot_color
    bot_color = chess.BLACK
    return "Bot", bot_color


def bot_random():
    global bot_color
    bot_color = random.choice((chess.WHITE, chess.BLACK))
    return "Bot", bot_color


def main_menu():
    global bot_options_visible, mode, bot_color
    bot_options_visible = False
    mode = None
    bot_color = None

    buttons = [
        Button("PvP", 140, 150, 200, 50, start_pvp),
        Button("Play with Bot", 140, 220, 200, 50, start_bot)
    ]

    bot_buttons = [
        Button("Bot play White", 140, 290, 200, 50, bot_white),
        Button("Bot play Black", 140, 350, 200, 50, bot_black),
        Button("Random", 140, 410, 200, 50, bot_random)
    ]

    running = True
    while running:
        screen.fill(WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return None, None

            for button in buttons:
                result = button.check_event(event)
                if result:
                    return result, None

            if bot_options_visible:
                for button in bot_buttons:
                    result = button.check_event(event)
                    if result:
                        return result

        for button in buttons:
            button.draw(screen)

        if bot_options_visible:
            for button in bot_buttons:
                button.draw(screen)

        pygame.display.flip()

    pygame.quit()
    return None, None


# Gọi main menu nếu chạy file trực tiếp
if __name__ == "__main__":
    game_mode, bot_side = main_menu()
    print("Selected Mode:", game_mode)
    if game_mode == "Bot":
        print("Bot Side:", bot_side)
