import gamebase as gb
import pygame
from pygame import Vector2


class Frame(gb.PopUp):
    def __init__(self, main_canvas: gb.Canvas,
                 rect: gb.Rect_f | tuple[float, float, float, float],
                 *args,
                 origin: str = 'topleft',
                 orientation: str = 'vertical',
                 bg_color: pygame.Color | tuple[int, int, int] | None = None,
                 focus_color: pygame.Color | tuple[int, int, int] | None = (200, 200, 60),
                 border_color: pygame.Color | tuple[int, int, int] | None = (60, 60, 60),
                 border_radius: int = 10,
                 border_width: int = 2,
                 **kwargs
                 ):
        size = Vector2(rect[2:])
        super().__init__(main_canvas, *args, bg_color=bg_color, size=size * main_canvas.scale, **kwargs)
        self.scale = main_canvas.scale
        if origin == 'topleft':
            self.bias = Vector2(0, 0)
        elif origin == 'center':
            self.bias = size / 2 * main_canvas.scale
        else:
            raise ValueError

        if not isinstance(rect, gb.Rect_f):
            rect = gb.Rect_f(rect)
        self.rect = rect

        if orientation.lower() != 'vertical':
            raise NotImplementedError("Apenas orientation='vertical' foi implementado.")

        self.border_color = border_color
        self.focus_color = focus_color
        self.border_radius = border_radius
        self.border_width = border_width
        self.draw_fun = self.default_draw
        self.on_focus = False

        self.components = []

    def register_component(self, new_component):
        self.components.append(new_component)



    def default_draw(self, canvas: gb.Canvas):

        if self.bg_color is not None:
            canvas.draw_rect(self.bg_color, self.rect, 0, self.border_radius)
        if self.border_color is not None and not self.on_focus:
            canvas.draw_rect(self.border_color, self.rect, self.border_width, self.border_radius)
        if self.focus_color is not None and self.on_focus:
            canvas.draw_rect(self.focus_color, self.rect, self.border_width, self.border_radius)


        canvas.blit(self.surface, self.rect[0:2])
        # self.fill(self.bg_color)

    def update(self, game: gb.BaseScreen):

        if self.rect.point_collision(game.mouse.pos) and not self.another_on_focus(self):
            self.on_focus = True
        else:
            self.on_focus = False

        for component in self.components:
            component.update(game)
        self.default_draw(game.canvas)

    def another_on_focus(self, component):
        ret = False
        for other in self.components:
            if component is not other:
                ret |= other.on_focus

        return ret



    def mouse_remap(self, point: Vector2):
        return ((point*self.main_canvas.scale + self.main_canvas.bias) -(Vector2(self.rect[0:2])*self.scale+self.main_canvas.bias+(self.bias[0], -self.bias[1]))) / self.scale