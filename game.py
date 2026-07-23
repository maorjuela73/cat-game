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

BG_COLOR = (40, 40, 60)
CELL_BG = (70, 70, 100)
WIN_COLOR = (255, 215, 0)
STATS_BG = (35, 35, 55)
BTN_COLOR = (60, 60, 90)
BTN_HOVER = (80, 80, 110)

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

STATS_FILE = "assets/stats.json"


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
        if self.current_streak > self.best_streak:
            self.best_streak = self.current_streak
        self.total_play_time += time_sec
        self.save()

    def reset_streak(self):
        self.current_streak = 0
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
            self.sprite_wins = d.get('sprite_wins', [0] * 4)
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


cells = []
for r in range(ROWS):
    for c in range(COLS):
        cells.append(Cell(r, c))


def all_same():
    val = cells[0].current_sprite
    return all(c.current_sprite == val for c in cells)


def all_stopped():
    return all(not c.spinning for c in cells)


def fmt_time(secs):
    if secs >= 60:
        m = int(secs // 60)
        s = secs % 60
        return f"{m}:{s:05.2f}"
    return f"{secs:.1f}s"


def draw_stats_screen(stats, mouse_pos, current_clicks=0):
    screen.fill(STATS_BG)

    title = title_font.render("STATISTICS", True, (220, 220, 220))
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 10))

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

    col1_x = 30
    col2_x = SCREEN_WIDTH // 2 + 15
    stat_y = 52
    line_h = 20

    for i, (label, val) in enumerate(left_stats):
        color = (255, 215, 0) if label == "Current Clicks" else (180, 180, 200)
        text = small_font.render(f"{label}: {val}", True, color)
        screen.blit(text, (col1_x, stat_y + i * line_h))

    for i, (label, val) in enumerate(right_stats):
        text = small_font.render(f"{label}: {val}", True, (180, 180, 200))
        screen.blit(text, (col2_x, stat_y + i * line_h))

    hist_label = font.render("Recent 10: Clicks per Game", True, (200, 200, 220))
    screen.blit(hist_label, (SCREEN_WIDTH // 2 - hist_label.get_width() // 2, 180))
    hist_y = 220
    hist_h = 130

    history = stats.clicks_history[-10:]
    if history:
        max_clicks_hist = max(history)
        total_w = SCREEN_WIDTH - 60
        bar_w = max(6, min(20, total_w // len(history) - 3))
        gap = max(2, min(4, (total_w - bar_w * len(history)) // (len(history) - 1))) if len(history) > 1 else 0
        total_bar_w = len(history) * bar_w + (len(history) - 1) * gap
        start_x = (SCREEN_WIDTH - total_bar_w) // 2

        for i, clicks in enumerate(history):
            bar_h = int((clicks / max_clicks_hist) * hist_h) if max_clicks_hist > 0 else 0
            x = start_x + i * (bar_w + gap)
            y = hist_y + hist_h - bar_h
            color = (100, 180, 255) if clicks < stats.max_clicks else (255, 200, 100)
            pygame.draw.rect(screen, color, (x, y, bar_w, bar_h))
            if bar_h > 18:
                val_text = tiny_font.render(str(clicks), True, (255, 255, 255))
                screen.blit(val_text, (x + (bar_w - val_text.get_width()) // 2, y - 15))

        if len(history) > 1:
            leg_box_w = 58
            leg_box_h = 34
            leg_box_y = hist_y + hist_h // 2 - leg_box_h // 2
            leg_box_x = SCREEN_WIDTH - 8
            pygame.draw.rect(screen, (45, 45, 65), (leg_box_x - leg_box_w, leg_box_y, leg_box_w, leg_box_h), border_radius=4)
            swatch_size = 8
            label_x = leg_box_x - leg_box_w + 6
            swatch_x = label_x
            text_x = label_x + swatch_size + 4
            row_y = leg_box_y + 4
            pygame.draw.rect(screen, (100, 180, 255), (swatch_x, row_y + 2, swatch_size, swatch_size), border_radius=2)
            older_lbl = tiny_font.render("older", True, (130, 130, 150))
            screen.blit(older_lbl, (text_x, row_y))
            row_y += 15
            pygame.draw.rect(screen, (255, 200, 100), (swatch_x, row_y + 2, swatch_size, swatch_size), border_radius=2)
            latest_lbl = tiny_font.render("latest", True, (130, 130, 150))
            screen.blit(latest_lbl, (text_x, row_y))
    else:
        no_data = small_font.render("No games played yet", True, (100, 100, 130))
        screen.blit(no_data, (SCREEN_WIDTH // 2 - no_data.get_width() // 2, hist_y + 30))

    heat_label = font.render("Favorite Cell", True, (200, 200, 220))
    screen.blit(heat_label, (SCREEN_WIDTH // 2 - heat_label.get_width() // 2, 364))
    heat_y = 388
    cell_w, cell_h = 40, 36
    cell_gap = 5
    heat_total_w = 3 * cell_w + 2 * cell_gap
    heat_start_x = (SCREEN_WIDTH - heat_total_w) // 2
    max_cell = max(stats.cell_clicks) if max(stats.cell_clicks) > 0 else 1

    for r in range(3):
        for c in range(3):
            idx = r * 3 + c
            clicks = stats.cell_clicks[idx]
            intensity = clicks / max_cell
            color = (
                int(40 + 180 * intensity),
                int(40 + 60 * (1 - intensity)),
                int(40 + 100 * (1 - intensity)),
            )
            x = heat_start_x + c * (cell_w + cell_gap)
            y = heat_y + r * (cell_h + cell_gap)
            pygame.draw.rect(screen, color, (x, y, cell_w, cell_h), border_radius=4)
            count_text = tiny_font.render(str(clicks), True, (255, 255, 255))
            screen.blit(count_text, (x + (cell_w - count_text.get_width()) // 2, y + (cell_h - count_text.get_height()) // 2))

    sprite_label = font.render("Win Sprite Distribution", True, (200, 200, 220))
    screen.blit(sprite_label, (SCREEN_WIDTH // 2 - sprite_label.get_width() // 2, 518))
    sprite_y = 544
    bar_x = 70
    bar_w = SCREEN_WIDTH - 140
    bar_h = 22
    sprite_gap = 4
    total_sprite_wins = sum(stats.sprite_wins)
    max_wins = max(stats.sprite_wins) if max(stats.sprite_wins) > 0 else 1

    for s in range(NUM_SPRITES):
        wins = stats.sprite_wins[s]
        pct = (wins / total_sprite_wins * 100) if total_sprite_wins > 0 else 0
        fill_w = int((wins / max_wins) * bar_w)

        thumb_x = bar_x - 28
        thumb_y = sprite_y + (bar_h - 24) // 2
        screen.blit(tiny_sprites[s], (thumb_x, thumb_y))

        pygame.draw.rect(screen, (50, 50, 70), (bar_x, sprite_y, bar_w, bar_h), border_radius=4)
        if fill_w > 0:
            bar_color = (80 + s * 30, 160 - s * 20, 200 - s * 30)
            pygame.draw.rect(screen, bar_color, (bar_x, sprite_y, fill_w, bar_h), border_radius=4)

        right_x = bar_x + bar_w + 6
        pct_text = tiny_font.render(f"{pct:.0f}%", True, (255, 255, 255))
        screen.blit(pct_text, (right_x, sprite_y + (bar_h - pct_text.get_height()) // 2))

        count_text = tiny_font.render(f"({wins})", True, (160, 160, 180))
        screen.blit(count_text, (right_x + pct_text.get_width() + 4, sprite_y + (bar_h - count_text.get_height()) // 2))

        sprite_y += bar_h + sprite_gap

    back_rect = pygame.Rect(SCREEN_WIDTH - 115, 10, 105, 34)
    btn_color = BTN_HOVER if back_rect.collidepoint(mouse_pos) else BTN_COLOR
    pygame.draw.rect(screen, btn_color, back_rect, border_radius=8)
    back_text = font.render("BACK", True, (200, 200, 220))
    screen.blit(back_text, (back_rect.centerx - back_text.get_width() // 2, back_rect.centery - back_text.get_height() // 2))

    return back_rect


if __name__ == '__main__':
    stats = StatsManager()
    STATS_BTN_RECT = pygame.Rect(SCREEN_WIDTH - 115, 10, 105, 34)
    stats_back_rect = None
    
    game_state = "PLAYING"
    won = False
    click_count = 0
    current_cell_clicks = [0] * 9
    game_start_ticks = 0
    running = True
    
    while running:
        dt = clock.tick(FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
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
                elif STATS_BTN_RECT.collidepoint(event.pos):
                    game_state = "STATS"
                else:
                    mx, my = event.pos
                    for cell in cells:
                        if cell.rect.collidepoint(mx, my) and not cell.spinning:
                            cell.start_spin()
                            click_count += 1
                            idx = cell.row * COLS + cell.col
                            current_cell_clicks[idx] += 1
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
            game_duration = (pygame.time.get_ticks() - game_start_ticks) / 1000.0
            win_sprite = cells[0].current_sprite
            stats.record_game(click_count, game_duration, current_cell_clicks, win_sprite)
    
        screen.fill(BG_COLOR)
    
        if game_state == "PLAYING":
            for cell in cells:
                cell.draw(screen)
    
            title = title_font.render("Michi Slot!", True, (220, 220, 220))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 10))
    
            btn_color = BTN_HOVER if STATS_BTN_RECT.collidepoint(mouse_pos) else BTN_COLOR
            pygame.draw.rect(screen, btn_color, STATS_BTN_RECT, border_radius=8)
            btn_text = font.render("STATS", True, (200, 200, 220))
            screen.blit(btn_text, (STATS_BTN_RECT.centerx - btn_text.get_width() // 2, STATS_BTN_RECT.centery - btn_text.get_height() // 2))
    
            if not won and all_stopped():
                hint = font.render("Click a cell to spin!", True, (150, 150, 180))
                screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 40))
    
            if won:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 100))
                screen.blit(overlay, (0, 0))
                win_text = big_font.render("YOU WIN!", True, WIN_COLOR)
                screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
                sub = font.render("Click anywhere to play again", True, (200, 200, 200))
                screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
    
        elif game_state == "STATS":
            stats_back_rect = draw_stats_screen(stats, mouse_pos, click_count)
    
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()
