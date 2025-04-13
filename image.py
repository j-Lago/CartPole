import pygame
from pathlib import Path
from pygame import Vector2
from canvas import Canvas
import math
from utils import outer_rect, points_from_rect, RotateMatrix
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




    def rotate_deg_around(self, angle: float, pivot: tuple[float, float] | Vector2) -> Self:
        img_screen_rect = self._surface.get_rect()

        screen_pivot = self._canvas.world_to_screen_v2(pivot)
        img_screen_rect.midtop = screen_pivot         # todo: criar Rect_f
        img_rect = self._canvas.screen_to_world_rect(img_screen_rect)

        points = points_from_rect(img_rect)

        rot_points = RotateMatrix(math.degrees(angle)) * points

        ext_rect = outer_rect(rot_points)
        ext_points = points_from_rect(ext_rect)
        rot_img = pygame.transform.rotate(self._surface, math.degrees(angle))
        return Image(self._canvas, surface=rot_img, pos=ext_rect[:2])

    def rotate_rad_around(self, angle: float, pivot: tuple[float, float] | Vector2) -> Self:
        return self.rotate_deg_around(math.degrees(angle), pivot)

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






