import gamebase as gb
import pygame
from pygame import Vector2


class Frame(gb.PopUp):
    def __init__(self, main_canvas: gb.Canvas, rect: gb.Rect_f | tuple[float, float, float, float], *args,
                 items: gb.PopUp = None,
                 # bg_color = (35, 35, 35),
                 border_color = (60, 60, 60),
                 border_radius: int = 10,
                 border_width: int = 2,
                 **kwargs
                 ):
        super().__init__(main_canvas, *args, **kwargs)
        if isinstance(rect, gb.Rect_f):
            rect = gb.Rect_f(rect)
        self.rect = rect
        if items is None:
            items = []
        self.items = items

        # self.bg_color = bg_color
        self.border_color = border_color
        self.border_radius = border_radius
        self.border_width = border_width

        self.draw_fun = self.default_draw

    def default_draw(self, canvas: gb.Canvas):
        self.fill((60, 30, 30))
        # self.draw_rect(self.bg_color, self.rect, 0, self.border_radius)
        # self.draw_rect(self.border_color, self.rect, self.border_width, self.border_radius)
        self.draw_circle((255, 255, 0), (0, 0), .1)
        self.draw_circle((255, 255, 0), (-1, 1), .1)
        self.draw_circle((255, 255, 0), (-1, -1), .1)
        self.draw_circle((255, 255, 0), (1, -1), .1)
        self.draw_circle((255, 255, 0), (1, 1), .1)
        canvas.blit(self.surface, (.4, -.2))

    def update(self, game:gb.BaseScreen):
        self.default_draw(game.canvas)
        # self.draw()



