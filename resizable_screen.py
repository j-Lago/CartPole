import pygame
import sys
from datetime import datetime


pygame.init()
WIDTH, HEIGHT = 1600, 900  # Tamanho maior da janela
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
clock = pygame.time.Clock()

canvas = pygame.surface.Surface((1920, 1080), pygame.SRCALPHA)
antialiasing = True
fullscreen = False




def display_message(surface, text, color):
    font = pygame.font.SysFont('Courier New', 200)
    text_surface = font.render(text, True, color[:3])
    text_rect = text_surface.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
    if len(color) == 4:
        text_surface.set_alpha(color[3])
    surface.blit(text_surface, text_rect)


def blit_with_aspect_ratio(source: pygame.surface.Surface, dest: pygame.surface.Surface, antialiasing=True, offset: tuple[int, int] | None = None):


    source_width, source_height = source.get_size()
    dest_width, dest_height = dest.get_size()

    source_ratio = source_width / source_height
    dest_ratio = dest_width / dest_height

    if source.get_size() == dest.get_size():
        scaled_surface = source.copy()
        if offset is None:
            offset = (0, 0)
    else:
        rescale = pygame.transform.smoothscale if antialiasing else pygame.transform.scale
        if source_ratio > dest_ratio:
            new_width = dest_width
            new_height = int(dest_width / source_ratio)
        else:
            new_height = dest_height
            new_width = int(dest_height * source_ratio)
        scaled_surface = rescale(source, (new_width, new_height))
        if offset is None:
            offset = (dest_width - new_width) // 2, (dest_height - new_height) // 2   # centralizada
    dest.blit(scaled_surface, offset)


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    pygame.display.quit()
                    pygame.display.init()
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
            elif event.key == pygame.K_UP:
                WIDTH, HEIGHT = screen.get_width(), screen.get_height()-50
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            elif event.key == pygame.K_DOWN:
                WIDTH, HEIGHT = screen.get_width(), screen.get_height()+50
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            elif event.key == pygame.K_LEFT:
                WIDTH, HEIGHT = screen.get_width()-50, screen.get_height()
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            elif event.key == pygame.K_RIGHT:
                WIDTH, HEIGHT = screen.get_width()+50, screen.get_height()
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            elif event.key == pygame.K_a:
                antialiasing = not antialiasing


    canvas.fill((60, 30, 30))
    pygame.draw.circle(canvas, (30, 255, 30, 128), (200, 200), 200)
    pygame.draw.circle(screen, (30, 30, 255), (350, 250), 200)
    display_message(canvas, datetime.now().strftime("%H:%M:%S"), (30, 120, 30, 128))
    width=2
    pygame.draw.line(canvas, (255, 255, 255), (200, 200), (600, 500), width=width)
    pygame.draw.line(canvas, (255, 255, 255), (600, 500), (1000, 500), width=width)
    pygame.draw.line(canvas, (255, 255, 255), (1000, 500), (1000, 800), width=width)

    screen.fill((30, 30, 30))
    blit_with_aspect_ratio(canvas, screen, antialiasing)





    pygame.display.flip()
    clock.tick(60)