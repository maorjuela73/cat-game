import pygame
import sys

pygame.init()

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 440
FPS = 60

BG_COLOR = (40, 40, 60)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Michi Slot!")
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BG_COLOR)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
