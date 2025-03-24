import random
import pygame
import math

def draw_center_mass(surface, pos, radius=15, colors=((255, 255, 255), (0, 0, 0))):
    pygame.draw.circle(surface, colors[0], pos, radius, draw_bottom_right=True, draw_top_left=True)
    pygame.draw.circle(surface, colors[1], pos, radius, draw_bottom_left=True, draw_top_right=True)
    pygame.draw.circle(surface, colors[1], pos, radius, 1)


def draw_particles(surface, color1, color2, pos, max_radius, min_radius, n_dir, fps=60):
    for _ in range(n_dir*int(60/fps)**2):
        angle = random.uniform(0, 2 * math.pi)
        radius = random.gauss(min_radius, max_radius)
        x = int(pos[0] + radius * math.cos(angle))
        y = int(pos[1] + radius * math.sin(angle))
        if color1 is None or color2 is None:
            pcolor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        else:
            pcolor = lerp_v3(color1, color2, random.random())
        pygame.draw.circle(surface, pcolor, (x,y), 1)


def draw_path_particles(surface, color1, color2, points, max_radius, min_radius, density, closed=True, fps=60):
    if closed:
        points = [*points, points[0]]
    for p0, p1 in zip(points, points[1:]):
        draw_line_particles(surface, color1, color2, p0, p1, max_radius, min_radius, density, fps=fps)


def get_distance(p0, p1):
    return math.sqrt((p1[0]-p0[0])**2+(p1[1]-p0[1])**2)


def get_direction(p0, p1):
    return math.atan2(p1[1]-p0[1], p1[0]-p0[0])


def draw_line_particles(surface, color1, color2, start_pos, end_pos, max_radius, min_radius, density, min_n_circ=4, fps=60):
    dist = get_distance(start_pos, end_pos)
    for n_circ in range(max(int(dist*density), min_n_circ)):
        t = random.uniform(0., 1.)
        center = lerp_v2(start_pos, end_pos, t)
        draw_particles(surface, color1, color2, center, max_radius, min_radius, n_circ, fps=fps)


def centered_rect(surface, width, height):
    cx, cy = surface.get_width() // 2, surface.get_height() // 2
    rect = (cx - width // 2, cy - height // 2, width, height)
    return rect


def lerp(a, b, t):
    return a + (b-a)*t


def lerp_v2(p0, p1, t):
    return lerp(p0[0], p1[0], t), lerp(p0[1], p1[1], t)


def lerp_v3(p0, p1, t):
    return lerp(p0[0], p1[0], t), lerp(p0[1], p1[1], t), lerp(p0[2], p1[2], t)



def centered_text(surface, rect, text, font, color):
    text_popup = font.render(text, True, color)
    tw, th = text_popup.get_width(), text_popup.get_height()
    cx, cy = rect[0]+rect[2]//2, rect[1]+rect[3]//2
    surface.blit(text_popup, (cx-tw//2, cy-th//2))


def text_center(text) -> tuple[int, int]:
    return text.get_width() // 2, text.get_height() // 2