import math

import pygame
# from canvas import Canvas
import colorsys
from typing import Sequence, Self
from pygame import Vector2


Vec2 = tuple[float, float] | pygame.Vector2
Vec3 = tuple[float, float, float] | pygame.Vector2
Vec4 = tuple[float, float, float, float]
Point = Vec2
Points = tuple[Point, ...] | Sequence


def points_from_rect(rect=Vec4) -> Points:
    x0, y0, w, h = rect
    return (x0 + w, y0), (x0 + w, y0 - h), (x0, y0 - h), (x0, y0)


def perpendicular_normal(vec: Vec2) -> (Vec2, Vec2):
    if not isinstance(vec, Vector2):
        vec = Vector2(vec)
    vec = vec.normalize()
    return Vector2(-vec[1], vec[0]), vec


def outer_rect(points: Points) -> Vec4:
    min_x, max_x = float('inf'), float('-inf')
    min_y, max_y = float('inf'), float('-inf')
    for p in points:
        min_x = min(min_x, p[0])
        max_x = max(max_x, p[0])
        min_y = min(min_y, p[1])
        max_y = max(max_y, p[1])
    return min_x, max_y, max_x - min_x, max_y - min_y


def rotate_around_v2(vec: Vec2, angle: float, center: Vec2 = (0.0, 0.0)):
    if not isinstance(vec, Vector2):
        vec = Vector2(vec)
    return (vec - center).rotate_rad(angle) + center


def rotate_vec2s(vecs: Sequence[Vector2] | Sequence[tuple[float, float]], angle: float, center: Vector2 = (0.0, 0.0)) -> Sequence:
    return tuple(rotate_around_v2(vec, angle, center) for vec in vecs)


def translate_vec2s(vecs: Sequence[Vector2] | Sequence[tuple[float, float]], shift: Vector2) -> Sequence:
    return tuple( (vec[0]+shift[0], vec[1]+shift[1]) for vec in vecs)

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
            case (a, b) if isinstance(a, float | int) and isinstance(b, float | int):
                return other[0]*self[0, 0] + other[1]*self[0, 1], other[0]*self[1, 0] + other[1]*self[1, 1]
            case _ if isinstance(other, Vector2):
                return Vector2(other[0]*self[0, 0] + other[1]*self[0, 1], other[0]*self[1, 0] + other[1]*self[1, 1])
            case float() | int():
                return Mat2x2(other*self[0, 0], other*self[0, 1], other*self[1, 0], other*self[1, 1])
            case [*points] | (*points, ) if all(isinstance(item, tuple | Vector2) for item in points):
                return tuple(self*p for p in points)
            case _:
                raise ValueError(f"Não é possível multiplicar Mat2x2 por {type(other)}: {other=}")

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


class fRect:
    def __init__(self, *args):
        if len(args) == 4:
            self.x, self.y, self.w, self.h = args
        elif len(args) == 1:
            self.x, self.y, self.w, self.h = args[0]
        else:
            raise ValueError(f'fRect aceita como argumentos 4 floats ou tupla de 4 floats, mar recebeu: {type(args)}, {args=}')

    def __getitem__(self, item):
        return (self.x, self.y, self.w, self.h)[item]

    @property
    def points(self):
        return points_from_rect((self.x, self.y, self.w, self.h))

    @property
    def topleft(self):
        return Vector2(self.x, self.y)

    @topleft.setter
    def topleft(self, point):
        self.x, self.y = point

    @property
    def midtop(self):
        return Vector2(self.x+self.w/2, self.y)

    @midtop.setter
    def midtop(self, point):
        self.x, self.y = point[0]-self.w/2, point[1]

    @property
    def topright(self):
        return Vector2(self.x+self.w, self.y)

    @topright.setter
    def topright(self, point):
        self.x, self.y = point[0]-self.w, point[1]

    @property
    def bottomright(self):
        return Vector2(self.x+self.w, self.y-self.h)

    @bottomright.setter
    def bottomright(self, point):
        self.x, self.y = point[0]-self.w, point[1]+self.h

    @property
    def midbottom(self):
        return Vector2(self.x+self.w/2, self.y-self.h)

    @midbottom.setter
    def midbottom(self, point):
        self.x, self.y = point[0]-self.w/2, point[1]+self.h

    @property
    def center(self):
        return Vector2(self.x+self.w/2, self.y-self.h/2)

    @center.setter
    def center(self, point):
        self.x, self.y = point[0]-self.w/2, point[1]+self.h/2

    @property
    def midleft(self):
        return Vector2(self.x, self.y-self.h/2)

    @midleft.setter
    def midleft(self, point):
        self.x, self.y = point[0], point[1]+self.h/2

    @property
    def midright(self):
        return Vector2(self.x+self.w, self.y-self.h/2)

    @midright.setter
    def midright(self, point):
        self.x, self.y = point[0]-self.w, point[1]+self.h/2

    @property
    def bottomleft(self):
        return Vector2(self.x, self.y-self.h)

    @bottomleft.setter
    def bottomleft(self, point):
        self.x, self.y = point[0], point[1]+self.h

    def __add__(self, vec2: Vec2):
        return fRect(self.x + vec2[0], self.y + vec2[1], self.w, self.h)

    def __sub__(self, vec2: Vec2):
        return fRect(self.x - vec2[0], self.y - vec2[1], self.w, self.h)

    def __format__(self, format_spec):
        return f'fRect[{self.x:{format_spec}}, {self.y:{format_spec}}, {self.w:{format_spec}}, {self.h:{format_spec}}]'

    def __str__(self):
        return f'fRect[{self.x}, {self.y}, {self.w}, {self.h}]'


class fPoints:
    def __init__(self, *points_seq):
        if len(points_seq) == 1:
            points_seq = tuple(*points_seq)

        self._points = tuple(Vector2(p) for p in points_seq)

    def __str__(self):
        points_str = ", ".join(f"({x}, {y})" for x, y in self._points)
        return f"fPoints[ {points_str} ]"

    def __iter__(self):
        yield from self._points

    def __getitem__(self, item):
        return self._points[item]

    def rotate(self, angle: float, center: Vector2 | tuple[float, float]) -> Self:
        return fPoints(rotate_around_v2(p, angle, center) for p in self._points)

    def translate(self, offset: Vector2 | tuple[float, float]) -> Self:
        return fPoints(p+offset for p in self._points)

    def scale(self, scale: float | tuple[float, float] | Vector2, anchor: float | tuple[float, float] | Vector2 = (0, 0)) -> Self:
        if isinstance(scale, float | int):
            scale = (scale, scale)
        return fPoints(((x - anchor[0]) * scale[0] + anchor[0], (y - anchor[1]) * scale[1] + anchor[1]) for x,y in self._points)

    def rect(self) -> fRect:
        return fRect(outer_rect(self._points))


if __name__ == '__main__':
    r = fRect(0.0, 0.0, 2.0, 1.0)

    print(f'{r:.2f}')
    print(r)
    print(r[0])
    x,y,w,h = r + (.5, .2)
    print(x,y,w,h)
    print(r-(10,20))
    r.center = (0, 0)
    print(r)

    r2 = (1,1,3,4)
    r3 = fRect(r2)



