import gamebase as gb
import pygame.transform
from pygame import Vector2


class PopUp(gb.Canvas):
    def __init__(self, main_canvas: gb.Canvas, *args, pos=(0, 0), alpha=255, flags=pygame.HWSURFACE | pygame.SRCALPHA, **kwargs):
        super().__init__(*args, flags=flags, **kwargs)
        self.main_canvas = main_canvas
        self.pos = pos
        self.set_alpha(alpha)

    def collision(self, pos) -> bool:
        _, _, w, h = self.surface.get_rect()
        rect = gb.Rect_f(self.pos[0], self.pos[1], w * self.main_canvas.relative_scale / self.main_canvas.scale, h * self.main_canvas.relative_scale / self.main_canvas.scale)
        return rect.point_collision(pos)

    def blit_to_main(self):
        dest = self.main_canvas
        dest.blit(pygame.transform.smoothscale_by(self.surface, self.main_canvas.relative_scale), self.pos)


class PopUpText(PopUp):
    def __init__(self, *args, color: tuple[int, int, int], font: pygame.font.Font, text: list[str] | str, size=(1, 1), border_width: int = 1, border_radius: int = 0, fill_color: tuple[int, int, int] | tuple[int, int, int, int] | None = None, pad: tuple[int, int] = (10, 10), bg_lerp_factor: float = 0.9,  antialiasing:bool = True, **kwargs):
        super().__init__(*args, size=size, **kwargs)

        if isinstance(text, str):
            text = [text]
        self.text = text

        self.antialiasing = antialiasing
        self.font = font
        self.color = color
        self.bg_lerp_factor = bg_lerp_factor
        if fill_color is None:
            fill_color = gb.lerp_vec3(self.color, self.main_canvas._bg_color, self.bg_lerp_factor)
        self.fill_color = fill_color
        self.border_radius = border_radius
        self.border_width = border_width
        self.pad = pad

        if self.draw_fun is None:
            self.draw_fun = self.default_draw

    def default_draw(self, canvas: gb.Canvas):
        if isinstance(self.text, str):
            self.text = [self.text]
        rects = []
        renders = []
        pad = Vector2(self.pad[0], 0)
        y_max = self.pad[1]
        x_max = 0
        for n, info in enumerate(self.text):
            rendered_text = self.font.render(info, self.antialiasing, self.color)
            text_rect = rendered_text.get_rect()

            pos = pad + Vector2(0, y_max)
            y_max = pos[1] + text_rect[3]
            if text_rect[2] > x_max:
                x_max = text_rect[2]
            text_rect.topleft = pos

            rects.append(text_rect)
            renders.append(rendered_text)

        canvas.surface = pygame.transform.scale(canvas.surface, (x_max + self.pad[0] * 2, y_max + self.pad[1]))

        rect = canvas.get_rect()
        canvas.draw_rect(self.fill_color, rect, 0, self.border_radius)

        for n in range(len(self.text)):
            self.blit(renders[n], self.screen_to_world_rect(rects[n]))

        canvas.draw_rect(self.color, rect, self.border_width, self.border_radius)
