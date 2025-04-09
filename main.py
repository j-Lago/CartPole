import pygame
from datetime import datetime
from canvas import Canvas
from inputs import Joystick, JOYBUTTON
import math
from canvas import rotate_vec2s
from random import random, randint, uniform, choice
from particles import BallParticle, Particles, TextParticle
from pygame import Vector2
from lerp import lerp, lerp_vec2, lerp_vec3
from basescreen import BaseScreen
from mouse import MouseButton, MouseScroll, Mouse
from popup import PopUp
import numpy as np
from _collections import deque
from itertools import islice
from utils import remap, ColorsDiscIterator
from scope import Scope


class Example(BaseScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mouse.left.press_callback = self.left_click
        self.mouse.left.release_callback = self.left_release
        self.mouse.right.press_callback = self.right_click
        self.mouse.right.release_callback = self.right_release
        self.mouse.scroll.up_callback = self.scroll_up
        self.mouse.scroll.down_callback = self.scroll_down

        self.tabs = {
            'rocket': Canvas(self.canvas_size, pygame.SRCALPHA, bg_color=(15, 15, 15), draw_fun=self.draw_rocket, shortcut=pygame.K_F1),
            'test'  : Canvas(self.canvas_size, pygame.SRCALPHA, bg_color=(30, 45, 30), draw_fun =self.draw_main, shortcut=pygame.K_F2),
            'menu'  : Canvas(self.canvas_size, pygame.SRCALPHA, bg_color=(15, 15, 15), draw_fun=self.draw_menu, shortcut=pygame.K_F3)
        }
        self.active_tab = 'rocket'
        self.last_active_tab = self.active_tab
        self.event_loop_callback = self.process_user_input_event
        self.tabs['rocket'].got_focus_callback = self.rocket_got_focus_callback

        focus_color = (255, 255, 0)
        self.scopes = {
            'ch1': Scope(self.tabs['rocket'], name='ch1', fps=self.fps, alpha=200, color=(55, 255, 200), focus_color=focus_color, pos=(0.5, 0.5), size=(500, 300), flags=pygame.SRCALPHA, maxlen=400),
            'ch2': Scope(self.tabs['rocket'], name='ch2', fps=self.fps, alpha=200, color=(55, 255, 200), line_colors=((255,128,128),(128,128,255)), y_scale=(0.9, 1.7), focus_color=focus_color, pos=(0.5, -0.1), size=(500, 300), flags=pygame.SRCALPHA, maxlen=400),
        }

        self.hue_ncols_exemple = 10
        self.hue_shift_exemple = 0



        self.steer = None
        self.throttle = None
        self.throttle_min = 0.05
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            self.steer = Joystick(joystick, 2)
            self.throttle = Joystick(joystick, 4, normalization=lambda x: (x+1)/2)

        self.particles = Particles(400)
        self.text_particles = Particles(350)
        self.particles_fonts = [
            pygame.font.SysFont('Times', 28),
            pygame.font.SysFont('Times', 34),
            pygame.font.SysFont('Times', 40),
        ]
        self.letters = [chr(i) for i in range(945, 970) if i != 962]  #choice(('0', '1')), #choice(tuple(chr(i) for i in range(97, 123))),

        self.loop()

    def left_release(self, button: MouseButton):
        pass

    def left_click(self, button: MouseButton):
        pos = self.mouse_world_pos


    def right_click(self, button: MouseButton):
        pass

    def right_release(self, button: MouseButton):
        pass

    def scroll_up(self, scroll: MouseScroll):
        if scroll.up_keys[pygame.K_LCTRL]:
            self.tabs[self.active_tab].scale /= 1.1

    def scroll_down(self, scroll: MouseScroll):
        if scroll.down_keys[pygame.K_LCTRL]:
            self.tabs[self.active_tab].scale *= 1.1

    def process_user_input_event(self, event):
        if self.mouse.right.dragging and self.mouse.right.drag_keys[pygame.K_LCTRL]:
            self.tabs[self.active_tab].bias = (int(self.tabs[self.active_tab].bias[0] + self.mouse.right.drag_delta[0]), int(self.tabs[self.active_tab].bias[1] + self.mouse.right.drag_delta[1]))
            self.mouse.right.clear_drag_delta()

        for scope in self.scopes.values():
            if self.mouse.left.dragging and scope.focus:
                canvas = self.tabs[self.active_tab]
                delta = canvas.screen_to_world_delta_v2(remap(self.mouse.left.drag_delta, self.window, canvas))
                # print(self.mouse.left.drag_delta, '->', remap(self.mouse.left.drag_delta, self.window, canvas), '->', canvas.screen_to_world_delta_v2(remap(self.mouse.left.drag_delta, self.window, canvas)))
                scope.pos = Vector2(scope.pos) + delta
                self.mouse.left.clear_drag_delta()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                pass
            elif event.key == pygame.K_RIGHT:
                pass
            elif event.key == pygame.K_UP:
                self.hue_ncols_exemple += 1
            elif event.key == pygame.K_DOWN:
                if self.hue_ncols_exemple > 2:
                    self.hue_ncols_exemple -= 1
            elif event.key == pygame.K_r:
                self.scopes['ch1'].clear()
                self.scopes['ch1'].rolling = not self.scopes['ch1'].rolling
            elif event.key == pygame.K_v:
                self.scopes['ch1'].visible = not self.scopes['ch1'].visible
            elif event.key == pygame.K_KP_MULTIPLY:
                self.scopes['ch1'].x_scale *= 2
            elif event.key == pygame.K_KP_DIVIDE:
                self.scopes['ch1'].x_scale /= 2

            elif event.key == pygame.K_t:
                self.scopes['ch2'].clear()
                self.scopes['ch2'].rolling = not self.scopes['ch2'].rolling
            elif event.key == pygame.K_b:
                self.scopes['ch2'].visible = not self.scopes['ch2'].visible
            elif event.key == pygame.K_KP_PLUS:
                self.scopes['ch2'].x_scale *= 2
            elif event.key == pygame.K_KP_MINUS:
                self.scopes['ch2'].x_scale /= 2

    def draw_main(self, canvas: Canvas):


        center = canvas.bias
        width = 1
        M = 10
        grid_color = (100, 100, 100)
        for m in range(4 * M + 1):
            canvas.draw_line(grid_color, (-2 + m / M, -1), (-2 + m / M, 1), width=width)
        for m in range(2 * M + 1):
            canvas.draw_line(grid_color, (-2, -1 + m / M), (2, -1 + m / M), width=width)

        radius = 0.1
        for n in range(11):
            canvas.draw_circle((180, 255, 180), (+0, +0), radius * n, width=1)
        canvas.draw_circle((255, 0, 0), (-1, -1), radius)
        canvas.draw_circle((0, 255, 0), (-1, +1), radius)
        canvas.draw_circle((0, 0, 255), (+1, +1), radius)
        canvas.draw_circle((255, 255, 0), (+1, -1), radius)

        self.hue_shift_exemple += 3 / 360
        d = .5
        r = radius
        cols_iter = ColorsDiscIterator(self.hue_ncols_exemple, self.hue_shift_exemple, 1.0, 0.9)
        for i, col in enumerate(cols_iter):
            ang = i * 2 * math.pi / len(cols_iter)
            canvas.draw_circle(col, (d * math.cos(ang), d * math.sin(ang)), r)

    def draw_menu(self, canvas):
        prtsc = self.tabs[self.last_active_tab].copy()
        prtsc.set_alpha(128)
        offset = (-canvas.get_world_rect()[2] / 2, canvas.get_world_rect()[3] / 2)
        canvas.blit(prtsc, offset)


    def rocket_got_focus_callback(self, canvas: Canvas):
        for key, scope in self.scopes.items():
            scope.clear()


    def draw_rocket(self, canvas):

        self.extra_info = [
        ]

        if self.steer is not None:
            self.steer.update()
            self.throttle.update()
            angle = self.steer.value * math.pi / 6
            throttle = max(self.throttle_min, self.throttle.value)
        else:
            angle = 0.0
            throttle = self.throttle_min

        if self.ticks % 2 == 0:
            for _ in range(int(11*60/self.fps)):
                self.text_particles.append(
                    TextParticle(canvas,
                                 color=lerp_vec3((90, 250, 90), (30, 90, 30), random()),
                                 text=choice(self.letters),
                                 font=choice(self.particles_fonts),
                                 pos=(uniform(-1.8, 1.8), 1.1),
                                 vel=(0, -2), dt=1/self.fps, g=0, lifetime=2,
                                 ))
        self.text_particles.step_and_draw()


        emmit_l = Vector2(-0.075, -0.04).rotate_rad(angle)
        emmit_r = Vector2(0.075, -0.04).rotate_rad(angle)

        # c, s = math.cos(angle), math.sin(angle)

        for _ in range(int(randint(round(15 * throttle), round(30 * throttle)) * 60/self.fps)):
            vel = Vector2(uniform(-0.07, .07), uniform(-1.9, -3.8))
            self.particles.append(BallParticle(canvas,
                                               lerp_vec3(lerp_vec3((255, 60, 0), (200, 200, 60), random()),(255, 255, 255), random() * 0.5),
                                               uniform(.003, .006),
                                               pos=lerp_vec2(emmit_l, emmit_r, random()),
                                               vel=vel.rotate_rad(angle),
                                               dt=1 / self.fps, lifetime=uniform(.2, .4), g=0))
        self.particles.step_and_draw()

        canvas.draw_polygon((90, 90, 100), rotate_vec2s(((0.06, 0.05), (0.08, -0.1), (-0.08, -0.1), (-0.06, 0.05)), angle))  # angle
        canvas.draw_polygon((120, 120, 130),
                            ((0.1, 0.0), (0.1, 0.6), (0.06, 0.75), (0.0, 0.8), (-0.06, 0.75), (-0.1, 0.6), (-0.1, 0.0)))

        canvas.draw_circle((255, 200, 60), (0, 0.25), 0.05, width=0, draw_top_left=True, draw_bottom_right=True)
        canvas.draw_circle((0, 0, 0), (0, 0.25), 0.05, width=0, draw_top_right=True, draw_bottom_left=True)

        # --Scope-----------------------------
        x = self.t
        y = {
            'ch1': 0.7 * math.sin(x * 5)+ uniform(-0.05, 0.05),
            'ch2': (throttle, angle),
        }

        any_on_focus = False

        def another_in_focus(self_key):
            for ikey, iscope in self.scopes.items():
                if ikey != self_key and iscope.focus:
                    return True
            return False

        for key, scope in self.scopes.items():


            # print(key, x, y[key])
            scope.append(x, y[key])

            scope.focus = scope.collision(self.mouse_world_pos) and not another_in_focus(key)
            scope.draw()
            scope.blit_to_main()



if __name__ == '__main__':
    Example(fps=60)