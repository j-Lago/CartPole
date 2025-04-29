import gamebase as gb
import pygame
from typing import Callable




class Button():
    def __init__(self,
                 canvas: gb.Canvas,
                 rect: gb.Rect_f | tuple[float, float, float, float],
                 state: bool = False,
                 text: tuple[str, str] | str | None = None,
                 text_font: pygame.font.Font = None,
                 label_font: pygame.font.Font = None,
                 active: bool = True,
                 unselectable: bool = False,
                 on_focus: bool = False,
                 on_color: pygame.Color | tuple[int, int, int] = (120, 120, 120),
                 off_color: pygame.Color | tuple[int, int, int] = (45, 45, 45),
                 focus_color: pygame.Color | tuple[int, int, int] | None = (200, 200, 60),
                 unselectable_color: pygame.Color | tuple[int, int, int] = (60, 60, 60),
                 label_color: pygame.Color | tuple[int, int, int] | None = None,
                 label_bg_color: pygame.Color | tuple[int, int, int] | None = (30, 30, 30, 0),
                 border_width: int = 2,
                 custom_draw: Callable = None,
                 custom_focus: Callable = None,
                 press_callback: Callable = None,
                 release_callback: Callable = None,
                 toggle_callback: Callable = None,
                 toggle: bool = False,
                 radio: bool = False,
                 label: tuple[str, str] | str | None = None,
                 label_pos: tuple[float, float] = (0.02, 0.0),
                 ):

        if text_font is None and text is not None:
            raise ValueError("Uma 'font' deve ser fornecida já que 'text' não é 'None'.")

        if isinstance(canvas, gb.Frame):
            canvas.register_component(self)
        self.canvas = canvas

        self.state = state
        self.unselectable = unselectable
        self.active = active
        self.on_focus = on_focus


        if not isinstance(rect, gb.Rect_f):
            rect = gb.Rect_f(rect)
        self.rect = rect

        self.text_font = text_font
        if isinstance(text, str):
            text = (text, text)
        self.text = text
        if isinstance(label, str):
            label = (label, label)
        self.label = label
        self.label_color = label_color if label_color is not None else on_color
        self.label_font = label_font if label_font is not None else text_font
        self.label_pos = label_pos

        if radio and not isinstance(canvas, gb.Frame):
            raise ValueError("A opção 'radio' só funciona em conjunto com um 'canvas' do tipo 'Frame'.")

        self.toggle = toggle or radio
        self.radio = radio

        self.on_color = on_color
        self.off_color = off_color
        self.focus_color = focus_color
        self.unselectable_color = unselectable_color
        self.label_bg_color = label_bg_color

        self.border_width = border_width
        self.border_radius = rect[2] / 2

        self.handle_on_focus = False
        self.drag_qualifier = False

        self.custom_draw = custom_draw
        self.custom_focus = custom_focus
        self.press_callback = press_callback
        self.release_callback = release_callback
        self.toggle_callback = toggle_callback

        self._clicked = False



    def collision(self, point: gb.Vector2 | tuple[float, float]) -> bool:
        if self.unselectable:
            return False
        return self.rect.point_collision(point)

    def draw(self):
        if self.active:
            if self.custom_draw is not None:
                self.custom_draw(self.canvas, rect=self.rect)
                return

            r_border = round(self.border_radius * self.canvas.scale)

            font_color = self.focus_color if self.on_focus and self.focus_color is not None else (self.off_color if self.state else self.on_color)
            border_color = self.focus_color if self.on_focus and self.focus_color is not None else (self.off_color if self.state else self.on_color)
            self.canvas.draw_rect((self.on_color if self.state else self.off_color), self.rect, border_radius=r_border)  # sombra

            if self.text is not None and self.text_font is not None:
                self.canvas.draw_text(font_color, self.text_font, self.text[0] if self.state else self.text[1], self.rect.center, 'center')
            if self.label is not None and self.label_font is not None:
                self.canvas.draw_text((255,255,255), self.label_font, self.label[0] if self.state else self.label[1], self.rect.midright, 'midleft', self.label_pos, self.label_bg_color)

            self.canvas.draw_rect(border_color, self.rect, border_radius=r_border, width=self.border_width) # border

    def update(self, game: gb.BaseScreen):
        self.focus(game)
        self.draw()


    def focus(self, game: gb.BaseScreen):
        point = self.mouse_remap(game.mouse.pos)
        if self.custom_focus is not None:
            self.custom_focus()
        else:
            if isinstance(self.canvas, gb.Frame):
                self.on_focus = (self.collision(point) and (not self.canvas.any_subcomponent_on_focus(self))) and (not gb.DragLock.another_on_focus(self.canvas))
            else:
                self.on_focus = self.collision(point)

        if self.on_focus and game.mouse.left.pressed:
            if not self._clicked:
                self._clicked = True
                if self.toggle:
                    if not self.radio:
                        self.state = not self.state
                    else:
                        if self._clicked:
                            if not self.state:
                                self.state = True
                                if self.toggle_callback is not None:
                                    self.toggle_callback(self)
                            for comp in self.canvas.components:
                                if comp is not self and isinstance(comp, Button):
                                    if comp.radio and comp.state:
                                        comp.state = False
                                        if comp.toggle_callback is not None:
                                            comp.toggle_callback(comp)


                if not self.toggle and self.press_callback is not None:
                    self.press_callback(self)

        if not game.mouse.left.pressed:
            if not self.toggle and self.on_focus and self._clicked and self.release_callback is not None:
                self.release_callback(self)
            self._clicked = False

        if not self.on_focus:
            self._clicked = False

        if not self.toggle:
            self.state = self._clicked





    def mouse_remap(self, point: gb.Vector2):
        if isinstance(self.canvas, gb.Frame):
            return self.canvas.mouse_remap(point)
        return point