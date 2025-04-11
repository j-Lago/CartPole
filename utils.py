import pygame
from canvas import Canvas
import colorsys

vec2 = tuple[float, float]
vec4 = tuple[float, float, float, float]


def remap(point: vec2, origin: vec4 | Canvas | pygame.Surface, dest: vec4 | Canvas | pygame.Surface) -> vec2:
    if isinstance(origin, Canvas):
        origin = origin.surface.get_rect()
    elif isinstance(origin, pygame.Surface):
        origin = origin.get_rect()

    if isinstance(dest, Canvas):
        dest = dest.surface.get_rect()
    elif isinstance(dest, pygame.Surface):
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


class ColorsDiscIterator:
    def __init__(self, maxlen, h0=0.0, s=1.0, v=1.0):
        self.N = maxlen
        self.n = 0
        self.h0 = h0
        self.s = s
        self.v = v

    def __len__(self): return self.N

    def __iter__(self): return self

    def __next__(self):
        if self.n >= self.N:
            raise StopIteration
        hue = (self.n / self.N + self.h0) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, self.s, self.v)
        self.n += 1
        return int(r * 255), int(g * 255), int(b * 255)


class Mat2x2:
    def __init__(self, e00, e01, e10, e11):
        self._values = ((e00, e01), (e10, e11))

    def __getitem__(self, item):
        match item:
            case tuple() | list(): return self._values[item[0]][item[1]]
            case int(): return self._values[item // 2][item % 2]
            case _: raise ValueError(f'item do tipo {type(item)} não é suportado.')

    def __mul__(self, other):
        match other:
            case complex(): return complex(other.real*self[0, 0] + other.imag*self[0, 1], other.real*self[1, 0] + other.imag*self[1, 1])
            case float() | int(): return Mat2x2(other*self[0, 0], other*self[0, 1], other*self[1, 0], other*self[1, 1])

    def __str__(self):
        return str(self._values)