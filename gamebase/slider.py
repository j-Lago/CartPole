import gamebase as gb
import pygame
from typing import Callable

class Slider():
    def __init__(self,
                 canvas: gb.Canvas,
                 rect: gb.Rect_f | tuple[float, float, float, float],
                 max_value = 1.0,
                 min_value = 0.0,
                 init_value = 0.0,
                 text: str | None = None,
                 font: pygame.font.Font = None,
                 active: bool = True,
                 on_focus: bool = False,
                 selectable: bool = True,
                 selected: bool = False,
                 font_color: pygame.Color | tuple[int, int, int] = (120, 120, 120),
                 bg_color: pygame.Color | tuple[int, int, int] = (45, 45, 45),
                 bg_unselectable_color: pygame.Color | tuple[int, int, int] = (30, 30, 30),
                 unselectable_color: pygame.Color | tuple[int, int, int] = (60, 60, 60),
                 font_unselectable_color: pygame.Color | tuple[int, int, int] = (45, 45, 45),
                 border_color: pygame.Color | tuple[int, int, int] = (100, 100, 100),
                 focus_color: pygame.Color | tuple[int, int, int] = (200, 200, 60),
                 font_focus_color: pygame.Color | tuple[int, int, int] = (200, 200, 60),
                 bg_selected_color: pygame.Color | tuple[int, int, int] = (90, 90, 30),
                 selected_color: pygame.Color | tuple[int, int, int] = (180, 180, 60),
                 fg_color: pygame.Color | tuple[int, int, int] = (120, 120, 120),
                 font_selected_color: pygame.Color | tuple[int, int, int] = (180, 180, 60),
                 border_width: int = 2,
                 custom_draw: Callable = None,
                 custom_focus: Callable = None,
                 custom_callback: Callable = None,
                 ):

        self.canvas = canvas
        self.max_value = max_value
        self.min_value = min_value
        self.init_value = init_value

        if not isinstance(rect, gb.Rect_f):
            rect = gb.Rect_f(rect)
        self.rect = rect

        self.font = font
        self.text = text
        self.font_color = font_color
        self.unselectable_color = unselectable_color
        self.font_unselectable_color = font_unselectable_color
        self.font_selected_color = font_selected_color
        self.font_focus_color = font_focus_color
        self.fg_color = fg_color

        self.bg_color = bg_color
        self.bg_selected_color = bg_selected_color
        self.bg_unselectable_color = bg_unselectable_color
        self.border_color = border_color
        self.selected_color = selected_color
        self.focus_color = focus_color
        self.border_width = border_width
        self.border_radius = rect[2] / 2

        self.active = active
        self.on_focus = on_focus
        self.selected = selected
        self.selectable = selectable

        self.handle_on_focus = False
        self.drag_qualifier = False

        self.custom_draw = custom_draw
        self.custom_focus = custom_focus
        self.custom_callback = custom_callback

        self._clicked = False

        self.norm_value = 0.0
        self.value = init_value # set self.norm_value

    @property
    def value(self):
        return self.norm_value*(self.max_value-self.min_value) + self.min_value

    @value.setter
    def value(self, new_value):
        self.norm_value = max(0.0, min(1.0, (new_value-self.min_value) / (self.max_value-self.min_value)))

    def collision(self, point: gb.Vector2 | tuple[float, float]) -> bool:
        if not self.selectable:
            return False

        xmin = self.rect[0]
        xmax = self.rect[0] + self.rect[2]
        ymax = self.rect[1]
        ymin = self.rect[1] - self.rect[3]
        return (xmin <= point[0] <= xmax) and (ymin <= point[1] <= ymax)

    def draw(self):
        if self.active:
            r_border = round(self.border_radius * self.canvas.scale)
            font_color = self.font_selected_color if self.selected else self.font_color if self.selectable else self.font_unselectable_color
            if self.on_focus:
                font_color = self.focus_color
            self.canvas.draw_rect(self.bg_selected_color if self.selected else self.bg_color if self.selectable else self.bg_unselectable_color, self.rect, border_radius=r_border)

            if self.selected:
                self.canvas.draw_rect(self.selected_color, self.rect, width=self.border_width, border_radius=r_border)

            # if self.text is not None and self.font is not None:
            #     pos = self.rect.center
            #     self.canvas.draw_text(font_color, self.font, self.text, pos, anchor='center')

            if self.custom_draw is not None:
                self.custom_draw(self.canvas, rect=self.rect)

            # self.norm_value = self.norm_value + 0.001
            # if self.norm_value > 1:
            #     self.norm_value = 0.0

            # print(self.norm_value)


            y_inf = self.rect.y - self.rect.h + self.border_radius
            y_sup = self.rect.y - self.border_radius - (1 - self.norm_value) * (self.rect.h - 2 * self.border_radius)
            x_cen = self.rect.center[0]

            self.canvas.draw_circle(self.fg_color, (x_cen, y_inf), self.border_radius, 0)
            self.canvas.draw_circle(self.fg_color, (x_cen, y_sup), self.border_radius, 0)

            self.canvas.draw_rect(self.fg_color, gb.Rect_f(self.rect[0], y_sup, self.rect[2], y_sup-y_inf), 0)



            color, width = ((200, 200, 30), 3) if self.handle_on_focus else (self.bg_color, 2)
            self.canvas.draw_circle(color, (x_cen, y_sup), self.border_radius, width)

            if self.text is not None and self.font is not None:
                self.canvas.draw_text(self.bg_color, self.font, self.text, (x_cen, y_sup), 'center')

            self.canvas.draw_rect(self.focus_color if self.on_focus else font_color, self.rect, border_radius=r_border, width=self.border_width)

    def update(self, game: gb.BaseScreen):
        self.handle_on_focus = gb.point_circle_collision(game.mouse.pos, (self.rect.center[0],self.rect.y - self.border_radius - (1 - self.norm_value) * (self.rect.h - 2 * self.border_radius)),self.border_radius)

        self.focus(game.mouse.pos)

        if self.on_focus and game.mouse.left.pressed:
            if not self._clicked:
                self._clicked = True
                self.callback()
        else:
            self._clicked = False

        if game.mouse.left.pressed:
            self.drag_qualifier |= gb.point_circle_collision(game.mouse.left.presspos, (self.rect.center[0],self.rect.y - self.border_radius - (1 - self.norm_value) * (self.rect.h - 2 * self.border_radius)),self.border_radius)
        else:
            self.drag_qualifier = False

        if game.mouse.left.dragging and self.drag_qualifier:
            self.norm_value = (game.mouse.left.dragpos[1] - (self.rect.y - self.rect.h + self.border_radius)) / (self.rect.h - 2*self.border_radius)
            self.norm_value = max(0.0, min(1.0, self.norm_value))

        self.draw()

    def callback(self):
        if self.custom_callback is not None:
            self.custom_callback(self)

    def focus(self, point: gb.Vector2 | tuple[float, float]):
        if self.custom_focus is not None:
            self.custom_focus()
        else:
            self.on_focus = self.collision(point)
