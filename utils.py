import math

import pygame
from canvas import Canvas
import colorsys


Vec2 = tuple[float, float] | pygame.Vector2
Vec3 = tuple[float, float, float] | pygame.Vector2
Vec4 = tuple[float, float, float, float]
Point = Vec2
Points = tuple[Point, ...]


def points_from_rect(rect=Vec4) -> Points:
    x0, y0, w, h = rect
    return (x0, y0), (x0, y0 - h), (x0 + w, y0 - h), (x0 + w, y0)

def external_rect_from_points(points: Points) -> Vec4:
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    return min_x, max_y, max_x - min_x, max_y - min_y



def remap(point: Vec2, origin: Vec4 | Canvas | pygame.Surface, dest: Vec4 | Canvas | pygame.Surface) -> Vec2:
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




def collision_point_rect(point: Vec2, rect: Vec4) -> bool:
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
            case complex():
                return complex(other.real*self[0, 0] + other.imag*self[0, 1], other.real*self[1, 0] + other.imag*self[1, 1])
            case (a, b) if isinstance(a, float) and isinstance(b, float):
                return other[0]*self[0, 0] + other[1]*self[0, 1], other[0]*self[1, 0] + other[1]*self[1, 1]
            case float() | int():
                return Mat2x2(other*self[0, 0], other*self[0, 1], other*self[1, 0], other*self[1, 1])
            case [*points] | (*points, ) if all(isinstance(item, tuple) for item in points):
                return tuple(self*p for p in points)
            case _:
                raise ValueError(f"Não é possível multiplicar Mat2x2 por {type(other)}")

    def __str__(self):
        return str(self._values)


class RotateMatrix(Mat2x2):
    def __init__(self, angle_rad: float):
        c, s = math.cos(angle_rad), math.sin(angle_rad)
        super().__init__(c, -s, s, c)

        self._angle_rad = angle_rad

    @property
    def angle_rad(self):
        return self._angle_rad

    @angle_rad.setter
    def angle_rad(self, value):
        c, s = math.cos(value), math.sin(value)
        self._values = (c, -s, s, c)

    @property
    def angle_deg(self):
        return self._angle_rad * 180 / math.pi

    @angle_deg.setter
    def angle_deg(self, value):
        self.angle_rad = value / 180 * math.pi
