import gamebase as gb
import pygame
from pygame import Vector2, Surface
from pathlib import Path
import math
from typing import Self



class Image:
    def __init__(self, canvas: gb.Canvas, surface: Surface | None = None, pos: tuple[float, float] | Vector2 = Vector2(0, 0), file_path: Path | None = None):
        self._canvas = canvas
        if file_path is not None:
            self._surface: Surface = pygame.image.load(file_path)
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

    def rotate_rad_around(self, angle: float, anchor: tuple[float, float] | Vector2 | str = 'center', dest_pos: tuple[float, float] | Vector2 = Vector2(0, 0)) -> Self:
        match anchor:
            case tuple() | list(): anchor = Vector2(anchor[0], -anchor[1])
            case _ if isinstance(anchor, Vector2): anchor = Vector2(anchor[0], -anchor[1])
            case 'center': anchor = self.center
            case 'topleft': anchor = self.topleft
            case 'topright': anchor = self.topright
            case 'bottomleft': anchor = self.bottomleft
            case 'bottomright': anchor = self.bottomright
            case 'midbottom': anchor = self.midbottom
            case 'midtop': anchor = self.midtop
            case 'midleft': anchor = self.midleft
            case 'midright': anchor = self.midright
            case _: ValueError(f"Anchor '{anchor}' não suportado.")

        if not isinstance(dest_pos, Vector2):
            dest_pos = Vector2(dest_pos)

        rect = gb.fRect(self.get_rect())
        points = gb.points_from_rect(rect - anchor)
        rot_points = gb.RotateMatrix(angle) * points
        ext_rect = gb.outer_rect(rot_points)
        rot_pos = Vector2(ext_rect[:2]) + dest_pos

        rot_img = pygame.transform.rotate(self._surface, angle*180/math.pi)
        rot = Image(self._canvas, surface=rot_img, pos=rot_pos)

        return rot

    def rotate_deg_around(self, angle: float, anchor: tuple[float, float] | Vector2 | str = 'center', dest_pos: tuple[float, float] | Vector2 = Vector2(0, 0)) -> Self:
        return self.rotate_deg_around(angle / 180 * math.pi, anchor, dest_pos)

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






