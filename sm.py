import pygame
from copy import deepcopy
from random import choice

# ================= CONFIG =================
W, H = 15, 25

# A5-подібне вертикальне вікно (пропорція як лист)
TILE = 25
GAME_RES = (W * TILE, H * TILE)

FPS = 60

pygame.init()

# ================= COLORS =================
BG_COLOR = (15, 15, 30)
GRID_COLOR = (40, 40, 60)

COLORS = [
    (255, 80, 80),
    (80, 255, 120),
    (80, 180, 255),
    (255, 220, 80),
    (255, 120, 255),
    (120, 255, 255),
    (255, 160, 80),
]

# ================= FIGURES =================
FIGURES_POS = [
    [(-1, 0), (-2, 0), (0, 0), (1, 0)],
    [(0, -1), (-1, -1), (-1, 0), (0, 0)],
    [(-1, 0), (-1, 1), (0, 0), (0, -1)],
    [(0, 0), (-1, 0), (0, 1), (-1, -1)],
    [(0, 0), (0, -1), (0, 1), (1, -1)],
    [(0, 0), (0, -1), (0, 1), (-1, 0)]
]

FIGURES = [
    [pygame.Rect(x + W // 2, y + 1, 1, 1) for x, y in f]
    for f in FIGURES_POS
]


class Tetris:

    def __init__(self):
        self.sc = pygame.display.set_mode(GAME_RES)
        pygame.display.set_caption("TETRIS")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 40, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 30, bold=True)

        self.reset_game()
        self.start_screen = True  # Показуємо стартовий екран

    def reset_game(self):
        self.field = [[0 for _ in range(W)] for _ in range(H)]

        self.figure = deepcopy(choice(FIGURES))
        self.next_figure = deepcopy(choice(FIGURES))

        self.color = choice(COLORS)
        self.next_color = choice(COLORS)

        self.dx = 0
        self.anim_count = 0
        self.anim_limit = 2000
        self.anim_speed = 60

        self.rotate_check = False
        self.fast_drop = False

        self.game_over = False
        self.paused = False

        self.words = ["BOOM!", "COOL!", "GOOD!", "GREAT!", "WOW!", "NICE!", "SUPER!"]
        self.effects = []

    def check_borders(self, i):#чи не виліз блок за лівий край;чи не виліз за правий край;чи не впав нижче поля;чи не врізався в інший блок.

        if self.figure[i].x < 0 or self.figure[i].x > W - 1:
            return False
        if self.figure[i].y > H - 1:
            return False
        if self.field[self.figure[i].y][self.figure[i].x]:
            return False
        return True

    def control(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

            # Якщо ми на стартовому екрані
            if self.start_screen:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if hasattr(self, "start_button_rect") and self.start_button_rect.collidepoint(event.pos):
                        self.start_screen = False  # Починаємо гру
                        self.reset_game()  # Повне скидання перед грою
                continue  # Ігноруємо все інше на стартовому екрані

            # Управління грою (тільки якщо гра запущена)
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_p:
                    self.paused = not self.paused

                if not self.game_over and not self.paused:

                    if event.key == pygame.K_LEFT:
                        self.dx = -1
                    elif event.key == pygame.K_RIGHT:
                        self.dx = 1
                    elif event.key == pygame.K_UP:
                        self.rotate_check = True
                    elif event.key == pygame.K_DOWN:
                        self.fast_drop = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    self.fast_drop = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_over and event.button == 1:
                    if hasattr(self, "restart_rect") and self.restart_rect.collidepoint(event.pos):
                        self.reset_game()

    def move_x(self):#рух по горизонталі
        old = deepcopy(self.figure)

        for i in range(4):
            self.figure[i].x += self.dx
            if not self.check_borders(i):
                self.figure = old
                break

        self.dx = 0

    def move_y(self):#рух вниз
        self.anim_count = 0
        old = deepcopy(self.figure)

        for i in range(4):
            self.figure[i].y += 1

            if not self.check_borders(i):

                for j in range(4):
                    self.field[old[j].y][old[j].x] = self.color

                self.figure = self.next_figure
                self.next_figure = deepcopy(choice(FIGURES))

                self.color = self.next_color
                self.next_color = choice(COLORS)
                break

    def rotate(self):#поворот
        center = self.figure[0]
        old = deepcopy(self.figure)

        for i in range(4):
            x = self.figure[i].y - center.y
            y = self.figure[i].x - center.x

            self.figure[i].x = center.x - x
            self.figure[i].y = center.y + y

            if not self.check_borders(i):
                self.figure = old
                break

    def check_lines(self):#перевіряє повні рядки
        line = H - 1
        lines = 0

        for row in range(H - 1, -1, -1):
            count = 0

            for i in range(W):
                if self.field[row][i]:
                    count += 1
                self.field[line][i] = self.field[row][i]

            if count < W:
                line -= 1
            else:
                lines += 1

        if lines > 0:
            self.effects.append({
                "text": choice(self.words),
                "timer": 40
            })

    def draw_block(self, x, y, color):
        rect = pygame.Rect(x * TILE + 2, y * TILE + 2, TILE - 4, TILE - 4)
        pygame.draw.rect(self.sc, color, rect, border_radius=6)

    def draw_effects(self):
        for effect in self.effects[:]:
            surf = self.font.render(effect["text"], True, (255, 255, 255))
            rect = surf.get_rect(center=(GAME_RES[0] // 2, GAME_RES[1] // 2))

            self.sc.blit(surf, rect)

            effect["timer"] -= 1
            if effect["timer"] <= 0:
                self.effects.remove(effect)

        if len(self.effects) > 5:
            self.effects.pop(0)

    def draw_restart_button(self):
        self.restart_rect = pygame.Rect(
            GAME_RES[0] // 2 - 120,
            GAME_RES[1] // 2 + 30,
            240,
            60
        )

        pygame.draw.rect(self.sc, (60, 60, 90), self.restart_rect, border_radius=10)

        text = self.font.render("RESTART", True, (255, 255, 255))
        self.sc.blit(text, (self.restart_rect.x + 40, self.restart_rect.y + 10))

    def draw_start_screen(self):
        """Малює початковий екран із заголовком та кнопкою"""
        # Затемнення фону
        overlay = pygame.Surface(GAME_RES)
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.sc.blit(overlay, (0, 0))

        # Назва гри
        title_font = pygame.font.SysFont("Arial", 70, bold=True)
        title_text = title_font.render("TETRIS", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(GAME_RES[0] // 2, GAME_RES[1] // 2 - 120))
        self.sc.blit(title_text, title_rect)

        # Кнопка "START THE GAME"
        self.start_button_rect = pygame.Rect(
            GAME_RES[0] // 2 - 140,
            GAME_RES[1] // 2 + 20,
            280,
            70
        )

        # Анімація кнопки (зміна кольору при наведенні)
        mouse_pos = pygame.mouse.get_pos()
        if self.start_button_rect.collidepoint(mouse_pos):
            button_color = (100, 100, 140)
        else:
            button_color = (60, 60, 90)

        pygame.draw.rect(self.sc, button_color, self.start_button_rect, border_radius=15)
        pygame.draw.rect(self.sc, (150, 150, 180), self.start_button_rect, 3, border_radius=15)

        # Текст кнопки
        button_font = pygame.font.SysFont("Arial", 35, bold=True)
        button_text = button_font.render("START THE GAME", True, (255, 255, 255))
        text_rect = button_text.get_rect(center=self.start_button_rect.center)
        self.sc.blit(button_text, text_rect)

        # Інструкція
        hint_font = pygame.font.SysFont("Arial", 20)
        hint_text = hint_font.render("Click the button to start", True, (200, 200, 200))
        hint_rect = hint_text.get_rect(center=(GAME_RES[0] // 2, GAME_RES[1] // 2 + 120))
        self.sc.blit(hint_text, hint_rect)

    def run(self):

        while True:
            self.control()

            # Якщо на стартовому екрані - малюємо заставку
            if self.start_screen:
                self.sc.fill(BG_COLOR)
                self.draw_start_screen()
                pygame.display.flip()
                self.clock.tick(FPS)
                continue

            # Основний ігровий цикл
            self.sc.fill(BG_COLOR)

            if self.game_over:
                overlay = pygame.Surface(GAME_RES)
                overlay.set_alpha(200)
                overlay.fill((0, 0, 0))
                self.sc.blit(overlay, (0, 0))

                t1 = self.font.render("GAME OVER", True, (255, 60, 60))
                self.sc.blit(t1, (GAME_RES[0] // 2 - t1.get_width() // 2, GAME_RES[1] // 2 - 140))

                self.draw_restart_button()

                pygame.display.flip()
                self.clock.tick(FPS)
                continue

            if self.paused:
                t = self.font.render("PAUSED", True, (255, 255, 255))
                self.sc.blit(t, (GAME_RES[0]//2 - 80, GAME_RES[1]//2))

                pygame.display.flip()
                self.clock.tick(FPS)
                continue

            self.anim_count += self.anim_speed

            if self.dx:
                self.move_x()

            speed = 80 if self.fast_drop else self.anim_limit

            if self.anim_count > speed:
                self.move_y()

            if self.rotate_check:
                self.rotate()
                self.rotate_check = False

            self.check_lines()

            for i in range(W):
                if self.field[0][i]:
                    self.game_over = True

            for x in range(W):
                for y in range(H):
                    pygame.draw.rect(
                        self.sc, GRID_COLOR,
                        (x * TILE, y * TILE, TILE, TILE), 1
                    )

            for y, row in enumerate(self.field):
                for x, c in enumerate(row):
                    if c:
                        self.draw_block(x, y, c)

            for i in range(4):
                self.draw_block(self.figure[i].x, self.figure[i].y, self.color)

            self.draw_effects()

            pygame.display.flip()
            self.clock.tick(FPS)


def main():
    Tetris().run()


if __name__ == "__main__":
    main()

