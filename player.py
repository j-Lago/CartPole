import dataclasses
import datetime

import gamebase as gb
import pygame
from pygame import Vector2
from cartpolemodel import CartPoleModel
import math
from pathlib import Path
from typing import Callable
from random import random, uniform, randint


class Cart:
    instance_count: int = 0

    assets_path = Path(__file__).parent / 'assets'
    jet_img = pygame.transform.smoothscale_by(pygame.image.load(assets_path / 'jet.png'), (0.35, 0.3))
    perturb_img = pygame.transform.smoothscale_by(pygame.image.load(assets_path / 'dedo.png'), 0.3)

    def __init__(self, name: str, game: gb.BaseScreen, input_device, pos: Vector2 = Vector2(0, 0), th0: float = 0,
                 base_color: tuple[int, int, int] = (180, 180, 180), rail_color: tuple[int, int, int] = (255, 255, 255), bg_color: tuple[int, int, int] = (30, 30, 30),
                 alive: bool = True, death_callback: Callable = None, max_force: float = 18):



        self.name = name
        self.game = game

        Cart.instance_count += 1
        self.id = Cart.instance_count
        self.collect_every_x_ticks = 10
        self.collect_shift = self.collect_every_x_ticks // 2 if (self.id % 2 == 0) else 0
        self.force_factor = max_force

        self.training_mode = False

        self.cart_on_target = False
        self.pole_on_target = False
        self.steps_with_pole_on_target = None
        self.steps_with_both_on_target = None
        self.score = None
        self.uncollected_score = None
        self.reward = None
        self.perturbation = None
        self.ticks_since_perturbation = None

        self.reward_pole_on_target_short = 1
        self.reward_pole_on_target_long = 2
        self.reward_cart_on_target_short = 2
        self.reward_cart_on_target_long = 6
        self.reward_on_death = -100
        self.reward_death_per_tick = -1

        self.time_pole_on_target_short = int(60 / (60 / self.fps)) if not self.training_mode else 0
        self.time_pole_on_target_long = int(60 * 3 / (60 / self.fps)) if not self.training_mode else 0
        self.time_cart_on_target_short = int(60 / (60 / self.fps)) if not self.training_mode else 0
        self.time_cart_on_target_long = int(60 * 3 / (60 / self.fps)) if not self.training_mode else 0

        self.death_callback = death_callback
        self.alive = alive
        self.canvas: gb.Canvas = self.game.canvas
        self.input = input_device
        self.fuel = 1.0
        self.fuel_consumption_rate = 0.00004
        self.x_target = (-0.15, 0.15)
        tol = math.pi / 12
        self.th_target = (math.pi - tol, math.pi + tol)

        if not isinstance(pos, Vector2):
            pos = Vector2(pos)

        self.initial_pos = pos
        self.linear_factor = 0.110625 * 0.8

        self.model = CartPoleModel(1., .3, 5., 1., 1., x0=self.initial_pos[0] / self.linear_factor, th0=th0, dt=1 / self.fps)

        self.base_color = base_color
        self.rail_col = rail_color
        self.bg_color = bg_color
        self.sleeper_col = (120, 100, 60)
        self.guardrail0_col = (60, 60, 60)
        self.guardrail1_col = (220, 200, 30)

        self.points = {
            'pole': ((0.015, 0), (0.015, -0.35), (-0.015, -0.35), (-0.015, 0))
        }

        self.base_rect = gb.Rect_f(0, 0, 0.35, 0.08)
        self.guardrail_rect = gb.Rect_f(0, 0, 0.09, 0.18)

        self.col1 = (255, 255, 0)
        self.col2 = (127, 180, 90)
        self.flag_col = (90, 200, 90)
        self.flag_pole_col = (60, 60, 60)

        self.spark_sigma = 1.0
        self.spark_mu = 0.0
        self.spark_density = 100
        self.spark_particle_size = 1, 2

        y = (self.canvas.ymax - 0.04) if self.id % 2 == 1 else (self.canvas.ymin+0.07)
        self.progress_fuel = gb.ProgressBar(
            self.canvas,
            (+1.72 - 0.7, y, 0.7, 0.04),
            0, 1, 1, .2,
            self.base_color, self.bg_color,
            border_width=2,
            border_radius=0,
            show_particles=True,
        )

        self.point_particles = None
        self.text_particles = None
        self.sliders = {
            'kp': gb.Slider(self.canvas, (pos[0]-.7, pos[1]+0.55, 0.1, 0.6), text='kp', font=self.game.fonts['small'],max_value=0.1, min_value=0.0, init_value=0.01),
            'ki': gb.Slider(self.canvas, (pos[0]-.55, pos[1]+0.55, 0.1, 0.6), text='ki', font=self.game.fonts['small'],max_value=.005, min_value=.0000001, init_value=.0005),
            'kd': gb.Slider(self.canvas, (pos[0]-.4, pos[1]+0.55, 0.1, 0.6), text='kd', font=self.game.fonts['small'],max_value=0.05, min_value=0.0, init_value=0.015),
        }

    def reset(self):
        self.cart_on_target = False
        self.pole_on_target = False
        self.steps_with_pole_on_target = 0
        self.steps_with_both_on_target = 0
        self.score = 0
        self.uncollected_score = 0
        self.reward = 0
        self.perturbation = 0
        self.fuel = 1.0
        self.ticks_since_perturbation = 0
        self.alive = True
        self.point_particles = gb.Particles(100)
        self.text_particles = gb.Particles(6)
        self.model.reset()

    def feedback(self):
        if self.alive:
            if isinstance(self.input, gb.Joystick):
                l = self.model.linear_acceleration / 30
                r = -self.model.linear_acceleration / 30

                self.input.source.rumble(l * .05, r, 100)

    def collect_score(self, max_collect: int = None):
        x = min(self.uncollected_score, max_collect) if max_collect is not None else self.uncollected_score
        self.uncollected_score -= x
        return x

    def perturb(self, intensity):
        self.perturbation = intensity
        self.ticks_since_perturbation = 0
        self.model.y[3][0] += intensity

    @property
    def ticks(self):
        return self.game.clock.ticks

    @property
    def fps(self):
        return self.game.clock.fps

    def step(self):
        force = self.input.value * self.force_factor if self.fuel > 0 else 0
        if self.alive:
            self.fuel -= self.fuel_consumption_rate * abs(force)
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
        f = 60 / self.game.clock.fps
        pole_col = self.base_color
        cart_col = gb.lerp_vec3(self.base_color, (0, 0, 0), 0.4)

        if not self.alive:
            pole_col = gb.lerp_vec3(pole_col, (0, 0, 0), 0.7)
            cart_col = gb.lerp_vec3(cart_col, (0, 0, 0), 0.7)

        # target test
        pole_on_target = False
        cart_on_target = False
        if self.alive and self.th_target[0] < self.theta < self.th_target[1]:
            pole_on_target = True
            if self.x_target[0] < self.x < self.x_target[1]:
                cart_on_target = True

        wheel_r = 0.055
        wheel_yaxis = self.base_rect[3] * 1.1
        wheel_xaxis = self.base_rect[2] / 2 * 0.6
        y = self.pos[1] - wheel_r - wheel_yaxis

        # flags
        flag_tops = []
        for x in (self.x_target[0] - self.base_rect.w / 2, self.x_target[1] + self.base_rect.w / 2):
            top = Vector2(x, y + 0.2)
            flag_tops.append(top)
            flag_points = (top - (0.0, 0.001), top - (-0.06, 0.019), top - (0.0, 0.037),)
            self.canvas.draw_polygon(self.flag_col, flag_points)
            self.canvas.draw_aalines(self.flag_col, False, flag_points)
            self.canvas.draw_line(self.flag_pole_col, (x, y), top, 5)
            self.canvas.draw_circle(self.flag_pole_col, top, 5 / self.canvas.scale)

        # flame
        if self.alive and self.fuel > 0:
            flame_gain = math.fabs(self.input.value) * uniform(0.8, 1.2)
            img0: pygame.Surface = pygame.transform.scale_by(self.jet_img, Vector2(flame_gain, max(flame_gain,
                                                                                                   0.8)) * self.canvas.relative_scale)
            if self.input.value < 0:
                img0 = pygame.transform.flip(img0, True, False)

            img = gb.Image(self.canvas, img0)
            flame_offset = self.base_rect[2] / 2 * 0.9, self.base_rect[3] / 2
            if self.input.value > 0:
                img.midright = self.pos - flame_offset
            else:
                img.midleft = self.pos + (flame_offset[0], -flame_offset[1])
            img.blit()

        cart_center = self.pos
        self.base_rect.midtop = cart_center

        pole_points = gb.RotateMatrix(self.theta) * self.points['pole']
        pole_points = tuple((cart_center[0] + p[0], cart_center[1] + p[1]) for p in pole_points)

        # cart
        self.canvas.draw_rect(cart_col, self.base_rect)
        self.canvas.draw_circle(cart_col, cart_center, 0.04)
        if cart_on_target:
            cart_points = self.base_rect.points
            for start, end in cart_points.pairs_iter():
                self.canvas.draw_line(color=self.col1, start_pos=start, end_pos=end)
                self.canvas.draw_circle(cart_col, cart_center, 0.04)
                self.canvas.draw_circle(self.col1, cart_center, 0.04, 1, draw_top_right=True, draw_top_left=True)
                self.canvas.draw_sparkly_line(start_pos=start, end_pos=end, width=10, density=self.spark_density,
                                              mu=self.spark_mu, sigma=self.spark_sigma,
                                              color1=self.col1, color2=self.col2,
                                              particle_size=self.spark_particle_size, both_sides=False)

        # wheels
        for m, wheel_center in enumerate(
                ((cart_center - (wheel_xaxis, wheel_yaxis)), (cart_center - (-wheel_xaxis, wheel_yaxis)))):
            self.canvas.draw_circle(pole_col, wheel_center, wheel_r, 10)
            self.canvas.draw_circle(pole_col, wheel_center, wheel_r * .3, 10)
            spoke = Vector2(0.0, wheel_r * .9)
            n_spokes = 5
            for n in range(n_spokes):
                ang = -self.x / wheel_r
                self.canvas.draw_line(pole_col, wheel_center,
                                      wheel_center + spoke.rotate_rad(n * 2 * math.pi / n_spokes + ang + m * 0.554), 6)
            self.canvas.draw_circle(cart_col, wheel_center, wheel_r * .15, 10)

        # rail
        rail_sleeper_rect = gb.Rect_f(0, 0, 0.03, 0.02)
        n_sleepers = 22
        mw = self.canvas.get_rect()[2] / (n_sleepers - 1)
        for i in range(n_sleepers):
            x = self.canvas.xmin + i * mw
            rail_sleeper_rect.midtop = (x, y)
            self.canvas.draw_rect(self.sleeper_col, rail_sleeper_rect)
        ground_width = 4
        self.canvas.draw_line(self.rail_col, (self.canvas.xmin, y), (self.canvas.xmax, y), ground_width)

        # for x in self.x_target:
        #     self.canvas.draw_line(col1, (x, y-0.03), (x, y-0.05), ground_width)

        # pole
        self.canvas.draw_circle(pole_col, cart_center, 0.02)
        if pole_on_target:
            self.canvas.draw_circle(self.col1, cart_center, 0.02, 1)
        self.canvas.draw_polygon(pole_col, pole_points)

        if pole_on_target:
            for start, end in zip(pole_points, pole_points[1:]):
                self.canvas.draw_aaline(color=self.col1, start_pos=start, end_pos=end)

        self.canvas.draw_circle(pole_col, cart_center, 0.0185)
        self.canvas.draw_circle(cart_col, cart_center, 0.01)
        if pole_on_target:
            for start, end in zip(pole_points, pole_points[1:]):
                self.canvas.draw_sparkly_line(start_pos=start, end_pos=end, width=10, density=self.spark_density,
                                              mu=self.spark_mu, sigma=self.spark_sigma, color1=self.col1,
                                              color2=self.col2, particle_size=self.spark_particle_size,
                                              both_sides=False)

        # guardrail
        g_rect = self.guardrail_rect
        fx = 2 / 3
        fy = 1 / 3

        g_rect.bottomleft = (self.canvas.xmin, y)
        ti_points = (g_rect.x, g_rect.y - g_rect.h), (g_rect.x, g_rect.y + fy * g_rect.h - g_rect.h), (
            g_rect.x + fx * g_rect.w, g_rect.y - g_rect.h)
        ts_points = (g_rect.x + g_rect.w, g_rect.y), (g_rect.x + g_rect.w, g_rect.y - fy * g_rect.h), (
            g_rect.x + g_rect.w - fx * g_rect.w, g_rect.y)
        tc_points = (g_rect.x, g_rect.y - g_rect.h + 1.75 * fy * g_rect.h), (
            g_rect.x, g_rect.y - g_rect.h + 2.75 * fy * g_rect.h), (
            g_rect.x + g_rect.w, g_rect.y - g_rect.h + 1.25 * fy * g_rect.h), (
            g_rect.x + g_rect.w, g_rect.y - g_rect.h + 0.25 * fy * g_rect.h)
        self.canvas.draw_polygon(self.guardrail0_col, g_rect.points)
        self.canvas.draw_polygon(self.guardrail1_col, ti_points)
        self.canvas.draw_polygon(self.guardrail1_col, ts_points)
        self.canvas.draw_polygon(self.guardrail1_col, tc_points)

        g_rect.bottomright = (self.canvas.xmax, y)
        ti_points = (g_rect.x, g_rect.y - g_rect.h), (g_rect.x, g_rect.y + fy * g_rect.h - g_rect.h), (
            g_rect.x + fx * g_rect.w, g_rect.y - g_rect.h)
        ts_points = (g_rect.x + g_rect.w, g_rect.y), (g_rect.x + g_rect.w, g_rect.y - fy * g_rect.h), (
            g_rect.x + g_rect.w - fx * g_rect.w, g_rect.y)
        tc_points = (g_rect.x, g_rect.y - g_rect.h + 1.75 * fy * g_rect.h), (
            g_rect.x, g_rect.y - g_rect.h + 2.75 * fy * g_rect.h), (
            g_rect.x + g_rect.w, g_rect.y - g_rect.h + 1.25 * fy * g_rect.h), (
            g_rect.x + g_rect.w, g_rect.y - g_rect.h + 0.25 * fy * g_rect.h)
        self.canvas.draw_polygon(self.guardrail0_col, g_rect.points)
        self.canvas.draw_polygon(self.guardrail1_col, ti_points)
        self.canvas.draw_polygon(self.guardrail1_col, ts_points)
        self.canvas.draw_polygon(self.guardrail1_col, tc_points)

        # if pole_on_target:
        #     pos = Vector2(pole_points[1]).lerp(pole_points[2], random())
        #     if (self.ticks + self.collect_shift) % self.collect_every_x_ticks == 0:
        #
        #         collect_amount = choice([10, 20, 50, 100, 200, 500])
        #
        #         if collect_amount >= 200:
        #             collect_color = self.game.cols['huge_collect']
        #         elif collect_amount >= 100:
        #             collect_color = self.game.cols['big_collect']
        #         elif collect_amount >= 50:
        #             collect_color = self.game.cols['small_collect']
        #         else:
        #             collect_color = self.game.cols['tiny_collect']
        #
        #         self.text_particles.append(
        #             TextParticle(self.canvas, collect_color, f'{collect_amount:+d}', self.game.fonts['reward'],
        #                          pos=pos, vel=(uniform(-0.2,0.2), uniform(0.4, 0.5)), dt=1/self.fps,
        #                          lifetime=2,
        #                          g=-98)
        #         )
        #         self.game.sounds['coin'].play()
        pole_tip = Vector2(pole_points[1]).lerp(pole_points[2], 0.5)

        uncollected_score = self.uncollected_score
        if self.alive and (self.ticks + self.collect_shift) % self.collect_every_x_ticks == 0 and uncollected_score > 0:
            collected = self.collect_score(max_collect=200)
            color = self.game.cols[
                'tiny_collect'] if collected <= f * self.collect_every_x_ticks * self.reward_pole_on_target_short \
                else self.game.cols[
                'small_collect'] if collected <= f * self.collect_every_x_ticks * self.reward_pole_on_target_long \
                else self.game.cols['big_collect'] if collected <= f * self.collect_every_x_ticks * (
                    self.reward_cart_on_target_short + self.reward_pole_on_target_long) \
                else self.game.cols['huge_collect']
            color = gb.lerp_vec3(color, (randint(5, 250), randint(5, 250), randint(5, 250)), uniform(0.1, 0.2))

            self.text_particles.append(
                gb.TextParticle(self.canvas,
                                color,
                                f'+{collected}',
                                self.game.fonts['reward'],
                                pos= Vector2(pole_points[1]) - (0.025, -0.03),
                                vel=(uniform(-0.3, 0.23), uniform(0.3, 0.5)),
                                dt=1 / self.game.clock.fps,
                                lifetime=uniform(0.5, 1.5),
                                g=-20,
                                )
            )
            self.game.sounds['coin'].play()

        if self.steps_with_both_on_target >= self.time_cart_on_target_long:
            for _ in range(randint(1, 5)):
                self.point_particles.append(
                    gb.BallParticle(self.canvas, (randint(0, 255), randint(0, 255), randint(0, 255)),
                                    uniform(1.1, 2.1) / self.canvas.scale,
                                    pos=flag_tops[0], vel=(uniform(-0.25, 0.25), uniform(0.4, .8)), dt=1 / self.fps,
                                    g=-98)
                )
                self.point_particles.append(
                    gb.BallParticle(self.canvas, (randint(0, 255), randint(0, 255), randint(0, 255)),
                                    uniform(1.1, 2.1) / self.canvas.scale,
                                    pos=flag_tops[1], vel=(uniform(-0.25, 0.25), uniform(0.4, .8)), dt=1 / self.fps,
                                    g=-98)
                )

        # particles
        self.text_particles.step_and_draw()
        self.point_particles.step_and_draw()

        # score
        self.pole_on_target = pole_on_target
        self.both_on_target = pole_on_target and cart_on_target

        self.steps_with_pole_on_target = self.steps_with_pole_on_target + 1 if self.pole_on_target else 0
        self.steps_with_both_on_target = self.steps_with_both_on_target + 1 if self.both_on_target else 0

        self.reward = 0
        if self.steps_with_pole_on_target > self.time_pole_on_target_short:
            self.reward += self.reward_pole_on_target_short if self.steps_with_pole_on_target < self.time_pole_on_target_long else self.reward_pole_on_target_long

        if self.steps_with_both_on_target > self.time_cart_on_target_short:
            self.reward += self.reward_cart_on_target_short if self.steps_with_both_on_target < self.time_cart_on_target_long else self.reward_cart_on_target_long
        # self.ticks += 1
        # else:
        #     self.reward = 0
            # self.ticks_since_death += 1

        self.reward = int(self.reward * 60 / self.game.clock.fps)
        self.score += self.reward
        self.uncollected_score += self.reward

        # draw score
        pad = 0.05
        pad2 = 0.06
        if self.id % 2 == 1:
            y_score = self.canvas.ymax - 0.04 - 0.04
            y_label = y_score - 0.2
            y_description = y_label - 0.06
            anchor = 'topright'
        else:
            y_score = self.canvas.ymin + 0.03
            y_label = y_score + 0.2 + 0.02
            y_description = y_label + 0.06
            anchor = 'bottomright'
        pos_score = self.canvas.xmax - pad, y_score
        pos_label = self.canvas.xmax - pad2, y_label
        pos_description = self.canvas.xmax - pad2, y_description
        self.canvas.draw_text(self.base_color, self.game.fonts['big'], f'{self.score}', pos_score, anchor)
        self.canvas.draw_text(self.base_color, self.game.fonts['medium'], self.name.upper() + ' SCORE', pos_label, anchor)
        self.canvas.draw_text(self.base_color, self.game.fonts['tiny'], self.input.description, pos_description, anchor)
        self.progress_fuel.update(self.fuel)


        #perturbtion
        if self.perturbation != 0:
            if self.alive:
                pole_down = not (math.pi / 2 < self.model.theta < 3 * math.pi / 2)
                direction = (pole_down ^ (self.perturbation > 0))
                w, h = 80, 50
                x, y = pole_tip
                if not direction:
                    x -= w / self.canvas.scale
                y -= h / self.canvas.scale / 2
                y += 0.09 if pole_down else 0.065
                dedo = pygame.transform.smoothscale(pygame.transform.flip(self.perturb_img, direction, False), (w, h))
                self.canvas.blit(dedo, (x,y))
            self.ticks_since_perturbation += 1
            if self.ticks_since_perturbation * 1 / self.fps > 0.2:
                self.perturbation = 0
                self.ticks_since_perturbation = 0

        if isinstance(self.input, gb.LinearController):
            for key, slider in self.sliders.items():
                slider.update(self.game)
                self.input.__dict__[key] = slider.value
                # print(f'{key}: {slider.value}')


@dataclasses.dataclass
class Score:
    value: int
    input_device: str
    date: datetime.date | None
    # player_name: str
