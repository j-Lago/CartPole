from pygame import Vector2
from basescreen import BaseScreen
from canvas import Canvas, remap
from utils import fRect, Mat2x2, RotateMatrix
from pendulo import Pendulo
from random import uniform
import math
import pygame
from inputs import Joystick, JOYBUTTON, LinearControl
from scope import Scope
from pathlib import Path
from image import Image
from lerp import lerp_vec3
from typing import Callable
from random import random
from popup import PopUpText


class Game(BaseScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.info_popup.visible = False

        self.rel_path = Path(__file__).parent
        self.assets_path = self.rel_path / 'assets'

        self.sounds['crash'] = self.load_sound(self.assets_path / 'crash.wav', volume=1.0)
        self.sounds['jet'] = self.load_sound(self.assets_path / 'jet.wav', volume=0.0)
        self.sounds['jet'].play(loops=-1)
        # self.images['jet'] = pygame.transform.smoothscale_by(self.load_image(self.assets_path / 'jet.png'), (0.35, 0.3))

        self.force_factor = 18
        joystick = None
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()

        # self.input = Joystick(joystick, 2, normalization=lambda x: x)
        self.input = LinearControl()


        self.canvases['main'] = Canvas(self.canvas_size, fonts=self.fonts, draw_fun=self.draw_main)
        self.pre_draw_callback = self.simulate
        self.event_loop_callback = self.process_user_input_event

        self.cols['focus'] = (255, 255, 0)
        self.cols['scope'] = (55, 255, 200)
        self.cols['fps'] = lerp_vec3(self.cols['info'], (0,0,0), 0.6)

        self.fps_popup = PopUpText(self.active_canvas, alpha=255, pos=(self.active_canvas.xmin+0.01, self.active_canvas.ymin+.1),
                                    color=self.cols['fps'], text='', font=self.fonts['small'], visible=True, border_width=-1, fill_color=(0,0,0,0))

        self.scopes = None
        self.players = None
        self.chash_xoffset = None

        self.reset()

    def reset(self):
        self.ticks = 0
        self.scopes = {
            'errs': Scope(self.active_canvas, name='states', legend=('th', 'x', 'vel', 'w'), fps=self.fps, alpha=200, color=self.cols['scope'], y_scale=(0.25, 0.25, .25, .25), focus_color=self.cols['focus'], pos=(0.9, 0.5), size=(320, 180), maxlen=400),
            'inputs': Scope(self.active_canvas, name='inputs', legend=('p1', 'p2'), fps=self.fps, alpha=200, color=self.cols['scope'], y_scale=(0.8, 0.8), focus_color=self.cols['focus'], pos=(0.9, 0.0), size=(320, 180), maxlen=400),
            'times': Scope(self.active_canvas, name='frame time', legend=('active', 'total'), fps=self.fps, alpha=200, color=self.cols['scope'], focus_color=self.cols['focus'], pos=(0.9, -0.5), size=(320, 180), maxlen=400),
        }

        th0 = uniform(-1, 1) * 0.0
        self.players = {
            'p1': Cart(self, Vector2(0.2, 0.35), base_color=(30, 180, 220), rail_color=(90, 90, 90), th0=th0, death_callback=self.death),
            'p2': Cart(self, Vector2(-0.2, -0.35), base_color=(180, 90, 220), rail_color=(90, 90, 90), th0=th0, death_callback=self.death),
        }

        self.chash_xoffset = 0.0




    def simulate(self):
        joystick_input = self.input.update(self.players['p1'])

        all_dead = True
        for player in self.players.values():
            all_dead = all_dead and not player.alive

        if all_dead:
            joystick_input = 0.0

        d = random() * self.chash_xoffset * 0.2
        self.chash_xoffset -= d
        # if abs(self.chash_xoffset) < .1:
        #     self.chash_xoffset = 0

        shake_intensity = 1.3
        self.blit_offset = uniform(-shake_intensity, shake_intensity) * joystick_input * shake_intensity + d, uniform(
            -shake_intensity, shake_intensity) * joystick_input * shake_intensity * (1+abs(d)*.3)



        for player in self.players.values():
            player.step(joystick_input * self.force_factor)
        self.sounds['jet'].set_volume(math.fabs(joystick_input))


    def draw_main(self, canvas: Canvas):
        canvas.fill(self.cols['bg'])
        pos = self.mouse_world_pos

        # desenha os mortos por traz
        for player in self.players.values():
            if not player.alive:
                player.draw(self.t)
        for player in self.players.values():
            if player.alive:
                player.draw(self.t)





        #scope
        x = self.t
        total_frame_time = 1 / self.real_fps if self.real_fps != 0 else 0
        y = {
            'errs': (self.players['p1'].theta - math.pi, self.players['p1'].x, self.players['p1'].v, self.players['p1'].omega),
            'inputs': (self.input.value, 0.0),
            'times': (self.last_active_frame_time * self.fps - 1, total_frame_time * self.fps - 1),
        }

        # fps
        self.fps_popup.text = (f'fps: {self.real_fps:.1f} ({self.mm_frame_time.value * self.fps * 100.0:.1f}%)', )
        self.fps_popup.draw()
        canvas.blit(self.fps_popup, self.fps_popup.pos)

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

    def death(self, player):
        self.sounds['crash'].play()
        self.chash_xoffset = player.v * 500

    def process_user_input_event(self, event):
        if self.mouse.right.dragging and self.mouse.right.drag_keys[pygame.K_LCTRL]:
            self.active_canvas.bias = (int(self.active_canvas.bias[0] + self.mouse.right.drag_delta[0]), int(self.active_canvas.bias[1] + self.mouse.right.drag_delta[1]))
            self.mouse.right.clear_drag_delta()

        for scope in self.scopes.values():
            if self.mouse.left.dragging and scope.focus:
                canvas = self.active_canvas
                delta = canvas.screen_to_world_delta_v2(remap(self.mouse.left.drag_delta, self.window, canvas))
                # print(self.mouse.left.drag_delta, '->', remap(self.mouse.left.drag_delta, self.window, canvas), '->', canvas.screen_to_world_delta_v2(remap(self.mouse.left.drag_delta, self.window, canvas)))
                scope.pos = Vector2(scope.pos) + delta
                self.mouse.left.clear_drag_delta()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.reset()
            elif event.key == pygame.K_UP:
                self.players['p1'].alive = not self.players['p1'].alive
            elif event.key == pygame.K_DOWN:
                self.players['p2'].alive = not self.players['p2'].alive

            # elif event.key == pygame.K_r:
            #     self.scopes['ch1'].clear()
            #     self.scopes['ch1'].rolling = not self.scopes['ch1'].rolling
            # elif event.key == pygame.K_v:
            #     self.scopes['ch1'].visible = not self.scopes['ch1'].visible
            # elif event.key == pygame.K_KP_MULTIPLY:
            #     self.scopes['ch1'].x_scale *= 2
            # elif event.key == pygame.K_KP_DIVIDE:
            #     self.scopes['ch1'].x_scale /= 2
            #
            # elif event.key == pygame.K_t:
            #     self.scopes['ch2'].clear()
            #     self.scopes['ch2'].rolling = not self.scopes['ch2'].rolling
            # elif event.key == pygame.K_b:
            #     self.scopes['ch2'].visible = not self.scopes['ch2'].visible
            # elif event.key == pygame.K_KP_PLUS:
            #     self.scopes['ch2'].x_scale *= 2
            # elif event.key == pygame.K_KP_MINUS:
            #     self.scopes['ch2'].x_scale /= 2



class Cart:
    assets_path = Path(__file__).parent / 'assets'
    jet_img = pygame.transform.smoothscale_by(pygame.image.load(assets_path / 'jet.png'), (0.35, 0.3))

    def __init__(self, game: BaseScreen, pos: Vector2 = Vector2(0, 0), th0: float = 0, base_color: tuple[int, int, int] = (180, 180, 180), rail_color: tuple[int, int, int] = (255, 255, 255), alive: bool=True, death_callback: Callable = None):

        self.death_callback = death_callback
        self.game = game
        self.alive = alive
        self.canvas = self.game.active_canvas
        self.input = self.game.input
        self.x_target = (-0.25, 0.25)
        tol = math.pi/6
        self.th_target = (math.pi - tol, math.pi + tol)

        if not isinstance(pos, Vector2):
            pos = Vector2(pos)

        self.initial_pos = pos
        self.linear_factor = 0.110625

        self.model = Pendulo(1., .3, 5., 1., 1., x0=self.initial_pos[0]/self.linear_factor, th0=th0, dt=1 / self.fps)


        self.base_color = base_color
        self.rail_col = rail_color
        self.sleeper_col = (120, 100, 60)
        self.guardrail0_col = (60, 60, 60)
        self.guardrail1_col = (220, 200, 30)


        self.points = {
            'pole': ((0.015, 0), (0.015, -0.4), (-0.015, -0.4), (-0.015, 0))
        }

        self.base_rect = fRect(0, 0, 0.35, 0.08)
        self.guardrail_rect = fRect(0, 0, 0.09, 0.18)


    @property
    def ticks(self):
        return self.game.ticks

    @property
    def fps(self):
        return self.game.fps


    def step(self, force):
        if self.alive:
            if self.x - self.base_rect.w / 2 < self.canvas.xmin + self.guardrail_rect.w or self.x + self.base_rect.w / 2 > self.canvas.xmax - self.guardrail_rect.w:
                self.alive = False
                if self.death_callback is not None:
                    self.death_callback(self)
            else:
                self.model.step(force)

    @property
    def theta(self):
        return self.model.theta

    @property
    def omega(self):
        return self.model.omega

    @property
    def x(self):
        return self.model.x * self.linear_factor


    @property
    def v(self):
        return self.model.v * self.linear_factor

    @property
    def pos(self):
        return Vector2(self.x, self.initial_pos[1])

    def draw(self, t):

        pole_col = self.base_color
        cart_col = lerp_vec3(self.base_color, (0, 0, 0), 0.4)

        if not self.alive:
            pole_col = lerp_vec3(pole_col, (0, 0, 0), 0.7)
            cart_col = lerp_vec3(cart_col, (0, 0, 0), 0.7)

        col1 = (255, 255, 0)
        col2 = (127, 127, 127)

        # flame
        if self.alive:
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


        wheel_r = 0.055
        wheel_yaxis = self.base_rect[3] * 1.1
        wheel_xaxis = self.base_rect[2] / 2 * 0.6
        y = self.pos[1] - wheel_r - wheel_yaxis

        # flags
        for x in (self.x_target[0]-self.base_rect.w/2, self.x_target[1]+self.base_rect.w/2):
            self.canvas.draw_line((60,60,60), (x, y), (x, y + 0.2), 5)

        # cart
        self.canvas.draw_rect(cart_col, self.base_rect)

        # wheels
        for m, wheel_center in enumerate(( (cart_center - (wheel_xaxis, wheel_yaxis)), (cart_center - (-wheel_xaxis, wheel_yaxis)))):
            self.canvas.draw_circle(pole_col, wheel_center, wheel_r, 10)
            self.canvas.draw_circle(pole_col, wheel_center, wheel_r*.3, 10)
            spoke = Vector2(0.0, wheel_r*.9)
            n_spokes = 5
            for n in range(n_spokes):
                ang = -self.x / wheel_r
                self.canvas.draw_line(pole_col, wheel_center, wheel_center + spoke.rotate_rad(n*2*math.pi/n_spokes+ang + m*0.554) , 6)
            self.canvas.draw_circle(cart_col, wheel_center, wheel_r * .15, 10)

        # cart-pole axis
        self.canvas.draw_circle(cart_col, cart_center, 0.04)

        # rail
        rail_sleeper_rect = fRect(0, 0, 0.03, 0.02)
        n_sleepers = 22
        mw = self.canvas.get_rect()[2] / (n_sleepers-1)
        for i in range(n_sleepers):
            x = self.canvas.xmin + i * mw
            rail_sleeper_rect.midtop = (x, y)
            self.canvas.draw_rect(self.sleeper_col, rail_sleeper_rect)
        ground_width = 4
        self.canvas.draw_line(self.rail_col, (self.canvas.xmin, y), (self.canvas.xmax, y), ground_width)

        # for x in self.x_target:
        #     self.canvas.draw_line(col1, (x, y-0.03), (x, y-0.05), ground_width)


        # pole
        self.canvas.draw_polygon(pole_col, pole_points)
        self.canvas.draw_circle(pole_col, cart_center, 0.02)
        self.canvas.draw_circle(cart_col, cart_center, 0.01)

        # guardrail
        g_rect = self.guardrail_rect
        fx = 2/3
        fy = 1/3

        g_rect.bottomleft = (self.canvas.xmin, y)
        ti_points = (g_rect.x, g_rect.y - g_rect.h), (g_rect.x, g_rect.y + fy * g_rect.h - g_rect.h), (g_rect.x + fx * g_rect.w, g_rect.y - g_rect.h)
        ts_points = (g_rect.x + g_rect.w, g_rect.y), (g_rect.x + g_rect.w, g_rect.y - fy * g_rect.h), (g_rect.x + g_rect.w - fx * g_rect.w, g_rect.y)
        tc_points = (g_rect.x, g_rect.y - g_rect.h + 1.75*fy * g_rect.h), (g_rect.x, g_rect.y - g_rect.h + 2.75*fy * g_rect.h), (g_rect.x + g_rect.w, g_rect.y - g_rect.h + 1.25 * fy * g_rect.h), (g_rect.x + g_rect.w, g_rect.y - g_rect.h + 0.25 * fy * g_rect.h)
        self.canvas.draw_polygon(self.guardrail0_col, g_rect.points)
        self.canvas.draw_polygon(self.guardrail1_col, ti_points)
        self.canvas.draw_polygon(self.guardrail1_col, ts_points)
        self.canvas.draw_polygon(self.guardrail1_col, tc_points)

        g_rect.bottomright = (self.canvas.xmax, y)
        ti_points = (g_rect.x, g_rect.y - g_rect.h), (g_rect.x, g_rect.y + fy * g_rect.h - g_rect.h), (g_rect.x + fx * g_rect.w, g_rect.y - g_rect.h)
        ts_points = (g_rect.x + g_rect.w, g_rect.y), (g_rect.x + g_rect.w, g_rect.y - fy * g_rect.h), (g_rect.x + g_rect.w - fx * g_rect.w, g_rect.y)
        tc_points = (g_rect.x, g_rect.y - g_rect.h + 1.75 * fy * g_rect.h), (g_rect.x, g_rect.y - g_rect.h + 2.75 * fy * g_rect.h), (g_rect.x + g_rect.w, g_rect.y - g_rect.h + 1.25 * fy * g_rect.h), (g_rect.x + g_rect.w, g_rect.y - g_rect.h + 0.25 * fy * g_rect.h)
        self.canvas.draw_polygon(self.guardrail0_col, g_rect.points)
        self.canvas.draw_polygon(self.guardrail1_col, ti_points)
        self.canvas.draw_polygon(self.guardrail1_col, ts_points)
        self.canvas.draw_polygon(self.guardrail1_col, tc_points)


        if self.alive and self.th_target[0] < self.theta < self.th_target[1]:
            for start, end in zip(pole_points, pole_points[1:]):
                self.canvas.draw_sparkly_line(start_pos=start, end_pos=end, width=10, density=200, mu=0.5, sigma=1, color1=col1, color2=col2, particle_size=(1, 2))
            if self.x_target[0] < self.x < self.x_target[1]:
                cart_points = self.base_rect.points
                for start, end in zip(cart_points, cart_points[1:] + (cart_points[0],)):
                    self.canvas.draw_sparkly_line(start_pos=start, end_pos=end, width=10, density=200, mu=0.5, sigma=1, color1=col1, color2=col2, particle_size=(1, 2))







if __name__ == '__main__':
    Game()
