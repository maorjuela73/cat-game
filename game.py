import pygame
import random
import json
import os
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
SCREEN_HEIGHT = 660
FPS = 60
STATS_FILE = "assets/stats.json"

BG_COLOR = (40, 40, 60)
CELL_BG = (70, 70, 100)
WIN_COLOR = (255, 215, 0)
STATS_BG = (35, 35, 55)
BTN_COLOR = (60, 60, 90)
BTN_HOVER = (80, 80, 110)
PANEL_BG = (40, 40, 62)
LEGEND_BG = (45, 45, 65)
BAR_TRACK = (50, 50, 70)
HIST_NORMAL = (100, 180, 255)
HIST_MAX = (255, 200, 100)

TEXT_BRIGHT = (220, 220, 220)
TEXT_NORMAL = (200, 200, 220)
TEXT_MUTED = (180, 180, 200)
TEXT_DIM = (150, 150, 175)
TEXT_FAINT = (100, 100, 130)

ACCENT_BLUE = (100, 180, 255)
ACCENT_ORANGE = (255, 180, 100)
ACCENT_GREEN = (120, 200, 160)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Michi Slot!")
clock = pygame.time.Clock()
font = pygame.font.Font("assets/fonts/PixelPurl.ttf", 28)
title_font = pygame.font.Font("assets/fonts/PixelPurl.ttf", 36)
big_font = pygame.font.Font("assets/fonts/PixelPurl.ttf", 48)
small_font = pygame.font.Font("assets/fonts/PixelPurl.ttf", 20)
tiny_font = pygame.font.Font("assets/fonts/PixelPurl.ttf", 14)

sheet = pygame.image.load(SPRITE_PATH).convert_alpha()
sprites = []
tiny_sprites = []
for i in range(NUM_SPRITES):
    frame = pygame.Surface((SPRITE_SIZE, SPRITE_SIZE), pygame.SRCALPHA)
    frame.blit(sheet, (0, 0), (i * SPRITE_SIZE, 0, SPRITE_SIZE, SPRITE_SIZE))
    scaled = pygame.transform.scale(frame, (CELL_SIZE, CELL_SIZE))
    sprites.append(scaled)
    tiny_sprites.append(pygame.transform.scale(frame, (24, 24)))

board_x = (SCREEN_WIDTH - BOARD_WIDTH) // 2
board_y = (SCREEN_HEIGHT - BOARD_HEIGHT) // 2

BTN_RECT = pygame.Rect(SCREEN_WIDTH - 115, 10, 105, 34)

STAT_COL_LEFT = 30
STAT_COL_RIGHT = SCREEN_WIDTH // 2 + 15


def draw_button(rect, label, mouse_pos):
    color = BTN_HOVER if rect.collidepoint(mouse_pos) else BTN_COLOR
    pygame.draw.rect(screen, color, rect, border_radius=8)
    text = font.render(label, True, TEXT_NORMAL)
    screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))


def draw_centered(surface, text_surf, y):
    surface.blit(text_surf, ((SCREEN_WIDTH - text_surf.get_width()) // 2, y))


def draw_section_header(title, y, accent_color):
    text = font.render(title, True, TEXT_NORMAL)
    x = (SCREEN_WIDTH - text.get_width()) // 2
    screen.blit(text, (x, y))
    pygame.draw.rect(screen, accent_color, (x - 10, y + 4, 4, 18), border_radius=2)


class StatsManager:
    def __init__(self):
        self.games_played = 0
        self.total_clicks = 0
        self.clicks_history = []
        self.times_history = []
        self.cell_clicks = [0] * 9
        self.sprite_wins = [0] * NUM_SPRITES
        self.current_streak = 0
        self.best_streak = 0
        self.total_play_time = 0.0
        self.load()

    @property
    def avg_clicks(self):
        return self.total_clicks / self.games_played if self.games_played else 0.0

    @property
    def max_clicks(self):
        return max(self.clicks_history) if self.clicks_history else 0

    @property
    def min_clicks(self):
        return min(self.clicks_history) if self.clicks_history else 0

    @property
    def avg_time(self):
        return self.total_play_time / self.games_played if self.games_played else 0.0

    @property
    def fastest_win(self):
        return min(self.times_history) if self.times_history else 0.0

    @property
    def slowest_win(self):
        return max(self.times_history) if self.times_history else 0.0

    def record_game(self, clicks, time_sec, cell_clicks, win_sprite):
        self.games_played += 1
        self.total_clicks += clicks
        self.clicks_history.append(clicks)
        self.times_history.append(time_sec)
        for i in range(9):
            self.cell_clicks[i] += cell_clicks[i]
        self.sprite_wins[win_sprite] += 1
        self.current_streak += 1
        self.best_streak = max(self.best_streak, self.current_streak)
        self.total_play_time += time_sec
        self.save()

    def load(self):
        if not os.path.exists(STATS_FILE):
            return
        try:
            with open(STATS_FILE) as f:
                d = json.load(f)
            self.games_played = d.get('games_played', 0)
            self.total_clicks = d.get('total_clicks', 0)
            self.clicks_history = d.get('clicks_history', [])
            self.times_history = d.get('times_history', [])
            self.cell_clicks = d.get('cell_clicks', [0] * 9)
            self.sprite_wins = d.get('sprite_wins', [0] * NUM_SPRITES)
            self.current_streak = d.get('current_streak', 0)
            self.best_streak = d.get('best_streak', 0)
            self.total_play_time = d.get('total_play_time', 0.0)
        except (json.JSONDecodeError, IOError):
            pass

    def save(self):
        d = {
            'games_played': self.games_played,
            'total_clicks': self.total_clicks,
            'clicks_history': self.clicks_history,
            'times_history': self.times_history,
            'cell_clicks': self.cell_clicks,
            'sprite_wins': self.sprite_wins,
            'current_streak': self.current_streak,
            'best_streak': self.best_streak,
            'total_play_time': self.total_play_time,
        }
        os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
        with open(STATS_FILE, 'w') as f:
            json.dump(d, f, indent=2)


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
        p = min(self.elapsed / self.spin_duration, 1.0)
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
        surface.blit(sprites[self.display_sprite], self.rect.topleft)


cells = [Cell(r, c) for r in range(ROWS) for c in range(COLS)]


def all_same():
    return all(c.current_sprite == cells[0].current_sprite for c in cells)


def all_stopped():
    return all(not c.spinning for c in cells)


def fmt_time(secs):
    if secs >= 60:
        m = int(secs // 60)
        return f"{m}:{secs % 60:05.2f}"
    return f"{secs:.1f}s"


def draw_clicks_histogram(stats, y):
    history = stats.clicks_history[-10:]
    if not history:
        no_data = small_font.render("No games played yet", True, TEXT_FAINT)
        draw_centered(screen, no_data, y + 30)
        return

    max_val = max(history)
    total_w = SCREEN_WIDTH - 60
    bar_w = max(6, min(20, total_w // len(history) - 3))
    gap = max(2, min(4, (total_w - bar_w * len(history)) // (len(history) - 1))) if len(history) > 1 else 0
    total_bar_w = len(history) * bar_w + (len(history) - 1) * gap
    start_x = (SCREEN_WIDTH - total_bar_w) // 2
    hist_h = 130

    for i, clicks in enumerate(history):
        bar_h = int((clicks / max_val) * hist_h) if max_val > 0 else 0
        x = start_x + i * (bar_w + gap)
        bar_y = y + hist_h - bar_h
        color = HIST_NORMAL if clicks < stats.max_clicks else HIST_MAX
        pygame.draw.rect(screen, color, (x, bar_y, bar_w, bar_h))
        if bar_h > 18:
            val = tiny_font.render(str(clicks), True, TEXT_BRIGHT)
            screen.blit(val, (x + (bar_w - val.get_width()) // 2, bar_y - 15))

    if len(history) > 1:
        leg_w, leg_h = 58, 34
        leg_x = SCREEN_WIDTH - 8 - leg_w
        leg_y = y + hist_h // 2 - leg_h // 2
        pygame.draw.rect(screen, LEGEND_BG, (leg_x, leg_y, leg_w, leg_h), border_radius=4)
        sx = leg_x + 6
        tx = sx + 12
        sy = leg_y + 4
        pygame.draw.rect(screen, HIST_NORMAL, (sx, sy + 2, 8, 8), border_radius=2)
        screen.blit(tiny_font.render("older", True, (130, 130, 150)), (tx, sy))
        sy += 15
        pygame.draw.rect(screen, HIST_MAX, (sx, sy + 2, 8, 8), border_radius=2)
        screen.blit(tiny_font.render("latest", True, (130, 130, 150)), (tx, sy))


def draw_heat_map(stats, y):
    cell_w, cell_h, cell_gap = 32, 28, 4
    grid_w = 3 * cell_w + 2 * cell_gap
    start_x = (SCREEN_WIDTH - grid_w) // 2
    max_clicks = max(stats.cell_clicks) if max(stats.cell_clicks) > 0 else 1

    lbl_y = y - 12
    for c in range(3):
        lbl = tiny_font.render(str(c + 1), True, TEXT_FAINT)
        cx = start_x + c * (cell_w + cell_gap) + (cell_w - lbl.get_width()) // 2
        screen.blit(lbl, (cx, lbl_y))

    lbl_x = start_x - 16
    for r in range(3):
        lbl = tiny_font.render(str(r + 1), True, TEXT_FAINT)
        ry = y + r * (cell_h + cell_gap) + (cell_h - lbl.get_height()) // 2
        screen.blit(lbl, (lbl_x, ry))

    for r in range(3):
        for c in range(3):
            idx = r * 3 + c
            clicks = stats.cell_clicks[idx]
            intensity = clicks / max_clicks
            color = (
                int(40 + 180 * intensity),
                int(40 + 60 * (1 - intensity)),
                int(40 + 100 * (1 - intensity)),
            )
            x = start_x + c * (cell_w + cell_gap)
            cy = y + r * (cell_h + cell_gap)
            pygame.draw.rect(screen, color, (x, cy, cell_w, cell_h), border_radius=4)
            count = tiny_font.render(str(clicks), True, TEXT_BRIGHT)
            screen.blit(count, (x + (cell_w - count.get_width()) // 2, cy + (cell_h - count.get_height()) // 2))


def draw_sprite_dist(stats, y):
    bar_x = 70
    bar_w = SCREEN_WIDTH - 140
    bar_h = 22
    sprite_gap = 4
    total_wins = sum(stats.sprite_wins)
    max_wins = max(stats.sprite_wins) if max(stats.sprite_wins) > 0 else 1
    colors = [(80 + i * 30, 160 - i * 20, 200 - i * 30) for i in range(NUM_SPRITES)]

    for s in range(NUM_SPRITES):
        wins = stats.sprite_wins[s]
        pct = (wins / total_wins * 100) if total_wins > 0 else 0
        fill_w = int((wins / max_wins) * bar_w)
        cy = y + s * (bar_h + sprite_gap)

        thumb = tiny_sprites[s]
        screen.blit(thumb, (bar_x - 28, cy + (bar_h - thumb.get_height()) // 2))

        pygame.draw.rect(screen, BAR_TRACK, (bar_x, cy, bar_w, bar_h), border_radius=4)
        if fill_w > 0:
            pygame.draw.rect(screen, colors[s], (bar_x, cy, fill_w, bar_h), border_radius=4)

        rx = bar_x + bar_w + 6
        pct_text = tiny_font.render(f"{pct:.0f}%", True, TEXT_BRIGHT)
        screen.blit(pct_text, (rx, cy + (bar_h - pct_text.get_height()) // 2))
        count = tiny_font.render(f"({wins})", True, (160, 160, 180))
        screen.blit(count, (rx + pct_text.get_width() + 4, cy + (bar_h - count.get_height()) // 2))


def draw_stats_screen(stats, mouse_pos, current_clicks):
    screen.fill(STATS_BG)
    draw_centered(screen, title_font.render("STATISTICS", True, TEXT_BRIGHT), 10)

    pygame.draw.rect(screen, PANEL_BG, (22, 52, SCREEN_WIDTH - 44, 132), border_radius=8)

    left_stats = [
        ("Games Played", str(stats.games_played)),
        ("Current Clicks", str(current_clicks)),
        ("Total Clicks", str(stats.total_clicks)),
        ("Avg Clicks", f"{stats.avg_clicks:.1f}"),
        ("Max Clicks", str(stats.max_clicks)),
        ("Min Clicks", str(stats.min_clicks)),
    ]
    right_stats = [
        ("Avg Time", fmt_time(stats.avg_time)),
        ("Fastest Win", fmt_time(stats.fastest_win)),
        ("Slowest Win", fmt_time(stats.slowest_win)),
        ("Current Streak", str(stats.current_streak)),
        ("Best Streak", str(stats.best_streak)),
        ("Total Play Time", fmt_time(stats.total_play_time)),
    ]

    stat_y = 60
    line_h = 20
    for i, (label, val) in enumerate(left_stats):
        color = WIN_COLOR if label == "Current Clicks" else TEXT_MUTED
        text = small_font.render(f"{label}:", True, TEXT_DIM)
        screen.blit(text, (STAT_COL_LEFT, stat_y + i * line_h))
        screen.blit(small_font.render(val, True, color), (STAT_COL_LEFT + text.get_width() + 8, stat_y + i * line_h))

    for i, (label, val) in enumerate(right_stats):
        text = small_font.render(f"{label}:", True, TEXT_DIM)
        screen.blit(text, (STAT_COL_RIGHT, stat_y + i * line_h))
        screen.blit(small_font.render(val, True, TEXT_MUTED), (STAT_COL_RIGHT + text.get_width() + 8, stat_y + i * line_h))

    draw_section_header("Recent 10: Clicks per Game", 188, ACCENT_BLUE)
    draw_clicks_histogram(stats, 228)

    draw_section_header("Favorite Cell", 372, ACCENT_ORANGE)
    draw_heat_map(stats, 412)

    draw_section_header("Win Sprite Distribution", 516, ACCENT_GREEN)
    draw_sprite_dist(stats, 542)

    draw_button(BTN_RECT, "BACK", mouse_pos)
    return BTN_RECT


if __name__ == '__main__':
    stats = StatsManager()
    stats_back_rect = None

    game_state = "PLAYING"
    won = False
    click_count = 0
    current_cell_clicks = [0] * 9
    game_start_ticks = 0

    while True:
        dt = clock.tick(FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state == "STATS":
                    if stats_back_rect and stats_back_rect.collidepoint(event.pos):
                        game_state = "PLAYING"
                elif won:
                    for cell in cells:
                        cell.current_sprite = random.randint(0, NUM_SPRITES - 1)
                        cell.display_sprite = cell.current_sprite
                        cell.target_sprite = cell.current_sprite
                    won = False
                    click_count = 0
                    current_cell_clicks = [0] * 9
                    game_start_ticks = 0
                    pygame.mixer.music.unpause()
                elif BTN_RECT.collidepoint(event.pos):
                    game_state = "STATS"
                else:
                    for cell in cells:
                        if cell.rect.collidepoint(event.pos) and not cell.spinning:
                            cell.start_spin()
                            click_count += 1
                            current_cell_clicks[cell.row * COLS + cell.col] += 1
                            random.choice(click_sounds).play()
                            if game_start_ticks == 0:
                                game_start_ticks = pygame.time.get_ticks()
                            break

        for cell in cells:
            cell.update(dt)

        if game_state == "PLAYING" and not won and all_stopped() and all_same():
            won = True
            win_sound.play()
            pygame.mixer.music.pause()
            stats.record_game(
                click_count,
                (pygame.time.get_ticks() - game_start_ticks) / 1000.0,
                current_cell_clicks,
                cells[0].current_sprite,
            )

        screen.fill(BG_COLOR)

        if game_state == "PLAYING":
            for cell in cells:
                cell.draw(screen)

            draw_centered(screen, title_font.render("Michi Slot!", True, TEXT_BRIGHT), 10)
            draw_button(BTN_RECT, "STATS", mouse_pos)

            if not won and all_stopped():
                hint = font.render("Click a cell to spin!", True, TEXT_DIM)
                draw_centered(screen, hint, SCREEN_HEIGHT - 40)

            if won:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 100))
                screen.blit(overlay, (0, 0))
                win_text = big_font.render("YOU WIN!", True, WIN_COLOR)
                draw_centered(screen, win_text, SCREEN_HEIGHT // 2 - 50)
                sub = font.render("Click anywhere to play again", True, TEXT_NORMAL)
                draw_centered(screen, sub, SCREEN_HEIGHT // 2 + 10)

        elif game_state == "STATS":
            stats_back_rect = draw_stats_screen(stats, mouse_pos, click_count)

        pygame.display.flip()
