import pygame
from pathlib import Path
from pygame import Vector2
from canvas import Canvas
import math
from utils import outer_rect, points_from_rect, RotateMatrix, fRect
from typing import Self



class Image:
    def __init__(self, canvas: Canvas, surface: pygame.Surface | None = None, pos: tuple[float, float] | Vector2 = Vector2(0, 0), file_path: Path | None = None):
        self._canvas = canvas
        if file_path is not None:
            self._surface: pygame.Surface = pygame.image.load(file_path)
        elif surface is not None:
            self._surface = surface
        else:
            raise ValueError(f"'file_path' ou '_surface' não podem ser ambos None.")
        self._pos = pos


    @property
    def topleft(self):
        return Vector2(self._pos)

    @topleft.setter
    def topleft(self, point):
        self._pos = point

    @property
    def midtop(self):
        x, y, w, h = self.get_rect()
        return Vector2(x+w/2, y)

    @midtop.setter
    def midtop(self, point):
        _, _, w, h = self.get_rect()
        self._pos = point[0]-w/2, point[1]

    @property
    def topright(self):
        x, y, w, h = self.get_rect()
        return Vector2(x+w, y)

    @topright.setter
    def topright(self, point):
        _, _, w, h = self.get_rect()
        self._pos = point[0]-w, point[1]

    @property
    def bottomright(self):
        x, y, w, h = self.get_rect()
        return Vector2(x+w, y-h)

    @bottomright.setter
    def bottomright(self, point):
        _, _, w, h = self.get_rect()
        self._pos = point[0]-w, point[1]+h

    @property
    def midbottom(self):
        x, y, w, h = self.get_rect()
        return Vector2(x+w/2, y-h)

    @midbottom.setter
    def midbottom(self, point):
        _, _, w, h = self.get_rect()
        self._pos = point[0]-w/2, point[1]+h

    @property
    def center(self):
        x, y, w, h = self.get_rect()
        return Vector2(x+w/2, y-h/2)

    @center.setter
    def center(self, point):
        _, _, w, h = self.get_rect()
        self._pos = point[0]-w/2, point[1]+h/2

    @property
    def midleft(self):
        x, y, w, h = self.get_rect()
        return Vector2(x, y-h/2)

    @midleft.setter
    def midleft(self, point):
        _, _, w, h = self.get_rect()
        self._pos = point[0], point[1]+h/2

    @property
    def midright(self):
        x, y, w, h = self.get_rect()
        return Vector2(x+w, y-h/2)

    @midright.setter
    def midright(self, point):
        _, _, w, h = self.get_rect()
        self._pos = point[0]-w, point[1]+h/2

    @property
    def bottomleft(self):
        x, y, w, h = self.get_rect()
        return Vector2(x, y-h)

    @bottomleft.setter
    def bottomleft(self, point):
        _, _, w, h = self.get_rect()
        self._pos = point[0], point[1]+h




    def rotate_rad_around(self, angle: float, pivot: tuple[float, float] | Vector2 | str = 'center', dest_pos: tuple[float, float] | Vector2 = Vector2(0, 0)) -> Self:

        match pivot:
            case tuple() | list(): pivot = pivot[:2]
            case 'center': pivot = self.center
            case 'topleft': pivot = self.topleft
            case 'topright': pivot = self.topright
            case 'bottomleft': pivot = self.bottomleft
            case 'bottomright': pivot = self.bottomright
            case 'midbottom': pivot = self.midbottom
            case 'midtop': pivot = self.midtop
            case 'midleft': pivot = self.midleft
            case 'midright': pivot = self.midright
            case _: ValueError(f"Anchor '{pivot}' não suportado.")

        rect = fRect(self.get_rect())

        self._canvas.draw_circle((0, 255, 0), rect[:2], 0.01)
        self._canvas.draw_circle((255, 0, 255), dest_pos, 0.01)

        if not isinstance(pivot, Vector2):
            pivot = Vector2(pivot)
        if not isinstance(dest_pos, Vector2):
            dest_pos = Vector2(dest_pos)

        points = points_from_rect(rect - pivot)
        rot_points = RotateMatrix(angle) * points
        ext_rect = outer_rect(rot_points)
        rot_pos = Vector2(ext_rect[:2]) + dest_pos

        rot_points_shift = tuple(dest_pos + p for p in rot_points)
        self._canvas.draw_lines((255, 255, 255), True, rot_points_shift, 2)
        self._canvas.draw_circle((255, 255, 255), rot_points_shift[0], 0.01)

        rot_img = pygame.transform.rotate(self._surface, angle*180/math.pi)
        rot = Image(self._canvas, surface=rot_img, pos=rot_pos)

        return rot

    def rotate_deg_around(self, angle: float, pivot: tuple[float, float] | Vector2 | str = 'center', dest_pos: tuple[float, float] | Vector2 = Vector2(0, 0)) -> Self:
        return self.rotate_deg_around(angle/180*math.pi, pivot, dest_pos)

    def get_rect(self):
        _, _, sw, sh = self._surface.get_rect()
        return self._pos[0], self._pos[1],  sw/self._canvas.scale, sh/self._canvas.scale

    def draw_rect(self, color: tuple[int, int, int] = (210, 60, 30), width: int = 2, marker_size: float = 0.03):
        # self._canvas.draw_circle(color, self.topleft, marker_size)
        points = (self.topleft, self.topright, self.bottomright, self.bottomleft)
        self._canvas.draw_lines(color, True, points, width)
        self._canvas.draw_polygon(color, (self.topleft, self.topleft + (marker_size, 0), self.topleft - (0, marker_size)))

    def blit(self):
        self._canvas.blit(self._surface, self.get_rect())






