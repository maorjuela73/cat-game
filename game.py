import pygame
import random
import sys

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("assets/audio/music/music.mp3")
pygame.mixer.music.play(-1)
click_sounds = [pygame.mixer.Sound(f"assets/audio/sfx/sound{i}.mp3") for i in range(1, 4)]
win_sound = pygame.mixer.Sound("assets/audio/sfx/win.mp3")

SPRITE_PATH = "assets/graphics/sprites/CatMegaFree/MochiFree/Box3.png"
NUM_SPRITES = 4
SPRITE_SIZE = 32
COLS, ROWS = 3, 3
CELL_SIZE = 100
PADDING = 10
BOARD_WIDTH = COLS * CELL_SIZE + (COLS - 1) * PADDING
BOARD_HEIGHT = ROWS * CELL_SIZE + (ROWS - 1) * PADDING
SCREEN_WIDTH = BOARD_WIDTH + 80
SCREEN_HEIGHT = BOARD_HEIGHT + 150
FPS = 60

BG_COLOR = (40, 40, 60)
CELL_BG = (70, 70, 100)
WIN_COLOR = (255, 215, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Michi Slot!")
clock = pygame.time.Clock()
font = pygame.font.Font("assets/fonts/PixelPurl.ttf", 28)
big_font = pygame.font.Font("assets/fonts/PixelPurl.ttf", 48)

sheet = pygame.image.load(SPRITE_PATH).convert_alpha()
sprites = []
for i in range(NUM_SPRITES):
    frame = pygame.Surface((SPRITE_SIZE, SPRITE_SIZE), pygame.SRCALPHA)
    frame.blit(sheet, (0, 0), (i * SPRITE_SIZE, 0, SPRITE_SIZE, SPRITE_SIZE))
    scaled = pygame.transform.scale(frame, (CELL_SIZE, CELL_SIZE))
    sprites.append(scaled)

board_x = (SCREEN_WIDTH - BOARD_WIDTH) // 2
board_y = 85


class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.current_sprite = random.randint(0, NUM_SPRITES - 1)
        self.spinning = False
        self.spin_timer = 0.0
        self.spin_duration = 0.0
        self.elapsed = 0.0
        self.display_sprite = self.current_sprite
        self.target_sprite = self.current_sprite

    @property
    def rect(self):
        x = board_x + self.col * (CELL_SIZE + PADDING)
        y = board_y + self.row * (CELL_SIZE + PADDING)
        return pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

    def start_spin(self):
        if self.spinning:
            return
        self.spinning = True
        self.spin_timer = 0.0
        self.spin_duration = random.uniform(2.0, 4.0)
        self.elapsed = 0.0
        self.target_sprite = random.randint(0, NUM_SPRITES - 1)

    def update(self, dt):
        if not self.spinning:
            return
        self.elapsed += dt
        progress = self.elapsed / self.spin_duration
        p = min(progress, 1.0)
        interval = 0.125 + p * p * 0.5

        self.spin_timer += dt
        if self.spin_timer >= interval:
            self.spin_timer -= interval
            self.display_sprite = (self.display_sprite + 1) % NUM_SPRITES

        if self.elapsed >= self.spin_duration:
            self.spinning = False
            self.display_sprite = self.target_sprite
            self.current_sprite = self.target_sprite

    def draw(self, surface):
        pygame.draw.rect(surface, CELL_BG, self.rect, border_radius=8)
        sprite_img = sprites[self.display_sprite]
        sx = self.rect.x + (CELL_SIZE - CELL_SIZE) // 2
        sy = self.rect.y + (CELL_SIZE - CELL_SIZE) // 2
        surface.blit(sprite_img, (sx, sy))
        if not self.spinning and self.current_sprite == self.target_sprite:
            pass


cells = []
for r in range(ROWS):
    for c in range(COLS):
        cells.append(Cell(r, c))


def all_same():
    val = cells[0].current_sprite
    return all(c.current_sprite == val for c in cells)


def all_stopped():
    return all(not c.spinning for c in cells)


won = False
click_count = 0
running = True

while running:
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if won:
                for cell in cells:
                    cell.current_sprite = random.randint(0, NUM_SPRITES - 1)
                    cell.display_sprite = cell.current_sprite
                    cell.target_sprite = cell.current_sprite
                won = False
                click_count = 0
                pygame.mixer.music.unpause()
            else:
                mx, my = event.pos
                for cell in cells:
                    if cell.rect.collidepoint(mx, my) and not cell.spinning:
                        cell.start_spin()
                        click_count += 1
                        random.choice(click_sounds).play()
                        break

    for cell in cells:
        cell.update(dt)

    if not won and all_stopped() and all_same():
        won = True
        win_sound.play()
        pygame.mixer.music.pause()

    screen.fill(BG_COLOR)

    for cell in cells:
        cell.draw(screen)

    title = font.render("Cat Slot!", True, (220, 220, 220))
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 12))

    clicks_text = font.render(f"Clicks: {click_count}", True, (200, 200, 220))
    screen.blit(clicks_text, (SCREEN_WIDTH // 2 - clicks_text.get_width() // 2, 48))

    if not won and all_stopped():
        hint = font.render("Click a cell to spin!", True, (150, 150, 180))
        screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 35))

    if won:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))
        win_text = big_font.render("YOU WIN!", True, WIN_COLOR)
        screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
        sub = font.render("Click anywhere to play again", True, (200, 200, 200))
        screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, SCREEN_HEIGHT // 2 + 10))

    pygame.display.flip()

pygame.quit()
sys.exit()
