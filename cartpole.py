from pygame import Vector2
from basescreen import BaseScreen
from canvas import Canvas
from utils import fRect, Mat2x2, RotateMatrix


class CartPoleGame(BaseScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvases['main'] = Canvas(self.canvas_size, fonts=self.fonts, draw_fun=self.draw_main)
        self.mouse.set_visible(False)

        self.player = Cart(self.active_canvas)

    def draw_main(self, canvas: Canvas):
        pos = self.mouse_world_pos

        self.player.pos = pos[0], 0
        self.player.draw(self.t)



class Cart:
    def __init__(self, canvas: Canvas, pos: Vector2 = Vector2(0, 0)):
        self.canvas = canvas
        if not isinstance(pos, Vector2):
            pos = Vector2(pos)
        self.pos = pos
        self.angle = 0.5

        self.cols = {
            'cart': (240, 220, 60),
            'pole': (200, 180, 30),
            'pivot': (60, 180, 60),
        }

        self.points = {
            'pole': ((-0.02, 0), (0.02, 0), (0.02, 0.6), (-0.02, 0.6))
        }

    def draw(self, t):
        base_rect = fRect(0, 0, 0.4, 0.06)
        base_rect.center = self.pos
        self.canvas.draw_rect(self.cols['cart'], base_rect)


        points = RotateMatrix(t) * self.points['pole']
        points = tuple((self.pos[0]+p[0], self.pos[1]+p[1]) for p in points)

        self.canvas.draw_polygon(self.cols['pole'], points)
        self.canvas.draw_circle(self.cols['pivot'], self.pos, 0.02)


if __name__ == '__main__':
    CartPoleGame()
