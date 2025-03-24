import pygame
from tools import centered_text

class Overlay():
    def __init__(self, surface, rect,
                 text=None,
                 font=None,
                 active=True,
                 on_focus=True,
                 selectable=True,
                 selected=False,
                 font_color=(120, 120, 120),
                 bg_color=(45, 45, 45),
                 bg_unselectable_color=(30, 30, 30),
                 unselectable_color=(60, 60, 60),
                 border_color=(100, 100, 100),
                 focus_color=(200, 200, 60),
                 bg_selected_color=(90, 90, 30),
                 selected_color=(180, 180, 60),
                 custom_draw=None,
                 custom_callback=None,
                 ):
        self.surface = surface
        self.rect = rect

        self.font = font
        self.text = text
        self.font_color = font_color
        self.unselectable_color = unselectable_color

        self.bg_color = bg_color
        self.bg_selected_color = bg_selected_color
        self.bg_unselectable_color = bg_unselectable_color
        self.border_color = border_color
        self.selected_color = selected_color
        self.focus_color = focus_color

        self.active = active
        self.on_focus = on_focus
        self.selected = selected
        self.selectable = selectable

        self.custom_draw = custom_draw
        self.custom_callback = custom_callback

    def collision(self, point: tuple[int, int]) -> bool:
        if not self.selectable:
            return False
        xmin = self.rect[0]
        xmax = self.rect[0] + self.rect[2]
        ymin = self.rect[1]
        ymax = self.rect[1] + self.rect[3]
        return (xmin <= point[0] <= xmax) and (ymin <= point[1] <= ymax)

    def draw(self):
        if self.active:
            r_border = 15
            font_color = self.selected_color if self.selected else self.font_color if self.selectable else self.unselectable_color
            pygame.draw.rect(self.surface, self.bg_selected_color if self.selected else self.bg_color if self.selectable else self.bg_unselectable_color, self.rect, border_radius=r_border)
            pygame.draw.rect(self.surface, self.focus_color if self.on_focus else font_color, self.rect, border_radius=r_border, width=2)
            if self.selected:
                pygame.draw.rect(self.surface, self.selected_color, self.rect, border_radius=r_border, width=2)

            if self.text is not None and self.font is not None:
                centered_text(self.surface, self.rect, self.text, self.font, font_color)

            if self.custom_draw is not None:
                self.custom_draw(self.surface, rect=self.rect)

    def callback(self):
        if self.custom_callback is not None:
            self.custom_callback()
