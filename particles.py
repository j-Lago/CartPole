import math
import random
from random import random as rand, randint, uniform, choice
import pygame
from screen import NormalizedScreen
from _collections import deque
from vec import lerp_vec3



class Particle():
    def __init__(self, pos: tuple[float, float], vel: tuple[float, float], dt, decay=.999999, lifetime=-1, alive=True, g=-9.81):
        self.x = pos[0]
        self.y = pos[1]
        self.vel_x = vel[0]
        self.vel_y = vel[1]
        self.g = g
        self.decay = decay
        self.ticks = 0
        self.dt = dt
        self.lifetime = lifetime
        self.alive = alive

    @property
    def pos(self):
        return self.x, self.y

    @property
    def vel(self):
        return self.vel_x, self.vel_y

    @property
    def abs_vel(self):
        return math.sqrt(self.vel_x**2 + self.vel_y**2)

    @property
    def direction(self):
        return math.atan2(self.vel_y, self.vel_x)

    def step(self):
        if self.alive:
            self.x += self.vel_x * self.dt
            self.y += self.vel_y * self.dt

            self.vel_x = self.vel_x * self.decay
            self.vel_y = self.vel_y * self.decay + 0.5 * self.g * self.dt**2

        self.ticks += 1
        if self.ticks * self.dt > self.lifetime:
            self.alive = False


class BallParticle(Particle):
    def __init__(self, surface, color, radius, radius_in_pixels=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = color
        self.surface = surface
        self.radius = radius
        self.radius_in_pixels = radius_in_pixels

    def draw(self):
        if self.alive:
            self.surface.draw_circle(self.color, (self.x, self.y), self.radius, self.radius_in_pixels)


class TextParticle(Particle):
    def __init__(self, surface: NormalizedScreen, color, text, font, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = color
        self.surface = surface
        self.text = text
        self.font = font

    def draw(self):
        if self.alive:
            self.surface.blit(self.font.render(self.text, True, self.color), (self.x, self.y), rescale=True)



class Particles():
    def __init__(self, maxlen: int | None = None):
        self.particles = deque(maxlen=maxlen)

    def append(self, particle: Particle):
        self.particles.append(particle)

    def __len__(self):
        return len(self.particles)

    def step(self):
        for particle in self.particles:
            particle.step()

    def draw(self):
        for particle in self.particles:
            particle.draw()

    def step_and_draw(self):
        self.step()
        self.draw()

    def garbage_collect(self):
        self.particles = [x for x in self.particles if x.alive]


def example(spawn_every_n_ticks = (1,2), particles_per_spawn = (1,2), lifetime = (1,2), maxlen=None):
    class Game(NormalizedScreen):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.particles = Particles(maxlen)
            self.text_particles = Particles(500)
            self.particles_fonts = [pygame.font.SysFont('Times', 28),
                                    pygame.font.SysFont('Times', 34),
                                    pygame.font.SysFont('Times', 40),]
            self.letters = [chr(i) for i in range(945, 970) if i != 962]  #choice(('0', '1')), #choice(tuple(chr(i) for i in range(97, 123))),
            self.loop()

        def draw(self):
            w, h = self.width, self.height
            if self.ticks % spawn_every_n_ticks == 0:
                for _ in range(4):
                    self.text_particles.append(
                        TextParticle(self,
                                     color=lerp_vec3((90, 250, 90), (30, 90, 30), rand()),
                                     text=choice(self.letters),
                                     font=choice(self.particles_fonts),
                                     pos=(uniform(-1.8, 1.8), 1.1),
                                     vel=(0, -0.8), dt=1/self.fps, g=-98, lifetime=2
                                     ))
                for _ in range(randint(*particles_per_spawn)):
                    self.particles.append(
                        BallParticle(self,
                                     (randint(0, 255), randint(0, 255), randint(0, 255)),
                                     # randint(1,2), radius_in_pixels=True,
                                     randint(1, 2) / 600,
                                     pos=(uniform(-1.3, -1.25), uniform(-.95, -.9)), vel=(uniform(.4, .7), rand() * 0.05 + 1.5),
                                     dt=1 / self.fps, lifetime=lifetime, g=-98))
            self.extra_info = [f'ball_particles: {len(self.particles)}',
                               f'text_particles: {len(self.text_particles)}',
                               f'global_scale: {self.global_scale:.1f}']
            self.text_particles.step_and_draw()
            self.particles.step_and_draw()

    Game('particle test', (900, 600))


if __name__ == '__main__':
    example(spawn_every_n_ticks=1, particles_per_spawn=(10, 30), lifetime=5, maxlen=20000)