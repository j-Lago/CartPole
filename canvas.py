import pygame
from pygame import Vector2, Rect
from pygame import Color
from typing import Callable


class Canvas(pygame.Surface):
    def __init__(self,
                 size: Vector2,
                 flags: pygame.constants,
                 bg_color: Color,
                 draw_fun: Callable,
                 shortcut: pygame.constants,
                 scale: float | None = None,
                 bias: Vector2 | None = None,
                 ):
        super().__init__(size, flags)
        self.bg_color: Color = bg_color
        self.draw = draw_fun
        self.shortcut = shortcut

        self.base_scale = min(*size) / 2
        if scale is None:
            scale = self.base_scale

        if bias is None:
            bias = (size[0] // 2, size[1] // 2)

        self.scale = scale
        self.bias = bias
        self.last_bias = bias
        self.ticks = 0

    @property
    def relative_scale(self):
        return self.scale / self.base_scale

    def draw_circle(self, color: Color | tuple[int, int, int], center: Vector2 | tuple[float, float], radius: float, width: int = 0, draw_top_right: bool = False, draw_top_left: bool = False, draw_bottom_left: bool = False, draw_bottom_right: bool = False):
        return pygame.draw.circle(self, color, self.world_to_screen_v2(center), self.world_to_screen_f(radius), width, draw_top_right, draw_top_left, draw_bottom_left, draw_bottom_right)

    def draw_line(self, color: Color | tuple[int, int, int], start_pos: Vector2 | tuple[float, float], end_pos: Vector2 | tuple[float, float], width: int = 1):
        return pygame.draw.line(self, color, self.world_to_screen_v2(start_pos), self.world_to_screen_v2(end_pos), width)

    def world_to_screen_v2(self, vec: Vector2) -> Vector2:
        return Vector2(round(vec[0] * self.scale + self.bias[0]), round(-vec[1] * self.scale + self.bias[1]))

    def world_to_screen_f(self, dist: float) -> int:
        return round(dist * self.scale)
