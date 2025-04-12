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
        self.pos = pos

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
        return self.pos[0], self.pos[1], self._canvas.relative_scale*sw+self.pos[0], self._canvas.relative_scale*sh+self.pos[1]

    def blit(self):
        self._canvas.blit(self._surface, self.get_rect())






