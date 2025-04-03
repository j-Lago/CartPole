from screen import NormalizedScreen
from particles import BallParticle, Particles
from random import random, randint, uniform
from vec import Vec2, scale_vec2s, rotate_vec2s, translate_vec2s, scale_vec2, translate_vec2, rotate_vec2, lerp, lerp_vec2, lerp_vec3
import pygame
from inputs import Joystick, JOYBUTTON
import math

class Game(NormalizedScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.particles = Particles(20000)

        self.steer = None
        self.throttle_min = 0.05
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            self.steer = Joystick(joystick, 2)
            self.throttle = Joystick(joystick, 1)


        self.reset()
        self.loop()

    def reset(self):
        super().reset()

    def draw(self):
        if self.steer is not None:
            self.steer.update()
            self.throttle.update()
            angle = self.steer.value * math.pi / 6
            throttle = max(self.throttle_min, -self.throttle.value)
        else:
            angle = 0.0
            throttle = self.throttle_min




        scale = 0.8

        self.draw_polygon((90, 90, 100),
                          rotate_vec2s(scale_vec2s(((0.06, 0.05), (0.08, -0.1), (-0.08, -0.1), (-0.06, 0.05)), scale),
                                       angle)
                          )

        self.draw_polygon((120, 120, 130),
                          scale_vec2s(((0.1, 0.0), (0.1, 0.6), (0.06, 0.75), (0.0, 0.8), (-0.06, 0.75), (-0.1, 0.6),
                                       (-0.1, 0.0)), scale),
                          )

        self.draw_circle((255, 200, 60), (0, 0.25), 0.02, width=0, draw_top_left=True, draw_bottom_right=True)
        self.draw_circle((0, 0, 0), (0, 0.25), 0.02, width=0, draw_top_right=True, draw_bottom_left=True)

        # w = self.screen.get_width()
        # h = self.screen.get_height()

        emmit_l = rotate_vec2(scale_vec2((-0.08, -0.1), scale), angle)
        emmit_r = rotate_vec2(scale_vec2((0.08, -0.1), scale), angle)

        c, s = math.cos(angle), math.sin(angle)

        for _ in range(randint(round(20*throttle), round(40*throttle))):
            vel = uniform(-70, 70), uniform(-400, -800)
            self.particles.append(BallParticle(self,
                                               lerp_vec3(lerp_vec3((255, 60, 0), (200, 200, 60), random()), (255,255,255), random()*0.5), #(randint(0, 255), randint(0, 255), randint(0, 255)),
                                               randint(1, 2),
                                    pos = self.world_to_screen(lerp_vec2(emmit_l, emmit_r, random())),
                                    vel=rotate_vec2(vel, angle),
                                    dt=1 / self.fps, lifetime=uniform(.2, .6), g=0))
        self.particles.step_and_draw()












if __name__ == '__main__':
    Game('LevelControl', (1200, 900), 60, aspect_ratio=1)