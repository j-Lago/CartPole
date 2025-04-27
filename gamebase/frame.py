import gamebase as gb
import pygame
from pygame import Vector2


class Frame(gb.PopUp):
    def __init__(self, main_canvas: gb.Canvas,
                 rect: gb.Rect_f | tuple[float, float, float, float],
                 *args,
                 origin: str = 'topleft',
                 items: gb.PopUp = None,
                 # bg_color = (35, 35, 35),
                 border_color = (60, 60, 60),
                 border_radius: int = 10,
                 border_width: int = 2,
                 **kwargs
                 ):
        size = Vector2(rect[2:])
        super().__init__(main_canvas, *args, size=size * main_canvas.scale, **kwargs)
        self.scale = main_canvas.scale
        if origin == 'topleft':
            self.bias = Vector2(0, 0)
        elif origin == 'center':
            self.bias = size / 2 * main_canvas.scale
        else:
            raise ValueError

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

        # self.draw_rect(self.bg_color, self.rect, 0, self.border_radius)
        # self.draw_rect(self.border_color, self.rect, self.border_width, self.border_radius)
        self.draw_circle((255, 255, 0), (0, 0), .02)
        self.draw_circle((255, 255, 0), (-1, 1), .1)
        self.draw_circle((255, 255, 0), (-1, -1), .1)
        self.draw_circle((255, 255, 0), (1, -1), .1)
        self.draw_circle((255, 255, 0), (1, 1), .1)

        for i in range(10):
            self.draw_circle((255, 25 * (10-i), 25*i), (-0.1 * i, 0.1 * i), .02)
            self.draw_circle((255, 25 * (10-i), 25*i), (-0.1 * i, -0.1 * i), .02)
            self.draw_circle((255, 25 * (10-i), 25*i), (0.1 * i, -0.1 * i), .02)
            self.draw_circle((255, 25 * (10-i), 25*i), (0.1 * i, 0.1 * i), .02)

        canvas.blit(self.surface, self.rect[0:2])
        self.fill((60, 30, 30))

    def update(self, game:gb.BaseScreen):
        self.default_draw(game.canvas)
        # self.draw()



    def mouse_remap(self, point: Vector2):
        return ((point*self.main_canvas.scale + self.main_canvas.bias) -(Vector2(self.rect[0:2])*self.scale+self.main_canvas.bias+(self.bias[0], -self.bias[1]))) / self.scale