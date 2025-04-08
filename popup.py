import pygame.transform

from canvas import Canvas
from utils import collision_point_rect

class PopUp(Canvas):
    def __init__(self, main_canvas: Canvas, *args, pos=(0, 0), alpha=255, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_canvas = main_canvas
        self.pos = pos
        self.set_alpha(alpha)

    def collision(self, pos) -> bool:
        _, _, w, h = self.get_rect()
        return collision_point_rect(pos, (self.pos[0], self.pos[1], w/self.main_canvas.scale, h/self.main_canvas.scale))

    def blit_to_main(self):
        dest = self.main_canvas
        dest.blit(pygame.transform.smoothscale_by(self.surface, self.main_canvas.relative_scale), self.pos)


