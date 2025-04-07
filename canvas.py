import pygame
from pygame import Vector2, Rect
from typing import Sequence
from pygame import Color
from typing import Callable
import math
from copy import deepcopy


class Canvas(pygame.Surface):
    def __init__(self,
                 size: Vector2 | tuple[int, int],
                 flags: pygame.constants,
                 bg_color: Color | tuple[int, int, int],
                 draw_fun: Callable = None,
                 shortcut: pygame.constants = None,
                 scale: float | None = None,
                 bias: Vector2 | tuple[float, float] | None = None,
                 ):


        super().__init__(size, flags)

        self.base_scale = min(*size) / 2
        if scale is None:
            scale = self.base_scale

        if bias is None:
            bias = (size[0] // 2, size[1] // 2)

        self.bg_color: Color = bg_color
        self.draw = draw_fun
        self.shortcut = shortcut
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

    def draw_polygon(self, color: Color | tuple[int, int, int], points: Sequence, width: int = 0):
        return pygame.draw.polygon(self, color, self.world_to_screen_points(points), width)

    def world_to_screen_v2(self, vec: Vector2) -> Vector2:
        return Vector2(round(vec[0] * self.scale + self.bias[0]), round(-vec[1] * self.scale + self.bias[1]))

    def world_to_screen_rect(self, rect: Rect) -> Rect:
        return Rect(round(rect[0] * self.scale + self.bias[0]), round(-rect[1] * self.scale + self.bias[1]), rect[2]*self.scale, rect[3]*self.scale)

    def screen_to_world_rect(self, rect: Rect) -> tuple[float, float, float, float]:
        return (rect[0] - self.bias[0]) / self.scale, (-rect[1] - self.bias[1]) / self.scale, rect[2]/self.scale, rect[3]/self.scale

    def world_to_screen_points(self, points: Sequence) -> Sequence:
        return tuple(self.world_to_screen_v2(point) for point in points)

    def world_to_screen_f(self, dist: float) -> int:
        return round(dist * self.scale)

    def get_world_rect(self) -> tuple[float, float, float, float]:
        return self.screen_to_world_rect(self.get_rect())

    def blit(self, source, dest, area=None, special_flags=0):
        super().blit(source, self.world_to_screen_v2(dest), area, special_flags)
    # def blit(self, rendered_text: pygame.Surface, pos, rescale=False):
    #     if (self.fullscreen_mode or self.global_scale != 1) and rescale:
    #         factor = min(self.fullscreen_scale_factor) * self.global_scale
    #         rendered_text = pygame.transform.scale(rendered_text, (
    #         rendered_text.get_width() * factor, rendered_text.get_height() * factor))
    #     self.screen.blit(rendered_text, self.world_to_screen(pos))


def rotate_around_v2(vec: Vector2, angle: float, center: Vector2 = (0.0, 0.0)):
    if not isinstance(vec, Vector2):
        vec = Vector2(vec)
    return (vec - center).rotate_rad(angle) + center


def rotate_vec2s(vecs: Sequence[Vector2] | Sequence[tuple[float, float]], angle: float, center: Vector2 = (0.0, 0.0)) -> Sequence:
    return tuple(rotate_around_v2(vec, angle, center) for vec in vecs)
