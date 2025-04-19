import gamebase as gb
import pygame
from pygame import Vector2
import math
from pathlib import Path
from random import random, uniform, randint, choice, choices
from player import Cart
from states import Intro, Running
from bindings import *
from game_draw import draw, simulate

class CartPoleGame(gb.BaseScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.game_duration = 45
        self.info_popup.visible = False

        self.rel_path = Path(__file__).parent
        self.assets_path = self.rel_path / 'assets'

        self.mouse.left.press_callback = self.left_click
        self.mouse.left.release_callback = self.left_release
        self.mouse.right.press_callback = self.right_click
        self.mouse.right.release_callback = self.right_release
        self.mouse.scroll.up_callback = self.scroll_up
        self.mouse.scroll.down_callback = self.scroll_down

        self.fonts['reward'] = pygame.font.SysFont('Comic Sans MS', 22)
        self.sounds['coin'] = self.load_sound(self.assets_path / 'coin.wav', volume=0.1)
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
        self.inputs: dict[str, gb.BaseInput] = {
            'p1': gb.Joystick(joystick, 2, dead_zone=0.03) if joystick is not None else gb.LinearController(),
            'p2': gb.LinearController(),
            'none_p1': gb.NoneInput(),
            'none_p2': gb.NoneInput(),
        }

        self.canvases['main'] = gb.Canvas(self.canvas_size, fonts=self.fonts, draw_fun=self.state_draw)
        self.event_loop_callback = self.handle_user_input_event

        self.cols['focus'] = (255, 255, 0)
        self.cols['scope'] = (55, 255, 200)
        self.cols['fps'] = gb.lerp_vec3(self.cols['info'], (0, 0, 0), 0.6)
        self.cols['p1'] = (90, 140, 190)
        self.cols['p2'] = (190, 90, 140)
        self.cols['tiny_collect'] = (235, 230, 180)
        self.cols['small_collect'] = (220, 200, 60)
        self.cols['big_collect'] = (200, 140, 240)
        self.cols['huge_collect'] = (200, 90, 255)
        self.cols['timer'] = (90, 60, 50)

        self.fps_popup = gb.PopUpText(self.active_canvas, alpha=255,
                                      pos=(self.active_canvas.xmin + 0.01, self.active_canvas.ymax - .04),
                                      color=self.cols['fps'], text='', font=self.fonts['medium'], visible=True,
                                      border_width=-1, fill_color=(0, 0, 0, 0))

        self.scopes = {
            'p1': gb.Scope(self.active_canvas, name='p1 states', legend=('th', 'x', 'vel', 'w'), fps=self.clock.fps,
                           alpha=200,
                           color=self.cols['p1'], y_scale=(0.25, 0.25, .25, .25), focus_color=self.cols['focus'],
                           pos=(-1.75, 0.8), size=(320, 180), maxlen=400, visible=False),
            'p2': gb.Scope(self.active_canvas, name='p2 states', legend=('th', 'x', 'vel', 'w'), fps=self.clock.fps,
                           alpha=200,
                           color=self.cols['p2'], y_scale=(0.25, 0.25, .25, .25), focus_color=self.cols['focus'],
                           pos=(-1.75, -0.01), size=(320, 180), maxlen=400, visible=False),
            'inputs': gb.Scope(self.active_canvas, name='inputs', legend=('p1', 'p2'), fps=self.clock.fps, alpha=200,
                               color=self.cols['info'], y_scale=(0.8, 0.8), focus_color=self.cols['focus'],
                               pos=(-1.1, -0.65), size=(320, 180), maxlen=400, visible=False),
            'times': gb.Scope(self.active_canvas, name='frame time', legend=('active', 'total'), fps=self.clock.fps,
                              alpha=200,
                              color=self.cols['info'], focus_color=self.cols['focus'], pos=(-1.75, -0.65),
                              size=(320, 180),
                              maxlen=400, visible=True),
        }
        self.paused = False
        self.players = None
        self.chash_xoffset = None
        self.perturbation = 0.0

        self.stress_test_particles = gb.Particles(1200)
        self.stress_test_en = False

        self.extra_help = [
            f'────────────────────────',
            f'ESC: reset',
            f' F7: toggle stress test',
            f'  1: toggle player 1 en',
            f'  2: toggle player 2 en',
            f'  .: perturb clockwise',
            f'  ,: perturb anticlock',
            f'  s: enable scopes',
            f'm_r: disable scope',
        ]

        self.state = None
        self.previous_state_screenshot = None
        self.reset()

    def reset(self):
        self.clock.reset()
        th0 = uniform(-1, 1) * 0.0
        self.players = {
            'p1': Cart('P1', self, self.inputs['p1'], Vector2(-0.8, 0.35), base_color=self.cols['p1'],
                       rail_color=(90, 90, 90), th0=th0, death_callback=self.death),
            'p2': Cart('P2', self, self.inputs['p2'], Vector2(-0.8, -0.45), base_color=self.cols['p2'],
                       rail_color=(90, 90, 90), th0=th0, death_callback=self.death),
        }

        self.chash_xoffset = 0.0
        self.paused = False
        for scope in self.scopes.values():
            scope.clear()
        for player in self.players.values():
            player.reset()
        for input_ in self.inputs.values():
            input_.reset()

        # self.previous_state_screenshot = None
        self.state = Running(self)

    def left_release(self, button: gb.MouseButton):
        pass

    def left_click(self, button: gb.MouseButton):
        pass

    def right_click(self, button: gb.MouseButton):
        pass

    def right_release(self, button: gb.MouseButton):
        for scope in self.scopes.values():
            if scope.collision(self.mouse_world_pos):
                scope.visible = False

    def scroll_up(self, scroll: gb.MouseScroll):
        pass

    def scroll_down(self, scroll: gb.MouseScroll):
        pass

    def perturb(self, intensity):
        for player in self.players.values():
            player.perturb(intensity)
            self.perturbation = intensity

    def state_draw(self, canvas: gb.Canvas):
        pygame.display.set_caption(str(self.state))
        self.state.update()
        self.state.draw(canvas)

    def stress_test(self):
        if self.stress_test_en:
            letters = [chr(i) for i in range(945, 970) if i != 962]
            for _ in range(10):
                font_index = randint(0, len(self.particles_fonts)-1)
                self.stress_test_particles.append(
                    gb.TextParticle(self.active_canvas,
                                    color=gb.lerp_vec3((90, 250, 90), (30, 90, 30), random()),
                                    text=choice(letters),
                                    font=self.particles_fonts[font_index],
                                    pos=(uniform(-1.8, 1.8), 1.05),
                                    vel=(0, -0.8 - font_index * .2), dt=1 / self.fps, g=0, lifetime=-1,
                                    ))
            self.stress_test_particles.step_and_draw()

    def death(self, player):
        self.sounds['crash'].play()
        self.chash_xoffset = player.v * 500

    def handle_user_input_event(self, event):
        self.state.handle_event(event)
        if self.mouse.right.dragging and self.mouse.right.drag_keys[pygame.K_LCTRL]:
            self.active_canvas.bias = (int(self.active_canvas.bias[0] + self.mouse.right.drag_delta[0]),
                                       int(self.active_canvas.bias[1] + self.mouse.right.drag_delta[1]))
            self.mouse.right.clear_drag_delta()

        for scope in self.scopes.values():
            if self.mouse.left.dragging and scope.focus:
                canvas = self.active_canvas
                delta = canvas.screen_to_world_delta_v2(gb.remap(self.mouse.left.drag_delta, self.window, canvas))
                # print(self.mouse.left.drag_delta, '->', remap(self.mouse.left.drag_delta, self.window, canvas), '->', canvas.screen_to_world_delta_v2(remap(self.mouse.left.drag_delta, self.window, canvas)))
                scope.pos = Vector2(scope.pos) + delta
                self.mouse.left.clear_drag_delta()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.reset()
            elif event.key == pygame.K_s:
                for scope in self.scopes.values():
                    scope.visible = True
            # elif event.key == pygame.K_UP:
            #     self.players['p1'].alive = not self.players['p1'].alive
            # elif event.key == pygame.K_DOWN:
            #     self.players['p2'].alive = not self.players['p2'].alive

            elif event.key == pygame.K_2:
                self.inputs['p2'], self.inputs['none_p2'] = self.inputs['none_p2'], self.inputs['p2']
                self.reset()

            elif event.key == pygame.K_1:
                self.inputs['p1'], self.inputs['none_p1'] = self.inputs['none_p1'], self.inputs['p1']
                self.reset()

            elif event.key == pygame.K_F7:
                self.stress_test_en = not self.stress_test_en
                if self.stress_test_en:
                    if 'particles_fonts' not in self.__dict__:
                        self.particles_fonts = [
                            pygame.font.SysFont('Times', 22),
                            pygame.font.SysFont('Times', 36),
                            pygame.font.SysFont('Times', 54),
                            pygame.font.SysFont('Times', 68),
                    ]
                elif 'particles_fonts' in self.__dict__:
                    del self.particles_fonts


            elif event.key == pygame.K_COMMA:
                self.perturb(0.4)
            elif event.key == pygame.K_PERIOD:
                self.perturb(-0.4)

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
