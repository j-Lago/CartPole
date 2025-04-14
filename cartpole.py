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


class Game(BaseScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rel_path = Path(__file__).parent
        self.assets_path = self.rel_path / 'assets'

        self.sounds['jet'] = self.load_sound(self.assets_path / 'jet.wav', volume=0.0)
        self.sounds['jet'].play(loops=-1)
        # self.images['jet'] = pygame.transform.smoothscale_by(self.load_image(self.assets_path / 'jet.png'), (0.35, 0.3))

        self.force_factor = 18
        joystick = None
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()

        self.input = Joystick(joystick, 2, normalization=lambda x: x)



        self.canvases['main'] = Canvas(self.canvas_size, fonts=self.fonts, draw_fun=self.draw_main)
        self.pre_draw_callback = self.simulate

        self.cols['focus'] = (255, 255, 0)
        self.cols['scope'] = (55, 255, 200)
        self.scopes = {
            'errs': Scope(self.active_canvas, name='position', legend=('th', 'x'), fps=self.fps, alpha=200, color=self.cols['scope'], y_scale=(0.25, 0.25), focus_color=self.cols['focus'], pos=(0.9, 0.5), size=(400, 250), maxlen=400),
            'inputs': Scope(self.active_canvas, name='inputs', legend=('input'), fps=self.fps, alpha=200, color=self.cols['scope'], y_scale=(0.8, ), focus_color=self.cols['focus'], pos=(0.9,0.0), size=(400, 250), maxlen=400),
            'times': Scope(self.active_canvas, name='frame time', legend=('active', 'total'), fps=self.fps, alpha=200, color=self.cols['scope'], focus_color=self.cols['focus'], pos=(0.9, -0.5), size=(400, 250), maxlen=400),
        }

        self.players = {
            'p1': Cart(self, Vector2(0.2, 0.35)),
            'p2': Cart(self, Vector2(-0.2, -0.35)),
        }






    def simulate(self):
        joystick_input = self.input.update()

        for player in self.players.values():
            player.step(joystick_input * self.force_factor)
        self.sounds['jet'].set_volume(math.fabs(joystick_input))

    def draw_main(self, canvas: Canvas):
        pos = self.mouse_world_pos
        for player in self.players.values():
            player.draw(self.t)

        #scope
        x = self.t
        total_frame_time = 1 / self.real_fps if self.real_fps != 0 else 0
        y = {
            'errs': (0, 0), #(self.players[0].theta - math.pi, self.players[0].x),
            'inputs': (self.input.value, ),
            'times': (self.last_active_frame_time * self.fps - 1, total_frame_time * self.fps - 1),
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
    assets_path = Path(__file__).parent / 'assets'
    jet_img = pygame.transform.smoothscale_by(pygame.image.load(assets_path / 'jet.png'), (0.35, 0.3))

    def __init__(self, game: BaseScreen, pos: Vector2 = Vector2(0, 0)):

        self.game = game
        self.canvas = self.game.active_canvas
        self.fps = self.game.fps
        self.input = self.game.input

        if not isinstance(pos, Vector2):
            pos = Vector2(pos)

        self.initial_pos = pos
        self.linear_factor = 0.110625

        self.model = Pendulo(1., .3, 5., 1., 1., x0=self.initial_pos[0]/self.linear_factor, th0=0.658, dt=1 / self.fps)



        self.cols = {
            'cart': (200, 180, 60),
            'pole': (240, 240, 120),
            'pivot': (200, 180, 60),
            'wheels': (240, 240, 120),
            'ground': (120, 90, 60),
            'target_x': (120, 90, 60),
        }

        self.points = {
            'pole': ((-0.02, 0), (0.02, 0), (0.02, -0.5), (-0.02, -0.5))
        }

        self.base_rect = fRect(0, 0, 0.4, 0.08)

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

        flame_gain = math.fabs(self.input.value) * uniform(0.8, 1.2)
        img0: pygame.Surface = pygame.transform.scale_by(self.jet_img, Vector2(flame_gain, max(flame_gain, 0.7)) * self.canvas.relative_scale)
        if self.input.value < 0:
            img0 = pygame.transform.flip(img0, True, False)

        img = Image(self.canvas, img0)
        flame_offset = self.base_rect[2]/2*0.9, self.base_rect[3]/2
        if self.input.value > 0:
            img.midright = self.pos - flame_offset
        else:
            img.midleft = self.pos + (flame_offset[0], -flame_offset[1])
        img.blit()

        cart_center = self.pos
        self.base_rect.midtop = cart_center

        pole_points = RotateMatrix(self.theta) * self.points['pole']
        pole_points = tuple((cart_center[0]+p[0], cart_center[1]+p[1]) for p in pole_points)

        wheel_r = 0.05

        wheel_yaxis = self.base_rect[3]*1.1
        self.canvas.draw_rect(self.cols['cart'], self.base_rect)

        for wheel_center in  ( (cart_center - (self.base_rect[2] / 2 * 0.65, wheel_yaxis)), (cart_center - (-self.base_rect[2] / 2 * 0.65, wheel_yaxis))):
            self.canvas.draw_circle(self.cols['wheels'], wheel_center, wheel_r, 10)
            self.canvas.draw_circle(self.cols['wheels'], wheel_center, wheel_r*.3, 10)
            spoke = Vector2(0.0, wheel_r*.9)
            n_spokes = 5
            for i in range(n_spokes):
                ang = -self.x / wheel_r
                self.canvas.draw_line(self.cols['wheels'], wheel_center, wheel_center + spoke.rotate_rad(i*2*math.pi/n_spokes+ang), 6)
            self.canvas.draw_circle(self.cols['cart'], wheel_center, wheel_r * .15, 10)


        self.canvas.draw_circle(self.cols['pivot'], cart_center, 0.04)

        y = self.pos[1] - wheel_r - wheel_yaxis
        ground_width = 4
        self.canvas.draw_line(self.cols['ground'], (self.canvas.xmin, y), (self.canvas.xmax, y), ground_width)
        self.canvas.draw_line(self.cols['target_x'], (-0.3, y-0.02), (-0.3, y), ground_width)
        self.canvas.draw_line(self.cols['target_x'], (0.3, y - 0.02), (0.3, y), ground_width)

        self.canvas.draw_polygon(self.cols['pole'], pole_points)
        self.canvas.draw_circle(self.cols['pole'], cart_center, 0.02)



if __name__ == '__main__':
    Game()
