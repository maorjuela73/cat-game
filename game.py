import pygame
import random
import sys

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("assets/audio/music/music.mp3")
pygame.mixer.music.play(-1)
click_sounds = [pygame.mixer.Sound(f"assets/audio/sfx/sound{i}.mp3") for i in range(1, 4)]
win_sound = pygame.mixer.Sound("assets/audio/sfx/win.mp3")

from models import Cell, StatsManager, COLS, ROWS, NUM_SPRITES, all_same, all_stopped
from ui import (
    SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE, PADDING, CELL_BG, BG_COLOR,
    WIN_COLOR, TEXT_BRIGHT, TEXT_NORMAL, TEXT_DIM, BTN_RECT,
    cell_rect, sprites, font, title_font, big_font,
    draw_button, draw_centered, draw_stats_screen,
)

FPS = 60

screen = pygame.display.get_surface()
clock = pygame.time.Clock()

stats = StatsManager()
cells = [Cell(r, c) for r in range(ROWS) for c in range(COLS)]

game_state = "PLAYING"
won = False
click_count = 0
current_cell_clicks = [0] * 9
game_start_ticks = 0
stats_back_rect = None

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
                    if cell_rect(cell.row, cell.col).collidepoint(event.pos) and not cell.spinning:
                        cell.start_spin()
                        click_count += 1
                        current_cell_clicks[cell.row * COLS + cell.col] += 1
                        random.choice(click_sounds).play()
                        if game_start_ticks == 0:
                            game_start_ticks = pygame.time.get_ticks()
                        break

    for cell in cells:
        cell.update(dt)

    if game_state == "PLAYING" and not won and all_stopped(cells) and all_same(cells):
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
            rect = cell_rect(cell.row, cell.col)
            pygame.draw.rect(screen, CELL_BG, rect, border_radius=8)
            screen.blit(sprites[cell.display_sprite], rect.topleft)

        draw_centered(screen, title_font.render("Michi Slot!", True, TEXT_BRIGHT), 10)
        draw_button(screen, BTN_RECT, "STATS", mouse_pos)

        if not won and all_stopped(cells):
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
        stats_back_rect = draw_stats_screen(screen, stats, mouse_pos, click_count)

    pygame.display.flip()
