import math
import gamebase as gb
from gamebase.canvas import Canvas
from pygame import Vector2


class CollidableParticle():
    def __init__(self, pos: tuple[float, float], vel: tuple[float, float], dt, decay=1.0, collision_decay=0.7, lifetime=-1, alive=True, g=-9.81):
        self.x = pos[0]
        self.y = pos[1]
        self.vel_x = vel[0]
        self.vel_y = vel[1]
        self.g = g
        self.decay = decay
        self.collision_decay = collision_decay
        self.ticks = 0
        self.dt = dt
        self.lifetime = lifetime
        self.alive = alive

    @property
    def pos(self):
        return Vector2(self.x, self.y)

    @pos.setter
    def pos(self, point):
        self.x, self.y = point

    @property
    def vel(self):
        return Vector2(self.vel_x, self.vel_y)

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
        if self.ticks * self.dt > self.lifetime and self.lifetime > 0:
            self.alive = False


class BallCollidableParticle(CollidableParticle):
    def __init__(self, canvas: Canvas, color, radius, radius_in_pixels=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = color
        self.canvas = canvas
        self.radius = radius
        self.radius_in_pixels = radius_in_pixels

    def step(self, line):
        start = self.pos
        super().step()
        end = self.pos

        # l = (end-start).magnitude()
        # end = gb.lerp_vec2(start, end, 1+self.radius/l)
        #
        # inter = gb.find_lines_intersection(start, end, line[0], line[1])
        # if inter is not None:
        #     self.vel_y *= -self.collision_decay
        #     x, y = inter
        #     y += self.radius
        #     self.y = y
        #
        if gb.circle_line_collision(self.pos, self.radius, line[0], line[1]):
            self.vel_y *= -self.collision_decay
            x, y = gb.find_lines_intersection(start, self.pos, line[0], line[1], True)
            y += self.radius
            self.y = y


    def draw(self):
        if self.alive:
            self.canvas.draw_circle(self.color, (self.x, self.y), self.radius, self.radius_in_pixels)