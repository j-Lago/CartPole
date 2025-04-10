import pygame
from pygame import Vector2, Rect, Vector3
from typing import Sequence
from pygame import Color
from typing import Callable
from copy import copy, deepcopy
import math
from copy import deepcopy
from typing import Self


class Canvas:
    def __init__(self,
                 size: Vector2 | tuple[int, int] = (0, 0),
                 flags: pygame.constants = 0,
                 surface: pygame.Surface | None = None,
                 bg_color: Color | tuple[int, int, int] = (0, 0, 0, 0),
                 fonts: dict | None = None,
                 scale: float | None = None,
                 bias: Vector2 | tuple[float, float] | None = None,
                 visible: bool = True,
                 shortcut: pygame.constants = None,
                 draw_fun: Callable = None,
                 got_focus_callback: Callable = None
                 ):
        self.fonts = fonts
        self.visible = visible
        self.got_focus_callback = got_focus_callback
        self._bg_color: Color = bg_color
        self.draw_fun = draw_fun
        self.shortcut = shortcut
        self.ticks = 0
        self.base_scale = 1.0
        if surface is None:
            self.surface = pygame.Surface(size, flags)
            self.base_scale = min(*size) / 2
            if scale is None:
                scale = self.base_scale
            if bias is None:
                bias = (size[0] // 2, size[1] // 2)
            self.scale = scale
            self.bias = bias
        else:
            self.surface = surface
            self.size = surface.get_size()
            self.scale = 1.0
            self.bias = (0, 0)

        self._last_alpha = self.surface.get_alpha()



    def got_focus(self):
        if self.got_focus_callback is not None:
            self.got_focus_callback(self)

    def draw(self):
        self.fill(self._bg_color)
        if self.visible:
            if self._last_alpha != self.surface.get_alpha():
                self.surface.set_alpha(self._last_alpha)
            self.draw_fun(canvas=self)
        else:
            self.surface.set_alpha(0)

    def copy(self):
        ret = copy(self)
        ret.surface = self.surface.copy()
        return ret

    def set_alpha(self, value):
        self.surface.set_alpha(value)
        self._last_alpha = self.surface.get_alpha()

    @property
    def relative_scale(self):
        return self.scale / self.base_scale

    def get_rect(self):
        return self.surface.get_rect()

    def get_width(self):
        return self.surface.get_width()

    def get_height(self):
        return self.surface.get_height()

    def get_size(self):
        return self.surface.get_size()

    def draw_circle(self, color: Color | tuple[int, int, int] | Vector3, center: Vector2 | tuple[float, float], radius: float, width: int = 0, draw_top_right: bool = False, draw_top_left: bool = False, draw_bottom_left: bool = False, draw_bottom_right: bool = False):
        return pygame.draw.circle(self.surface, color, self.world_to_screen_v2(center), self.world_to_screen_f(radius), width, draw_top_right, draw_top_left, draw_bottom_left, draw_bottom_right)

    def draw_line(self, color: Color | tuple[int, int, int] | Vector3, start_pos: Vector2 | tuple[float, float], end_pos: Vector2 | tuple[float, float], width: int = 1):
        return pygame.draw.line(self.surface, color, self.world_to_screen_v2(start_pos), self.world_to_screen_v2(end_pos), width)

    def draw_aaline(self, color: Color | tuple[int, int, int] | Vector3, start_pos: Vector2 | tuple[float, float], end_pos: Vector2 | tuple[float, float], width: int = 1):
        return pygame.draw.aaline(self.surface, color, self.world_to_screen_v2(start_pos), self.world_to_screen_v2(end_pos), width)

    def draw_lines(self, color: Color | tuple[int, int, int] | Vector3, closed: bool, points: Sequence[tuple[float, float]], width: int = 1):
        return pygame.draw.lines(self.surface, color, closed, self.world_to_screen_points(points), width)

    def draw_aalines(self, color: Color | tuple[int, int, int] | Vector3, closed: bool, points: Sequence[tuple[float, float]], width: int = 1):
        return pygame.draw.aalines(self.surface, color, closed, self.world_to_screen_points(points), width)

    def draw_polygon(self, color: Color | tuple[int, int, int] | Vector3, points: Sequence, width: int = 0):
        return pygame.draw.polygon(self.surface, color, self.world_to_screen_points(points), width)

    def draw_rect(self, color: Color | tuple[int, int, int] | Vector3, rect: Rect | tuple[float, float, float, float], width: int = 0, border_radius: int=-1):
        return pygame.draw.rect(self.surface, color, self.world_to_screen_rect(rect), width, border_radius)

    def draw_text(self, color: Color | tuple[int, int, int] | Vector3, font: pygame.font.Font, text: str, pos: Vector2 | tuple[float, float], anchor='center'):
        rendered_text = font.render(text, True, color)
        text_rect = rendered_text.get_rect()
        pos = self.world_to_screen_v2(pos)
        match anchor:
            case 'center'     : text_rect.center = pos
            case 'topleft'    : text_rect.topleft = pos
            case 'topright'   : text_rect.topright = pos
            case 'bottomleft' : text_rect.bottomleft = pos
            case 'bottomright': text_rect.bottomright = pos
            case 'midbottom'  : text_rect.midbottom = pos
            case 'midtop'     : text_rect.midtop = pos
            case 'midleft'    : text_rect.midleft = pos
            case 'midright'   : text_rect.midright = pos
            case _: ValueError(f"Anchor '{anchor}' não suportado.")
        self.blit(rendered_text, self.screen_to_world_rect(text_rect))
        return text_rect

    def world_to_screen_v2(self, vec: Vector2) -> Vector2:
        return Vector2(round(vec[0] * self.scale + self.bias[0]), round(-vec[1] * self.scale + self.bias[1]))

    def world_to_screen_rect(self, rect: Rect) -> Rect:
        return Rect(round(rect[0] * self.scale + self.bias[0]), round(-rect[1] * self.scale + self.bias[1]), rect[2]*self.scale, rect[3]*self.scale)

    def screen_to_world_rect(self, rect: Rect) -> tuple[float, float, float, float]:
        return (rect[0] - self.bias[0]) / self.scale, (-rect[1] + self.bias[1]) / self.scale, rect[2]/self.scale, rect[3]/self.scale  # todo: verificar

    def screen_to_world_v2(self, vec: Vector2 | tuple[float, float]) -> Vector2:
        return Vector2((vec[0] - self.bias[0]) / self.scale, (-vec[1] + self.bias[1]) / self.scale)  # todo: verificar

    def screen_to_world_delta_v2(self, vec: Vector2 | tuple[float, float]) -> Vector2:
        return Vector2(vec[0] / self.scale, -vec[1] / self.scale)


    def world_to_screen_points(self, points: Sequence) -> Sequence:
        return tuple(self.world_to_screen_v2(point) for point in points)

    def world_to_screen_f(self, dist: float) -> int:
        return round(dist * self.scale)

    def get_world_rect(self) -> tuple[float, float, float, float]:
        return self.screen_to_world_rect(self.get_rect())

    def fill(self, color, rect=None, special_flags=0):
        self.surface.fill(color, rect, special_flags)

    def blit(self, source: Self | pygame.Surface, dest, area=None, special_flags=0):
        if not self.visible:
            return 0, 0, 0, 0
        if isinstance(source, Canvas):
            if not source.visible:
                return 0, 0, 0, 0
            source = source.surface
        return self.surface.blit(source, self.world_to_screen_v2(dest), area, special_flags)


def rotate_around_v2(vec: Vector2, angle: float, center: Vector2 = (0.0, 0.0)):
    if not isinstance(vec, Vector2):
        vec = Vector2(vec)
    return (vec - center).rotate_rad(angle) + center


def rotate_vec2s(vecs: Sequence[Vector2] | Sequence[tuple[float, float]], angle: float, center: Vector2 = (0.0, 0.0)) -> Sequence:
    return tuple(rotate_around_v2(vec, angle, center) for vec in vecs)


# def resolution_map(dest: Canvas, source: Canvas, source_pos: Vector2 | tuple[int, int]) -> Vector2:
#     dw, dh = dest.get_size()
#     sw, sh = source.get_size()
#     return Vector2(round(source_pos[0] / sw * dw), round(source_pos[1] / sh * sw))