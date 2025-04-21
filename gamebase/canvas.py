import gamebase as gb
import pygame
from typing import Sequence, Callable, Self
from copy import copy
from random import random, uniform, randint, gauss
from pygame import Vector2, Vector3, Rect, Color
from gamebase.utils import fRect


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
        # self.ticks = 0
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

    def clear(self):
        self.fill(self._bg_color)

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

    # def get_rect(self):
    #     return self.surface.get_rect()

    def get_width(self):
        return self.surface.get_width()

    def get_height(self):
        return self.surface.get_height()

    def get_size(self):
        return self.surface.get_size()

    def draw_circle(self, color: Color | tuple[int, int, int] | Vector3, center: Vector2 | tuple[float, float], radius: float, width: int = 0, draw_top_right: bool = False, draw_top_left: bool = False, draw_bottom_left: bool = False, draw_bottom_right: bool = False):
        return pygame.draw.circle(self.surface, color, self.world_to_screen_v2(center), self.world_to_screen_f(radius), width, draw_top_right, draw_top_left, draw_bottom_left, draw_bottom_right)

    def draw_sparkly_line(self, start_pos: Vector2 | tuple[float, float], end_pos: Vector2 | tuple[float, float], color1: Color | tuple[int, int, int] | Vector3 = None, color2: Color | tuple[int, int, int] | Vector3 = None, width: int = 1, density: float = 100, mu: float = 0.0, sigma: float = 1.0, both_sides:bool=True, particle_size: int | tuple[int, int]=1):

        if color1 is None and color2 is None:
            color = randint(0, 255), randint(0, 255), randint(0, 255)
        elif color1 is not None and color2 is None:
            color = color1
        elif color1 is not None and color2 is not None:
            color = gb.lerp_vec3(color1, color2, random())
        else:
            color = color2

        if not isinstance(start_pos, Vector2):
            start_pos = Vector2(start_pos)
        if not isinstance(end_pos, Vector2):
            end_pos = Vector2(end_pos)

        # pygame.draw.line(self.surface, color, self.world_to_screen_v2(start_pos), self.world_to_screen_v2(end_pos), 2)
        vec = Vector2(end_pos-start_pos)
        perp, norm = gb.perpendicular_normal(vec)

        world_width_2 = width / self.scale / 2

        start_pos -= norm * world_width_2 * (1+mu) * sigma
        end_pos += norm * world_width_2 * (1+mu) * sigma

        for _ in range(int((end_pos-start_pos).length()*density)):
            pos = start_pos.lerp(end_pos, random())
            if both_sides:
                pos = pos + perp*world_width_2*gauss(mu, sigma)
            else:
                pos = pos + perp*world_width_2*abs(gauss(mu, sigma))
            psize = particle_size if isinstance(particle_size, int | float) else randint(*particle_size)
            pygame.draw.circle(self.surface, color, self.world_to_screen_v2(pos), psize)





    def draw_aaline(self, color: Color | tuple[int, int, int] | Vector3, start_pos: Vector2 | tuple[float, float], end_pos: Vector2 | tuple[float, float], width: int = 1):
        return pygame.draw.aaline(self.surface, color, self.world_to_screen_v2(start_pos), self.world_to_screen_v2(end_pos), width)

    def draw_lines(self, color: Color | tuple[int, int, int] | Vector3, closed: bool, points: Sequence[tuple[float, float]] | Sequence[Vector2], width: int = 1):
        return pygame.draw.lines(self.surface, color, closed, self.world_to_screen_points(points), width)

    def draw_aalines(self, color: Color | tuple[int, int, int] | Vector3, closed: bool, points: Sequence[tuple[float, float]], width: int = 1):
        return pygame.draw.aalines(self.surface, color, closed, self.world_to_screen_points(points), width)

    def draw_polygon(self, color: Color | tuple[int, int, int] | Vector3, points: Sequence, width: int = 0):
        return pygame.draw.polygon(self.surface, color, self.world_to_screen_points(points), width)

    def draw_rect(self, color: Color | tuple[int, int, int] | Vector3, rect: fRect | Rect | tuple[float, float, float, float], width: int = 0, border_radius: int=-1):
        return pygame.draw.rect(self.surface, color, self.world_to_screen_rect(rect), width, border_radius)

    def draw_line(self, color: Color | tuple[int, int, int] | Vector3, start_pos: Vector2 | tuple[float, float], end_pos: Vector2 | tuple[float, float], width: int = 1):
        return pygame.draw.line(self.surface, color, self.world_to_screen_v2(start_pos), self.world_to_screen_v2(end_pos), width)

    def draw_text(self, color: Color | tuple[int, int, int] | Vector3, font: pygame.font.Font, text: str, pos: Vector2 | tuple[float, float], anchor='center', shift: Vector2 | tuple[float, float] = (0, 0)):
        rendered_text = self.render_text(color, font, text)
        if not isinstance(shift, Vector2):
            shift = Vector2(shift)
        return self.blit_text(rendered_text, shift+pos, anchor)

    def render_text(self, color: Color | tuple[int, int, int] | Vector3, font: pygame.font.Font, text: str):
        return font.render(text, True, color)

    def blit_text(self, rendered_text, pos: Vector2 | tuple[float, float], anchor='center'):
        text_rect = rendered_text.get_rect()
        pos = self.world_to_screen_v2(pos)
        match anchor:
            case 'center': text_rect.center = pos
            case 'topleft': text_rect.topleft = pos
            case 'topright': text_rect.topright = pos
            case 'bottomleft': text_rect.bottomleft = pos
            case 'bottomright': text_rect.bottomright = pos
            case 'midbottom': text_rect.midbottom = pos
            case 'midtop': text_rect.midtop = pos
            case 'midleft': text_rect.midleft = pos
            case 'midright': text_rect.midright = pos
            case _: ValueError(f"Anchor '{anchor}' não suportado.")
        self.blit(rendered_text, self.screen_to_world_rect(text_rect))
        return self.screen_to_world_rect(text_rect)

    @property
    def center(self):
        x, y, w, h = self.get_rect()
        print(Vector2(x+w/2, y-h/2))
        return Vector2(x+w/2, y-h/2)

    @property
    def topleft(self):
        x, y, *_ = self.get_rect()
        return Vector2(x, y)

    @property
    def xmin(self) -> float:
        x, *_ = self.get_rect()
        return x

    @property
    def ymin(self) -> float:
        _, y, *_ = self.get_rect()
        return -y

    @property
    def xmax(self) -> float:
        x, _, w, _ = self.get_rect()
        return x + w

    @property
    def ymax(self) -> float:
        _, y, _, h = self.get_rect()
        return -y + h

    def center_pixels(self):
        return self.world_to_screen_v2(self.center)

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

    def get_rect(self) -> tuple[float, float, float, float]:
        return self.screen_to_world_rect(self.surface.get_rect())


    def fill(self, color, rect=None, special_flags=0):
        self.surface.fill(color, rect, special_flags)

    def blit(self, source: Self | pygame.Surface, dest_pos, area=None, special_flags=0):
        if not self.visible:
            return 0, 0, 0, 0
        if isinstance(source, Canvas):
            if not source.visible:
                return 0, 0, 0, 0
            source = source.surface
        return self.surface.blit(source, self.world_to_screen_v2(dest_pos), area, special_flags)


def remap(point: tuple[float, float] | Vector2, origin: tuple[float, float, float, float] | Canvas | pygame.Surface, dest: tuple[float, float, float, float] | Canvas | pygame.Surface) -> Vector2:
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

    return Vector2(dx, dy)


def blit_with_aspect_ratio(dest: Canvas, source: Canvas, antialiasing=True, offset: tuple[int, int] | None = None):
    source_size = source.get_size()
    dest_size = dest.get_size()

    source_ratio = source_size[0] / source_size[1]
    dest_ratio = dest_size[0] / dest_size[1]

    if source_size == dest_size:
        scaled_surface = source.copy()
        if offset is None:
            offset = (0, 0)
    else:
        rescale = pygame.transform.smoothscale if antialiasing else pygame.transform.scale
        if source_ratio > dest_ratio:
            new_width = dest_size[0]
            new_height = int(dest_size[0] / source_ratio)
        else:
            new_height = dest_size[1]
            new_width = int(dest_size[1] * source_ratio)
        scaled_surface = rescale(source.surface, (new_width, new_height))
        if offset is None:
            offset = (dest_size[0] - new_width) // 2, (dest_size[1] - new_height) // 2   # centralizada
    dest.blit(scaled_surface, dest.screen_to_world_v2(offset))