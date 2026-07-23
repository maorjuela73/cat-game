import pygame
from models import COLS, ROWS, NUM_SPRITES, fmt_time

SPRITE_PATH = "assets/graphics/sprites/CatMegaFree/MochiFree/Box3.png"
SPRITE_SIZE = 32
CELL_SIZE = 100
PADDING = 10
BOARD_WIDTH = COLS * CELL_SIZE + (COLS - 1) * PADDING
BOARD_HEIGHT = ROWS * CELL_SIZE + (ROWS - 1) * PADDING
SCREEN_WIDTH = BOARD_WIDTH + 80
SCREEN_HEIGHT = 660

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

board_x = (SCREEN_WIDTH - BOARD_WIDTH) // 2
board_y = (SCREEN_HEIGHT - BOARD_HEIGHT) // 2

BTN_RECT = pygame.Rect(SCREEN_WIDTH - 115, 10, 105, 34)

STAT_COL_LEFT = 30
STAT_COL_RIGHT = SCREEN_WIDTH // 2 + 15


def cell_rect(row, col):
    x = board_x + col * (CELL_SIZE + PADDING)
    y = board_y + row * (CELL_SIZE + PADDING)
    return pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)


pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Michi Slot!")


def init():
    global font, title_font, big_font, small_font, tiny_font
    global sprites, tiny_sprites
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
        sprites.append(pygame.transform.scale(frame, (CELL_SIZE, CELL_SIZE)))
        tiny_sprites.append(pygame.transform.scale(frame, (24, 24)))


font = None
title_font = None
big_font = None
small_font = None
tiny_font = None
sprites = None
tiny_sprites = None


def draw_button(surface, rect, label, mouse_pos):
    color = BTN_HOVER if rect.collidepoint(mouse_pos) else BTN_COLOR
    pygame.draw.rect(surface, color, rect, border_radius=8)
    text = font.render(label, True, TEXT_NORMAL)
    surface.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))


def draw_centered(surface, text_surf, y):
    surface.blit(text_surf, ((SCREEN_WIDTH - text_surf.get_width()) // 2, y))


def draw_section_header(surface, title, y, accent_color):
    text = font.render(title, True, TEXT_NORMAL)
    x = (SCREEN_WIDTH - text.get_width()) // 2
    surface.blit(text, (x, y))
    pygame.draw.rect(surface, accent_color, (x - 10, y + 4, 4, 18), border_radius=2)


def draw_clicks_histogram(surface, stats, y):
    history = stats.clicks_history[-10:]
    if not history:
        no_data = small_font.render("No games played yet", True, TEXT_FAINT)
        draw_centered(surface, no_data, y + 30)
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
        color = HIST_MAX if i == len(history) - 1 else HIST_NORMAL
        pygame.draw.rect(surface, color, (x, bar_y, bar_w, bar_h))
        if bar_h > 18:
            val = tiny_font.render(str(clicks), True, TEXT_BRIGHT)
            surface.blit(val, (x + (bar_w - val.get_width()) // 2, bar_y - 15))

    if len(history) > 1:
        leg_w, leg_h = 58, 34
        leg_x = SCREEN_WIDTH - 8 - leg_w
        leg_y = y + hist_h // 2 - leg_h // 2
        pygame.draw.rect(surface, LEGEND_BG, (leg_x, leg_y, leg_w, leg_h), border_radius=4)
        sx = leg_x + 6
        tx = sx + 12
        sy = leg_y + 4
        pygame.draw.rect(surface, HIST_NORMAL, (sx, sy + 2, 8, 8), border_radius=2)
        surface.blit(tiny_font.render("older", True, (130, 130, 150)), (tx, sy))
        sy += 15
        pygame.draw.rect(surface, HIST_MAX, (sx, sy + 2, 8, 8), border_radius=2)
        surface.blit(tiny_font.render("latest", True, (130, 130, 150)), (tx, sy))


def draw_heat_map(surface, stats, y):
    cell_w, cell_h, cell_gap = 32, 28, 4
    grid_w = 3 * cell_w + 2 * cell_gap
    start_x = (SCREEN_WIDTH - grid_w) // 2
    max_clicks = max(stats.cell_clicks) if max(stats.cell_clicks) > 0 else 1

    lbl_y = y - 12
    for c in range(3):
        lbl = tiny_font.render(str(c + 1), True, TEXT_FAINT)
        cx = start_x + c * (cell_w + cell_gap) + (cell_w - lbl.get_width()) // 2
        surface.blit(lbl, (cx, lbl_y))

    lbl_x = start_x - 16
    for r in range(3):
        lbl = tiny_font.render(str(r + 1), True, TEXT_FAINT)
        ry = y + r * (cell_h + cell_gap) + (cell_h - lbl.get_height()) // 2
        surface.blit(lbl, (lbl_x, ry))

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
            pygame.draw.rect(surface, color, (x, cy, cell_w, cell_h), border_radius=4)
            count = tiny_font.render(str(clicks), True, TEXT_BRIGHT)
            surface.blit(count, (x + (cell_w - count.get_width()) // 2, cy + (cell_h - count.get_height()) // 2))


def draw_sprite_dist(surface, stats, y):
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
        surface.blit(thumb, (bar_x - 28, cy + (bar_h - thumb.get_height()) // 2))

        pygame.draw.rect(surface, BAR_TRACK, (bar_x, cy, bar_w, bar_h), border_radius=4)
        if fill_w > 0:
            pygame.draw.rect(surface, colors[s], (bar_x, cy, fill_w, bar_h), border_radius=4)

        rx = bar_x + bar_w + 6
        pct_text = tiny_font.render(f"{pct:.0f}%", True, TEXT_BRIGHT)
        surface.blit(pct_text, (rx, cy + (bar_h - pct_text.get_height()) // 2))
        count = tiny_font.render(f"({wins})", True, (160, 160, 180))
        surface.blit(count, (rx + pct_text.get_width() + 4, cy + (bar_h - count.get_height()) // 2))


def draw_stats_screen(surface, stats, mouse_pos, current_clicks):
    surface.fill(STATS_BG)
    draw_centered(surface, title_font.render("STATISTICS", True, TEXT_BRIGHT), 10)

    pygame.draw.rect(surface, PANEL_BG, (22, 52, SCREEN_WIDTH - 44, 132), border_radius=8)

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
        surface.blit(text, (STAT_COL_LEFT, stat_y + i * line_h))
        surface.blit(small_font.render(val, True, color), (STAT_COL_LEFT + text.get_width() + 8, stat_y + i * line_h))

    for i, (label, val) in enumerate(right_stats):
        text = small_font.render(f"{label}:", True, TEXT_DIM)
        surface.blit(text, (STAT_COL_RIGHT, stat_y + i * line_h))
        surface.blit(small_font.render(val, True, TEXT_MUTED), (STAT_COL_RIGHT + text.get_width() + 8, stat_y + i * line_h))

    draw_section_header(surface, "Recent 10: Clicks per Game", 188, ACCENT_BLUE)
    draw_clicks_histogram(surface, stats, 228)

    draw_section_header(surface, "Favorite Cell", 372, ACCENT_ORANGE)
    draw_heat_map(surface, stats, 412)

    draw_section_header(surface, "Win Sprite Distribution", 516, ACCENT_GREEN)
    draw_sprite_dist(surface, stats, 542)

    draw_button(surface, BTN_RECT, "BACK", mouse_pos)
    return BTN_RECT
