import pygame
from canvas import Canvas
vec2 = tuple[float, float]
vec4 = tuple[float, float, float, float]


def remap(point: vec2, origin: vec4 | Canvas | pygame.Surface, dest: vec4 | Canvas | pygame.Surface) -> vec2:
    if isinstance(origin, Canvas | pygame.Surface):
        origin = origin.get_rect()
    if isinstance(dest, Canvas | pygame.Surface):
        dest = dest.get_rect()

    ox, oy = point
    ox0, oy0, ow, oh = origin
    dx0, dy0, dw, dh = dest

    oxr = ox - ox0
    oyr = oy - oy0

    dxr = oxr * dw / ow
    dyr = oyr * dh / oh

    dx = dxr + dx0
    dy = dyr + dy0

    return dx, dy


def collision_point_rect(point: vec2, rect: vec4) -> bool:
    return rect[0] < point[0] < rect[0] + rect[2] and rect[1] > point[1] > rect[1] - rect[3]
