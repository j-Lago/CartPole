from pygame import Vector2
from basescreen import BaseScreen
from canvas import Canvas
from utils import fRect, Mat2x2, RotateMatrix
from pendulo import Pendulo
from random import uniform
import math
import pygame
from inputs import Joystick, JOYBUTTON
from scope import Scope
from pathlib import Path
from image import Image

class CartPoleGame(BaseScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rel_path = Path(__file__).parent
        self.assets_path = self.rel_path / 'assets'

        self.canvases['main'] = Canvas(self.canvas_size, fonts=self.fonts, draw_fun=self.draw_main)
        self.mouse.set_visible(True)

        self.cols['focus'] = (255, 255, 0)
        self.cols['scope'] = (55, 255, 200)
        self.scopes = {
            'ch1': Scope(self.active_canvas, name='position', legend=('th', 'x'), fps=self.fps,
                         alpha=200, color=self.cols['scope'], y_scale=(0.25, 0.25), focus_color=self.cols['focus'], pos=(0.9, 0.4),
                         size=(400, 250), maxlen=400),
            'ch2': Scope(self.active_canvas, name='inputs', legend=('input'), fps=self.fps, alpha=200,
                         color=self.cols['scope'], y_scale=(0.8, ), focus_color=self.cols['focus'],
                         pos=(0.9, -0.1), size=(400, 250), maxlen=400),
        }

        self.player = Cart(self.active_canvas, self.fps)

        self.force_factor = 18
        self.input = None
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            self.input = Joystick(joystick, 2, normalization=lambda x: x)

        self.sounds['beep'] = self.load_sound(self.assets_path / 'beep.wav', volume=0.6)
        self.sounds['jet'] = self.load_sound(self.assets_path / 'jet.wav', volume=0.0)
        self.sounds['jet'].play(loops=-1)

        self.images['jet'] = pygame.transform.smoothscale_by(self.load_image(self.assets_path / 'jet.png'), (0.35, 0.3))




    def draw_main(self, canvas: Canvas):
        pos = self.mouse_world_pos


        self.input.update()

        self.player.step(self.input.value * self.force_factor)

        self.sounds['jet'].set_volume(math.fabs(self.input.value))

        flame_gain = math.fabs(self.input.value) * uniform(0.8, 1.2)
        img0: pygame.Surface = pygame.transform.scale_by(self.images['jet'], Vector2(flame_gain, max(flame_gain, 0.7)) * canvas.relative_scale)
        if self.input.value < 0:
            img0 = pygame.transform.flip(img0, True, False)

        img = Image(canvas, img0)
        cart_r = 0.19
        if self.input.value > 0:
            img.midright = self.player.pos - (cart_r, 0)
        else:
            img.midleft = self.player.pos + (cart_r, 0)
        img.blit()



        self.player.draw(self.t)

        #scope
        x = self.t
        total_frame_time = 1 / self.real_fps if self.real_fps != 0 else 0
        y = {
            'ch1': (self.player.theta - math.pi, self.player.x),
            # (self.mm_frame_time.value * self.fps - 1, self.last_active_frame_time * self.fps - 1),
            'ch2': (self.input.value, ),
        }

        def another_in_focus(self_key):
            for ikey, iscope in self.scopes.items():
                if ikey != self_key and iscope.focus:
                    return True
            return False

        for key, scope in self.scopes.items():
            scope.append(x, y[key])
            scope.focus = scope.collision(self.mouse_world_pos) and not another_in_focus(key)
            scope.draw()
            scope.blit_to_main()



class Cart:
    def __init__(self, canvas: Canvas, fps: float, pos: Vector2 = Vector2(0, 0)):
        self.canvas = canvas
        if not isinstance(pos, Vector2):
            pos = Vector2(pos)

        self.initial_pos = pos
        self.fps = fps
        self.linear_factor = 0.110625

        self.model = Pendulo(1., .3, 5., 1., 1., x0=self.initial_pos[0], th0=0.658, dt=1 / self.fps)


        self.cols = {
            'cart': (240, 220, 60),
            'pole': (200, 180, 30),
            'pivot': (60, 180, 60),
        }

        self.points = {
            'pole': ((-0.02, 0), (0.02, 0), (0.02, -0.6), (-0.02, -0.6))
        }

        self.base_rect = fRect(0, 0, 0.4, 0.06)

    def step(self, force):
        self.model.step(force)

    @property
    def theta(self):
        return self.model.theta

    @property
    def x(self):
        return self.model.x*self.linear_factor

    @property
    def pos(self):
        return Vector2(self.x, self.initial_pos[1])

    def draw(self, t):

        cart_center = self.pos

        self.base_rect.center = cart_center
        self.canvas.draw_rect(self.cols['cart'], self.base_rect)


        points = RotateMatrix(self.theta) * self.points['pole']
        points = tuple((cart_center[0]+p[0], cart_center[1]+p[1]) for p in points)

        self.canvas.draw_polygon(self.cols['pole'], points)
        self.canvas.draw_circle(self.cols['pivot'], cart_center, 0.02)


if __name__ == '__main__':
    CartPoleGame()
